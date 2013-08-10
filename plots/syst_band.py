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
import numpy

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

def reorder(src, dest, reverse=False):
    """
    Reorders objects in the src dictionary according to the dest order list.

    Args:
        src: the source dictionary
        dest: a list with the desired order of the keys.

    Keywords:
        reverse: return the output in the reversed order.

    Returns:
        a list with the objects in the desired order.
    """
    ret = []
    if reverse:
        dest = list(reversed(dest))
    for i in dest[::-1]:
        ret.append(src[i])
    return ret

if __name__=="__main__":
    from plots.common.tdrstyle import tdrstyle
    tdrstyle()

    inf = "final_fit/histos/ele__mva_BDT_with_top_mass_C_eta_lj_el_pt_mt_el_pt_bj_mass_bj_met_mass_lj_met30.root"
    files = {
        "mu": "mu__cos_theta__mva_0_06",
        "ele": "ele__cos_theta__mva_0_13"
    }
    lumi = 18600
    channel_pretty = {
        "mu": "Muon",
        "ele": "Electron",
    }
    mva_cut = {
        "mu": 0.06,
        "ele": 0.13
    }

    dfit_results = dict()

    suffix = 'top_plus_qcd'
    dfit_results['top_plus_qcd'] = {
        "mu": "mu__mva_BDT_with_top_mass_eta_lj_C_mu_pt_mt_mu_met_mass_bj_pt_bj_mass_lj__top_plus_qcd",
        "ele": "ele__mva_BDT_with_top_mass_C_eta_lj_el_pt_mt_el_pt_bj_mass_bj_met_mass_lj__top_plus_qcd"
    }

    dfit_results['default'] = {
        "mu": "mu__mva_BDT_with_top_mass_eta_lj_C_mu_pt_mt_mu_met_mass_bj_pt_bj_mass_lj",
        "ele": "ele__mva_BDT_with_top_mass_C_eta_lj_el_pt_mt_el_pt_bj_mass_bj_met_mass_lj"
    }
    fit_results = dfit_results[suffix]


    styles = {'tchan': 'T_t', 'other': 'TTJets_FullLept', 'wzjets': 'WJets_inclusive'}
    for channel in ['mu', 'ele']:
        hists = NestedDict()
        fi = File(inf)
        rate_sfs = load_fit_results("final_fit/results/%s.txt" % fit_results[channel])
        for root, dirs, items in fi.walk():
            for it in items:
                k = join(root, it)
                spl = k.split("__")
                if len(spl)==2:
                    variable, sample = spl
                    syst = "nominal"
                    systdir = "none"
                elif len(spl)==4:
                    variable, sample, syst, systdir = spl

                it = fi.get(k)
                if not isinstance(it, ROOT.TH1F):
                    continue

                if sample!= "DATA":
                    Styling.mc_style(it, styles[sample])
                else:
                    Styling.data_style(it)
                #if sample in rate_sfs.keys():
                #    it.Scale(rate_sfs[sample])
                hists[variable][syst][systdir][sample]= it

        hists = hists.as_dict()

        hists = hists.values()[0]
        hists_nominal = hists.pop("nominal")['none']
        hists_nom_data = hists_nominal.pop('DATA')
        hists_nom_mc = hists_nominal.values()
        hists_syst = hists

        tots = [
        ]

        systs_to_consider = hists_syst.keys()
        systs_to_remove = ['iso']

        for sr in systs_to_remove:
            systs_to_consider.pop(systs_to_consider.index(sr))

        nom = sum(hists_nom_mc)

        doScale = True

        for syst in systs_to_consider:
            totupdown = []
            print syst
            for systdir in ["up", "down"]:
                _hists = hists_syst[syst][systdir]
                for k, h in _hists.items():
                    if doScale:
                        h.Scale(hists_nominal[k].Integral() / h.Integral())
                #print syst, systdir, hists_syst[syst][systdir]
                present = set(_hists.keys())
                all_mc = set(hists_nominal.keys())
                missing = list(all_mc.difference(present))
                tot = sum(_hists.values()) + sum([hists_nominal[m] for m in missing])
                totupdown.append(tot)
                diff = numpy.array(list(nom.y())) - numpy.array(list(tot.y()))
                print "sum abs diff=", numpy.sum(numpy.abs(diff))

            tots.append(
                (syst, tuple(totupdown))
            )


        syst_up, syst_down = total_syst(nom, tots)


        h = OrderedDict()
        h['data'] = hists_nom_data
        h['nominal'] = nom
        h['up'] = syst_up
        h['down'] = syst_down

        stacks_d = OrderedDict()
        stacks_d['mc'] = reorder(hists_nominal, ["tchan", "other", "wzjets"])
        stacks_d['data'] = [hists_nom_data]

        for s in [syst_up, syst_down]:
            s.SetFillStyle(0)
            s.SetLineWidth(3)
            s.SetLineColor(ROOT.kGray+1)
            s.SetLineStyle('dashed')
            s.SetTitle("syst.")

        hists_nom_data.SetTitle('data')
        hists_nominal['tchan'].SetTitle("signal (t-channel)")
        hists_nominal['other'].SetTitle("t#bar{t}, tW, s, QCD")
        hists_nominal['wzjets'].SetTitle("W, diboson, DY-jets")
        #hists_nominal['qcd'].SetTitle("QCD")

        c = ROOT.TCanvas()
        p1 = ROOT.TPad("p1", "p1", 0, 0.3, 1, 1)
        p1.Draw()
        p1.SetTicks(1, 1);
        p1.SetGrid();
        p1.SetFillStyle(0);
        p1.cd()

        stacks = plot_hists_stacked(p1, stacks_d, x_label="BDT", max_bin_mult=100)
        p1.SetLogy()

        syst_up.Draw("SAME hist")
        syst_down.Draw("SAME hist")

        ratio_pad, hratio = plot_data_mc_ratio(c, hists_nom_data, nom, syst_hists=(syst_up, syst_down), min_max=(-0.5, 0.5))

        p1.cd()
        leg = legend(stacks_d['data']+list(reversed(stacks_d['mc']))+[syst_up], legend_pos='top-left')
        lb = lumi_textbox(lumi,
            line2="%s channel, BDT>%.2f, sf applied" % (channel_pretty[channel], mva_cut[channel]), pos='top-right')
        c.SaveAs("out/plots/cos_theta_%s_%s.png" % (channel, suffix))
        c.Close()
        print "Systs:", systs_to_consider
    #canv = plot_hists_dict(h)
