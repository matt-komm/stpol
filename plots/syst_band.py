#!/usr/bin/env python
"""
Uses the unfolding histograms to make a final plot with the systematic band.
"""
from rootpy.io import File
from os.path import join
from plots.common.utils import NestedDict
from SingleTopPolarization.Analysis.systematics import total_syst
from plots.common.hist_plots import plot_hists, plot_hists_dict, plot_data_mc_ratio
from plots.common.stack_plot import plot_hists_stacked
from plots.common.odict import OrderedDict
from plots.common.sample_style import Styling
from plots.common.legend import legend
from plots.common.utils import lumi_textbox
from plots.load_histos2 import load_theta_format, SystematicHistCollection
from plots.common.utils import reorder, PhysicsProcess
from SingleTopPolarization.Analysis import sample_types


import numpy, re, math, logging, copy

logger = logging.getLogger("syst_band")
import rootpy
rootpy.log.basic_config_colorized()
logger.setLevel(logging.INFO)

import ROOT
ROOT.gROOT.SetBatch(True)

def load_fit_results(fn):
    """
    Opens the fit results file and returns the per-sample scale factors.

    Args:
        fn: the file name with the fit results

    Returns:
        A dictionary with (sample_name, scale_factor) elements.
    """
    fi = open(fn)
    rates = {}
    for line in fi.readlines():
        line = line.strip()
        spl = line.split(",")
        spl = map(lambda x: x.strip(), spl)
        assert len(spl)==4

        spl = tuple(spl)
        typ, sample, sf, err = spl
        if not typ=="rate":
            continue
        rates[sample] = float(sf)
    return rates

class PlotDef:
    from plots.vars import varnames

    defaults = dict(
        log=False,
        qcd_sf=None,
        fit_sf=None,
        systematics=[],
        systematics_shapeonly=False,
        systematics_symmetric=True,
        x_label=r"%(var_name)s %(x_units)s",
        x_units='',
        y_units='',
        lumibox_format='%(channel)s channel'
    )

    def __init__(self, **kwargs):

        for k, v in self.defaults.items():
            setattr(self, k, v)

        #Set any keyword arguments as attributes to self
        for k, v in kwargs.items():
            setattr(self, k, v)

        #The default variable pretty name is taken externally
        if not hasattr(self, "var_name"):
            self.var_name = self.varnames[self.var]

        #The systematic inclusion list is a list of regex patterns to include
        if isinstance(self.systematics, basestring):
            self.systematics = [self.systematics]

    def get_x_label(self):
        return self.x_label % self.__dict__

    def get_lumibox_comments(self, **kwargs):
        kwargs.update(**self.__dict__)
        return self.lumibox_format % kwargs

    def __repr__(self):
        return self.__dict__

    def __str__(self):
        return str(self.__repr__())

    def update(self, **kwargs):
        self.__dict__.update(**kwargs)

    def copy(self, **kwargs):
        newd = copy.deepcopy(self.__dict__)
        newd.update(**kwargs)
        new = PlotDef(**newd)

        return new

styles = {
    'tchan': 'T_t',
    'ttjets': 'TTJets_FullLept',
    'wjets': 'WJets_inclusive',
    'diboson': 'WW',
    'twchan': 'T_tW',
    'schan': 'T_s',
    'qcd': 'QCD'
}

def data_mc_plot(inf, pd, lumi):
    hists = load_theta_format(inf, styles)


    for (variable, sample, systtype, systdir), hist in hists.items_flat():

        #Scale all MC samples except QCD to the luminosity
        if sample_types.is_mc(sample) and not sample=="qcd":
            hist.Scale(lumi)
        hist.SetTitle(sample)
        hist.SetName(sample)


    #Assuming we only have 1 variable
    hists = hists[pd.var]

    hists_nominal = hists.pop("nominal")[None]
    hists_nom_data = hists_nominal.pop('data')
    hists_nom_mc = hists_nominal.values()
    hists_syst = hists

    hists_nom_data.SetTitle('data')

    #A list of all the systematic up, down variation templates as 2-tuples
    all_systs = [
    ]

    all_systs = hists_syst.keys()
    systs_to_consider = []

    for syst in all_systs:
        for sm in pd.systematics:
            if re.match(sm, syst):
                systs_to_consider.append(syst)

    #The total nominal MC histogram
    nom = sum(hists_nom_mc)

    #Get all the variated up/down total templates

    #A list with all the up/down total templates
    all_systs = []

    sumsqs = []
    for syst in systs_to_consider:

        #A list with the up/down variated template for a particular systematic
        totupdown = []

        sumsq = []
        for systdir in ["up", "down"]:

            #Get all the templates corresponding to a systematic scenario and a variation
            _hists = hists_syst[syst][systdir]


            for k, h in _hists.items():

                """
                Consider only the shape variation of the systematic,
                hence the variated template is noprmalized to the corresponding
                unvariated template.
                """
                if pd.systematics_shapeonly:
                    h.Scale(hists_nominal[k].Integral() / h.Integral())

            #For the missing variated templates, use the nominal ones, but warn the user
            present = set(_hists.keys())
            all_mc = set(hists_nominal.keys())
            missing = list(all_mc.difference(present))
            for m in missing:
                logger.warning("Missing systematic template for %s:%s" % (syst, systdir))

            #Calculate the total variated template
            tot = sum(_hists.values()) + sum([hists_nominal[m] for m in missing])
            totupdown.append(tot)

            sumsq.append(
                math.sqrt(numpy.sum(numpy.power(numpy.array(list(nom.y())) - numpy.array(list(tot.y())), 2)))
            )
        logger.debug("Systematic %s: sumsq=%.2Eu, %.2Ed" % (syst, sumsq[0], sumsq[1]))
        sumsqs.append((syst, max(sumsq)))
        all_systs.append(
            (syst, tuple(totupdown))
        )

    sumsqs = sorted(sumsqs, key=lambda x: x[1], reverse=True)
    for syst, sumsq in sumsqs[0:4]:
        logger.info("Systematic %s, %.4f" % (syst, sumsq))

    #Calculate the total up/down variated templates by summing in quadrature
    syst_up, syst_down, syst_stat_up, syst_stat_down = total_syst(nom, all_systs,
        symmetric=pd.systematics_symmetric,
        consider_variated_stat_err=False
    )

    stacks_d = OrderedDict()
    stacks_d['mc'] = reorder(hists_nominal, PhysicsProcess.desired_plot_order_mc)
    stacks_d['data'] = [hists_nom_data]

    #Systematic style
    for s in [syst_stat_up, syst_stat_down]:
        s.SetFillStyle(0)
        s.SetLineWidth(2)
        s.SetMarkerSize(0)
        s.SetLineColor(ROOT.kGray+2)
        s.SetLineStyle('dashed')
        s.SetTitle("stat. + syst.")

    c = ROOT.TCanvas()
    p1 = ROOT.TPad("p1", "p1", 0, 0.3, 1, 1)
    p1.Draw()
    p1.SetTicks(1, 1);
    p1.SetGrid();
    p1.SetFillStyle(0);
    p1.cd()

    stacks = plot_hists_stacked(p1, stacks_d, x_label=pd.get_x_label(), max_bin_mult=1.5 if not pd.log else 100)
    p1.SetLogy(pd.log)

    syst_stat_up.Draw("SAME hist")
    syst_stat_down.Draw("SAME hist")

    ratio_pad, hratio = plot_data_mc_ratio(c, hists_nom_data, nom, syst_hists=(syst_stat_down, syst_stat_up), min_max=(-1, 1))

    p1.cd()
    leg = legend(
        stacks_d['data'] +
        list(reversed(stacks_d['mc'])) +
        [syst_stat_up],
        legend_pos='top-right'
    )
    lb = lumi_textbox(lumi,
        line2=pd.get_lumibox_comments(channel="Muon"),
        pos='top-left'
    )
    c.children = [p1, ratio_pad, stacks, leg, lb]

    return c
if __name__=="__main__":
    from plots.common.tdrstyle import tdrstyle
    tdrstyle()

    inf = "hists_out_merged.root"
    channel = "mu"

    lumi=19800


    pd = PlotDef(
        var='abs_eta_lj',
        leg_pos='top-right',
        systematics='.*',
        log=True,
        systematics_shapeonly=False
    )
    pd2 = pd.copy(
        log=True,
        systematics='en',
        systematics_shapeonly=False
    )

    c1 = data_mc_plot(inf, pd, lumi)
    c2 = data_mc_plot(inf, pd2, lumi)
