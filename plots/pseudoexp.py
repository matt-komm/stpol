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
        #print "Integrating over ",range(a, b)
        I = sum([hist.GetBinContent(i) for i in range(a, b)])
        #print a,b, I
        return I
    low = my_int(1, center)
    high = my_int(center, hist.nbins()+1)
    if (low+high - hist.Integral())>0.01:
        raise Exception("Low and high parts don't sum to the integral: %.2f + %.2f != %.2f" % (low, high, hist.Integral()))
    asy = (high-low)/(low+high)
    return asy


fitpars = {}
fitpars['mu'] = 1.03
fitpars['ele'] = 0.95

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
        hasym = Hist(100, 0.0, 0.7, title='posterior PE')

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

    #Take the lumis from a central database
    lumi = lumis["83a02e9_Jul22"]["iso"][lep]

    pe_post, pe_asym, binning = get_posterior(args.infileMC)
    data_post, data_asym, binning = get_posterior(args.infileD)

    data_post.SetTitle("unfolded data")
    data_asym.SetTitle("unfolded data")
    
    # Make the ansatz that the pseudo-experiment distribution
    # describes the distribution of the unfolding result, that is
    # that we can take the PE error as the final error on the unfolding.
    for i in range(1, data_post.nbins()+1):
        data_post.SetBinError(i, pe_post.GetBinError(i))

    # Get the true distribution at generator level,
    # requiring the presence of a lepton with the
    # correct gen flavour
    htrue = None
    for fn in ["T_t_ToLeptons", "Tbar_t_ToLeptons"]:
        s = Sample.fromFile("data/Jul26/%s/mc/iso/nominal/Jul15/%s.root" % (lep, fn))
        hi = s.drawHistogram("true_cos_theta", str(Cuts.true_lepton(lep)), binning=binning)
        hi.Scale(s.lumiScaleFactor(lumi))
        if htrue:
            htrue += hi
        else:
            htrue = hi
    htrue.SetTitle("generated")

    #Scale to the final fit
    htrue.Scale(fitpars[lep])

    #Normalize to same area
    #htrue.Scale(data_post.Integral() / htrue.Integral())

    #####################
    # Plot the unfolded #
    #####################
    from plots.common.sample_style import Styling
    #Styling.mc_style(pe_post, 'T_t')
    Styling.mc_style(htrue, 'T_t')
    htrue.SetLineColor(ROOT.kGreen)
    htrue.SetFillColor(ROOT.kGreen)
    htrue.SetMarkerSize(0)
    Styling.data_style(data_post)

    hi = [data_post, htrue]
    chi2 = data_post.Chi2Test(htrue, "WW CHI2/NDF")
    htrue.SetTitle(htrue.GetTitle() + " #chi^{2}/#nu = %.1f" % chi2)
    hi_norm = map(post_normalize, hi)
    for h in hi[1:]:
        h.SetMarkerSize(0)
    of = OutputFolder(subdir='unfolding/%s' % lep)
    canv = plot_hists(hi_norm, x_label="cos #theta", draw_cmd=["E1", "E1"], y_label="a.u.")
    leg = legend(hi, styles=['p', 'f'], legend_pos='top-left', nudge_x=-0.08)
    lb = lumi_textbox(lumi,
            pos='top-right',
            line2="#scale[3.0]{A = %.2f #pm %.2f}" % (data_asym.GetMean(), pe_asym.GetRMS())
        )
    pmi = PlotMetaInfo('costheta_unfolded_%s' % lep, 'genlevel', 'None', [args.infileMC, args.infileD])
    of.savePlot(canv, pmi)

    ######################
    # Plot the asymmetry #
    ######################
    hi = [pe_asym]
    Styling.mc_style(pe_asym, 'T_t')
    pe_asym.SetMarkerSize(0)
    Styling.data_style(data_asym)
    canv = plot_hists(hi, x_label="asymmetry", draw_cmd=["l2"])
    line = ROOT.TLine(data_asym.GetMean(), 0, data_asym.GetMean(), 0.5*pe_asym.GetMaximum())
    lb = lumi_textbox(lumi, line2="exp. %.2f #pm %.2f, meas. %.2f" % (pe_asym.GetMean(), pe_asym.GetRMS(), data_asym.GetMean()))
    line.Draw("SAME")
    leg = legend(hi, styles=['f'])
    pmi = PlotMetaInfo('asymmetry_%s' % lep, 'genlevel', 'None', [args.infileMC, args.infileD])
    of.savePlot(canv, pmi)
    print 80*"-"
    print "Expected %.2f ± %.2f, measured %.2f" % (pe_asym.GetMean(), pe_asym.GetRMS(), data_asym.GetMean())
    print "All done"
