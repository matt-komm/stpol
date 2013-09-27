#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Plots the distribution from the pseudo-experiments drawn by theta.
"""

import ROOT
ROOT.gROOT.SetBatch(True)
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("pseodoexp")
from rootpy.plotting import Hist
import numpy as np
from plots.common.hist_plots import plot_hists
from plots.common.output import OutputFolder
from plots.common.metainfo import PlotMetaInfo
from plots.common.legend import legend
from plots.common.histogram import calc_int_err
from plots.common.utils import lumi_textbox
from plots.common.sample import Sample
from plots.common.cuts import Cuts
from plots.common.cross_sections import lumis
import argparse

def find_bin_idx(binning, val):
    """
    Finds the 1-based index of the Hist which contains the value,
    scanning from the left.

    Args:
        binning: a list of the bin lower edges
        val: the value to find_bin_idx

    Returns:
        The one-based index
    """
    for b, i in zip(binning, range(len(binning))):
        if b>val:
            return i+1

def get_binning(hi):
    """
    Returns the lower ends of the bins of a histogram,
    with the addition of the upper end of the last bin.

    Args:
        hi: a Hist instance
    Returns:
        a list with length nbins+1 of the lower edges plus
        the top edge.
    """
    return [hi.GetBinLowEdge(i) for i in range(1, hi.GetNbinsX()+2)]

def get_bin_widths(hi):
    """
    Returns the bin widths of a Hist.

    Args:
        hi: a Hist instance

    Returns:
        a list with length nbins containing the bin widths.
    """

    return [hi.GetBinWidth(i) for i in range(1, hi.GetNbinsX()+1)]

def post_normalize(hist):
    """
    Rescales the bin heights of a variably-binned histogram
    according to the bin width. Errors are scaled as well.
    A new Hist instance is created.

    Args:
        hist: a Hist instance to be rescaled.

    Returns:
        A new Hist instance after rescaling.
    """
    hn = hist.Clone()
    for i in range(1, hn.nbins()+1):
        hn.SetBinContent(i, hn.GetBinContent(i) / hn.GetBinWidth(i))
        hn.SetBinError(i, hn.GetBinError(i) / hn.GetBinWidth(i))
        if hn.GetBinContent(i)<0:
            hn.SetBinContent(i, 0)
    return hn

def asymmetry(hist, center):
    """
    Calculates the asymmetry around a central bin according to
    A = (N(x>=c) - N(x<c)) / (N(x>=c) + N(x<c)).

    Args:
        hist: a Hist instance
        center: a 1-based index with the central bin, around
            which to calculate the asymmetry.

    Returns:
        A numberical value of the
    """
    def my_int(a, b):
        I = sum([hist.GetBinContent(i) for i in range(a, b)])
        return I

    #An even number of bins which are equidistant
    if hist.nbins()%2 == 0 and np.std(list(hist.xwidth()))<0.001:
        if hist.nbins()/2+1 != center:
            raise ValueError("Wrong central bin provided: %d, %d" % (center, hist.nbins()))
    low = my_int(1, center)
    high = my_int(center, hist.nbins()+1)
    if (low+high - hist.Integral())>0.01:
        raise Exception("Low and high parts don't sum to the integral: %.2f + %.2f != %.2f" % (low, high, hist.Integral()))
    asy = (high-low)/(low+high)
    return asy


from plots.fit_scale_factors import fitpars_process
fitpars = {}
fitpars['mu'] = fitpars_process['final_2j1t_mva']['mu'][0][1]
fitpars['ele'] = fitpars_process['final_2j1t_mva']['ele'][0][1]

measured_asym_errs = dict()
measured_asym_errs['mu'] = (0.07, 0.15)
measured_asym_errs['ele'] = (0.11, 0.23)

if __name__=="__main__":
    from plots.common.tdrstyle import tdrstyle
    tdrstyle()

    #THhe name of the pseudoexperiment TH1D
    brname = "tunfold"

    parser = argparse.ArgumentParser(
        description='Plots the pseudoexperiment distribution'
    )
    parser.add_argument("infileMC",
        default=None, type=str,
        help="The MC input file with pseudoexp."
    )
    parser.add_argument("infileD",
        default=None, type=str,
        help="THe input file with the unfolded data."
    )
    parser.add_argument("--channel",
        default=None, type=str, required=True,
        help="The input channel"
    )
    args = parser.parse_args()
    lep = args.channel
    channels = {
        "mu": "Muon channel",
        "ele": "Electron channel",
    }
    channel = channels[lep]

    ROOT.TH1F.AddDirectory(False)
    def get_posterior(fn):
        logger.info("Loading pseudoexperiments from file %s" % fn)
        fi = ROOT.TFile(fn)
        fi.ls()
        t = fi.Get("unfolded")
        print "Tree:", t

        #Make a histogram with a nonspecific binning just to have a memory address
        hi = ROOT.TH1D()
        #ROOT wants a pointer, use AddressOf
        t.SetBranchAddress(brname, ROOT.AddressOf(hi))
        #Initialize the histogram
        t.GetEntry(0)

        #Now we can have a proper histogram with the right bins
        binning = get_binning(hi)
        hi = Hist(binning, type='D')
        t.SetBranchAddress(brname, ROOT.AddressOf(hi))

        #The last element in the binning is not the low edge, but the top edge,
        #which is needed to create the histogram
        nbins = len(binning)-1
        nentries = t.GetEntries()

        #Create a vector for the bin contents. Rows - histos, cols - bins
        bins = np.empty((nentries, nbins), dtype='f')
        i=0

        #The asymmetry distribution
        hasym = Hist(100, -2, 2, title='posterior PE')

        #Find the bin index where costheta=0 (center)
        center = find_bin_idx(list(hi.x()), 0)

        logger.info("Central bin index = %d" % center)

        #Fill the bin contents vector and the asymmetry histogram by looping over the events
        for ev in t:
            bins[i] = np.array(list(hi.y()), dtype='f')
            i += 1
            #print asymmetry(hi, center), list(hi.y())
            hasym.Fill(asymmetry(hi, center))
        logger.info("Looped over %d entries" % i)

        #The distribution of the unfolded costheta
        posterior = Hist(get_binning(hi), type='D', title='PE')
        logger.debug("Posterior binning A = %s" % (str(get_binning(posterior))))

        #Fill the posterior histogram
        for i in range(nbins):
            posterior.SetBinContent(i+1, np.mean(bins[:,i]))
            if nentries>1:
                posterior.SetBinError(i+1, np.std(bins[:,i]))
            #In case of only 1 unfolded histo (data), take the stat. error.
            #This is not used at the moment
            else:
                posterior.SetBinError(i+1, hi.GetBinError(i))

        logger.debug("Posterior binning B = %s" % (str(get_binning(posterior))))
        return posterior, hasym, binning

    def get_posterior_method2(fn):
        fi = ROOT.TFile(fn)
        ROOT.gROOT.cd()
        posterior = fi.Get("unfolded").Clone()
        try:
            hasym = fi.Get("asymmetry").Clone()
        except:
            hasym = None
        binning = get_binning(posterior)
        return posterior, hasym, binning

    def rebin(hi, binning):

        n = 1
        hnew = Hist(binning, name=hi.name, title=hi.title)
        for i in range(hi.nbins()):
            hnew[i] = hi[i]
            hnew.SetBinError(i+1, hi.GetBinError(i+1))
        return hnew


    #Take the lumis from a central database
    lumi = lumis["343e0a9_Aug22"]["iso"][lep]

    pe_post, pe_asym, binning = get_posterior_method2(args.infileMC)
    data_post, data_asym, binning = get_posterior_method2(args.infileD)
    data_post.__class__ = Hist
    data_post._post_init()

    #data_asym.__class__ = Hist
    #data_asym._post_init()

    binning = np.linspace(-1, 1, len(binning))
    logger.info(str(binning))

    data_post.SetTitle("unfolded data")
    #data_asym.SetTitle("unfolded data")

    data_post = rebin(data_post, binning)
    # disabled since now the unfolded distribution already has an error
    # # Make the ansatz that the pseudo-experiment distribution
    # # describes the distribution of the unfolding result, that is
    # # that we can take the PE error as the final error on the unfolding.
    # for i in range(1, data_post.nbins()+1):
    #     data_post.SetBinError(i, pe_post.GetBinError(i))

    # Get the true distribution at generator level,
    # requiring the presence of a lepton with the
    # correct gen flavour
    htrue = None
    datadir = "data/37acf5_343e0a9_Aug22"
    def gen_hist(sample):
        hi = sample.drawHistogram("true_cos_theta", str(Cuts.true_lepton(lep)), binning=list(binning))
        hi.Scale(s.lumiScaleFactor(lumi))
        return hi

    for fn in ["T_t_ToLeptons", "Tbar_t_ToLeptons"]:
        #s = Sample.fromFile("data/Step3_Jul26/%s/mc/iso/nominal/Jul15/%s.root" % (lep, fn))
        s = Sample.fromFile("data/37acf5_343e0a9_Aug22/%s.root" % (fn))
        hi = gen_hist(s)
        if htrue:
            htrue += hi
        else:
            htrue = hi
    htrue.SetTitle("generated (POWHEG)")
    #Scale to the final fit
    htrue.Scale(fitpars[lep])

    hcomphep = None
    for fn in ["TToBENu_t-channel", "TToBMuNu_t-channel", "TToBTauNu_t-channel"]:
        s = Sample.fromFile(datadir  + "/{0}/{1}.root".format(lep, fn))
        hi = gen_hist(s)
        if hcomphep:
            hcomphep += hi
        else:
            hcomphep = hi
    hcomphep.Scale(fitpars[lep])
    hcomphep.SetTitle("generated (CompHEP)")

    logger.info("Data={0:.0f}, powheg={1:.0f}, comphep={0:.0f}".format(data_post.Integral(), htrue.Integral(), hcomphep.Integral()))
    #Normalize to same area
    #htrue.Scale(data_post.Integral() / htrue.Integral())
    measured_asym = asymmetry(data_post, len(binning)/2 + 1)


    #####################
    # Plot the unfolded #
    #####################
    from plots.common.sample_style import Styling
    #Styling.mc_style(pe_post, 'T_t')
    Styling.mc_style(htrue, 'T_t')
    htrue.SetLineColor(ROOT.kGreen)
    htrue.SetFillColor(ROOT.kGreen)
    htrue.SetMarkerSize(0)

    Styling.mc_style(hcomphep, 'T_t')
    hcomphep.SetLineColor(ROOT.kRed)
    hcomphep.SetFillColor(ROOT.kRed)
    hcomphep.SetFillStyle('/')
    hcomphep.SetLineStyle('dashed')
    hcomphep.SetMarkerSize(0)

    Styling.data_style(data_post)

    hi = [data_post, htrue, hcomphep]
    chi2 = data_post.Chi2Test(htrue, "WW CHI2/NDF")
    #htrue.SetTitle(htrue.GetTitle() + " #chi^{2}/#nu = %.1f" % chi2)
    #hi_norm = hi
    hi_norm = map(post_normalize, hi)
    for h in hi[1:]:
        h.SetMarkerSize(0)
    of = OutputFolder(subdir='unfolding/%s' % lep)
    canv = plot_hists(hi_norm, x_label="cos #theta*", draw_cmd=len(hi)*["E1"], y_label="a.u.")
    #leg = legend(hi, styles=['p', 'f'], legend_pos='bottom-right', nudge_x=-0.29, nudge_y=-0.08)
    leg = legend(hi, styles=['p', 'f'], legend_pos='top-left', nudge_y=-0.14)
    lb = lumi_textbox(lumi,
        pos='top-center',
        line2="#scale[1.5]{A = %.2f #pm %.2f (stat.) #pm %.2f (syst.)}" % (
            measured_asym, measured_asym_errs[lep][0],  measured_asym_errs[lep][1]
        ), nudge_y=0.03
    )
    pmi = PlotMetaInfo(
        'costheta_unfolded',
        '2j1t_mva_loose {0}'.format(channel),
        'weighted to lumi={0}, sf(tchan)={1}'.format(lumi, fitpars[lep]),
        [args.infileMC, args.infileD]
    )

    of.savePlot(canv, pmi)

    ######################
    # Plot the asymmetry #
    ######################
    hi = [pe_asym]
    Styling.mc_style(pe_asym, 'T_t')
    #Styling.data_style(data_asym)
    pe_asym.SetTitle("exp. asymmetry")

    # from plots.common.histogram import norm
    # norm(pe_asym)
    # norm(data_asym)

    #data_asym.SetMarkerSize(1)

    canv = plot_hists(hi, x_label="asymmetry", draw_cmd=["l2"])
    line = ROOT.TLine(measured_asym, 0, measured_asym, 0.5*pe_asym.GetMaximum())
    def line_title():
        return "meas. (stat. + syst.)"
    line.GetTitle = line_title

    import math
    err = math.sqrt(reduce(lambda x, y: x**2 + y**2, list(measured_asym_errs[lep])))
    low, high = measured_asym - err, measured_asym + err

    line_low = ROOT.TLine(low, 0, low, 0.5*pe_asym.GetMaximum())
    line_high = ROOT.TLine(high, 0, high, 0.5*pe_asym.GetMaximum())

    for l in [line_low, line_high]:
        l.SetLineStyle(2)

    lb = lumi_textbox(lumi,
        pos='top-center',
        line2="#scale[1.5]{A = %.2f #pm %.2f (stat.) #pm %.2f (syst.)}" % (
            measured_asym, measured_asym_errs[lep][0],  measured_asym_errs[lep][1]
        ), nudge_y=0.03
    )
    line.Draw("SAME")
    line_low.Draw("SAME")
    line_high.Draw("SAME")

    leg = legend(hi + [line], styles=['f', 'f'], legend_pos='top-left', nudge_y=-0.14)
    pmi = PlotMetaInfo(
        'asymmetry',
        '2j1t_mva_loose {0}'.format(channel),
        'weighted to lumi={0}, sf(tchan)={1}'.format(lumi, fitpars[lep]),
        [args.infileMC, args.infileD]
    )
    of.savePlot(canv, pmi)
    print 80*"-"
    print "Expected %.2f ± %.2f, measured %.2f" % (pe_asym.GetMean(), pe_asym.GetRMS(), measured_asym)
    print "All done"
