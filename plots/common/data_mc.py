import logging,re
logger = logging.getLogger("data_mc")
import ROOT
import numpy

from plots.common.cuts import Cuts, Weights, Cut, Weight
from plots.common.sample_style import Styling
from plots.common.plot_defs import *
from plots.common.utils import PhysicsProcess, merge_hists, lumi_textbox, get_stack_total_hist
from plots.common.histogram import calc_int_err
from plots.common.legend import legend
from plots.common.odict import OrderedDict
from plots.common.stack_plot import plot_hists_stacked
from plots.common.hist_plots import plot_data_mc_ratio


def rescale_to_fit(sample_name, hist, fitpars, ignore_missing=True):
    """
    Rescales the histogram from a sample by the corresponding scale factors.
    Raises a KeyError when there was no match.

    sample_name - the name of the sample, corresponding to the patterns in fitpars
    hist - the Hist to be scaled
    fitpars - a list with tuple contents
        [
            ([patA1, patA2, ...], sfA),
            ([patB1, patB2, ...], sfB),
        ]

    returns - nothing
    """
    for patterns, sf in fitpars:
        for pat in patterns:
            if re.match(pat, sample_name):
                logger.debug("Rescaling sample %s to lepton_channeless %s, sf=%.2f" % (sample_name, pat, sf))
                hist.Scale(sf)
                #We take the first match
                return
    #If we loop through and get here, there was no match
    if not ignore_missing:
        raise KeyError("Couldn't match sample %s to fit parameters!" % sample_name)

def data_mc_plot(samples, plot_def, name, lepton_channel, lumi, weight, physics_processes):

    logger.info('Plot in progress %s' % name)

    merge_cmds = PhysicsProcess.get_merge_dict(physics_processes) #The actual merge dictionary

    var = plot_def['var']

    #Id var is a list/tuple, assume
    if not isinstance(var, basestring):
        if lepton_channel == 'ele':
            var = var[0]
        else:
            var = var[1]

    cut = None
    if lepton_channel == 'ele':
        cut = plot_def['elecut']
    elif lepton_channel == 'mu':
        cut = plot_def['mucut']

    cut_str = str(cut)

    plot_range = plot_def['range']

    do_norm = False
    if 'normalize' in plot_def.keys() and plot_def['normalize']:
        do_norm = True
    hists_mc = dict()
    hists_data = dict()
    for name, sample in samples.items():
        logger.debug("Starting to plot %s" % name)
        if sample.isMC:
            hist = sample.drawHistogram(var, cut_str, weight=str(weight), plot_range=plot_range)
            hist.Scale(sample.lumiScaleFactor(lumi))
            hists_mc[sample.name] = hist
            if do_norm:
                Styling.mc_style_nostack(hists_mc[sample.name], sample.name)
            else:
                Styling.mc_style(hists_mc[sample.name], sample.name)

            if "fitpars" in plot_def.keys():
                rescale_to_fit(sample.name, hist, plot_def["fitpars"][lepton_channel])
        elif "antiiso" in name and plot_def['estQcd']:

            #FIXME: it'd be nice to move the isolation cut to plots/common/cuts.py for generality :) -JP
            cv='mu_iso'
            lb=0.2
            if lepton_channel == 'ele':
                cv='el_iso'
                lb=0.1
            qcd_extra_cut = Cuts.deltaR(0.3)*Cut(cv+'>'+str(lb)+' & '+cv+'<0.5')

            # Make loose template
            region = '2j1t'
            if '2j0t' in plot_def['estQcd']: region='2j0t'
            if '3j0t' in plot_def['estQcd']: region='3j0t'
            if '3j1t' in plot_def['estQcd']: region='3j1t'
            if '3j2t' in plot_def['estQcd']: region='3j2t'
            qcd_loose_cut = cutlist[region]*cutlist['presel_'+lepton_channel]*qcd_extra_cut
            qcd_cut = cut*qcd_extra_cut

            hist_qcd_loose = sample.drawHistogram(var, str(qcd_loose_cut), weight="1.0", plot_range=plot_range)
            hist_qcd = sample.drawHistogram(var, str(qcd_cut), weight="1.0", plot_range=plot_range)
            logger.debug("Using the QCD scale factor %s: %.2f" % (plot_def['estQcd'], qcdScale[lepton_channel][plot_def['estQcd']]))
            hist_qcd.Scale(qcdScale[lepton_channel][plot_def['estQcd']])
            hist_qcd_loose.Scale(hist_qcd.Integral()/hist_qcd_loose.Integral())
            hist_qcd=hist_qcd_loose
            sampn = "QCD"+sample.name

            #Rescale the QCD histogram to the eta_lj fit
            if "fitpars" in plot_def.keys():
                rescale_to_fit(sampn, hist_qcd, plot_def["fitpars"][lepton_channel])

            hists_mc[sampn] = hist_qcd
            hists_mc[sampn].SetTitle('QCD')
            if do_norm:
                Styling.mc_style_nostack(hists_mc[sampn], 'QCD')
            else:
                Styling.mc_style(hists_mc[sampn], 'QCD')

        #Real ordinary data in the isolated region
        elif not "antiiso" in name:
            hist_data = sample.drawHistogram(var, cut_str, weight="1.0", plot_range=plot_range)
            hist_data.SetTitle('Data')
            Styling.data_style(hist_data)
            hists_data[name] = hist_data


    if len(hists_data.values())==0:
        raise Exception("Couldn't draw the data histogram")

    #Combine the subsamples to physical processes
    hist_data = sum(hists_data.values())
    merge_cmds['QCD']=["QCD"+merge_cmds['data'][0]]
    order=['QCD']+PhysicsProcess.desired_plot_order
    if plot_def['log']:
        order = PhysicsProcess.desired_plot_order_log+['QCD']
    merged_hists = merge_hists(hists_mc, merge_cmds, order=order)

    if hist_data.Integral()<=0:
        raise Exception("Histogram for data was empty. Something went wrong, please check.")

    if do_norm:
        for k,v in merged_hists.items():
            v.Scale(1./v.Integral())
        hist_data.Scale(1./hist_data.Integral())

    htot = sum(merged_hists.values())

    chi2 = hist_data.Chi2Test(htot, "UW CHI2/NDF")
    if chi2>20:#FIXME: uglyness
        logger.error("The chi2 between data and MC is large (%s, chi2=%.2f). You may have errors with your samples!" %
            (name, chi2)
        )
        logger.info("MC  : %s" % " ".join(map(lambda x: "%.1f" % x, list(htot.y()))))
        logger.info("DATA: %s" % " ".join(map(lambda x: "%.1f" % x, list(hist_data.y()))))
        logger.info("diff: %s" % str(
            " ".join(map(lambda x: "%.1f" % x, numpy.abs(numpy.array(list(htot.y())) - numpy.array(list(hist_data.y())))))
        ))

    merged_hists_l = merged_hists.values()

    PhysicsProcess.name_histograms(physics_processes, merged_hists)

    leg_style = ['p','f']
    if do_norm:
        leg_style=['p','l']
    leg = legend([hist_data] + list(reversed(merged_hists_l)), legend_pos=plot_def['labloc'], styles=leg_style)

    canv = ROOT.TCanvas()

    #Make the stacks
    stacks_d = OrderedDict()
    stacks_d["mc"] = merged_hists_l
    stacks_d["data"] = [hist_data]

    #label
    xlab = plot_def['xlab']
    if not isinstance(xlab, basestring):
        if lepton_channel == 'ele':
            xlab = xlab[0]
        else:
            xlab = xlab[1]
    ylab = 'N / '+str((1.*(plot_range[2]-plot_range[1])/plot_range[0]))
    if plot_def['gev']:
        ylab+=' GeV'
    fact = 1.5
    if plot_def['log']:
        fact = 10

    plow=0.3
    if do_norm:
        plow=0

    #Make a separate pad for the stack plot
    p1 = ROOT.TPad("p1", "p1", 0, plow, 1, 1)
    p1.Draw()
    p1.SetTicks(1, 1);
    p1.SetGrid();
    p1.SetFillStyle(0);
    p1.cd()

    stacks = plot_hists_stacked(p1, stacks_d, x_label=xlab, y_label=ylab, max_bin_mult = fact, do_log_y = plot_def['log'], stack = (not do_norm))

    #Put the the lumi box where the legend is not
    boxloc = 'top-right'
    if plot_def['labloc'] == 'top-right':
        boxloc = 'top-left'
    chan = 'Electron'
    if lepton_channel == "mu":
        chan = 'Muon'

    additional_comments = ""
    if 'cutname' in plot_def.keys():
        additional_comments += ", " + plot_def['cutname']['lepton_channel']
    lbox = lumi_textbox(lumi,
        boxloc,
        'preliminary',
        chan + ' channel' + additional_comments
    )

    #Draw everything
    lbox.Draw()
    leg.Draw()
    canv.Draw()

    #Draw the ratio plot with
    if not do_norm:
        ratio_pad, hratio, hline = plot_data_mc_ratio(canv, get_stack_total_hist(stacks["mc"]), hist_data)
        canv.PAD2 = ratio_pad
        canv.HRATIO = hratio
        canv.HLINE = hline

    canv.PAD1 = p1
    canv.STACKS = stacks
    canv.LEGEND = legend
    canv.LUMIBOX = lbox

    return canv, merged_hists, htot, hist_data
