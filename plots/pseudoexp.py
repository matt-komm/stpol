#!/usr/bin/env python
"""
Plots the distribution from the pseudo-experiments drawn by theta.
"""

import ROOT
ROOT.gROOT.SetBatch(True)
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("pseodoexp")
from rootpy.plotting import Hist
import numpy as np
from plots.common.hist_plots import plot_hists
from plots.common.output import OutputFolder
from plots.common.metainfo import PlotMetaInfo
from plots.common.legend import legend
from plots.common.histogram import calc_int_err
import argparse

def find_bin_idx(binning, val):
    for b, i in zip(binning, range(len(binning))):
        if b>val:
            return i

def asymmetry(hist, center):
    low = hist.Integral(1, center-1)
    high = hist.Integral(center, hist.nbins())
    if (low+high - hist.Integral())>0.01:
        raise Exception("Low and high parts don't sum to the integral: %.2f + %.2f != %.2f" % (low, high, hist.Integral()))
    asy = (low-high)/(low+high)
    return asy


if __name__=="__main__":
    from plots.common.tdrstyle import tdrstyle
    tdrstyle()

    #THhe name of the pseudoexperiment TH1D
    brname = "tunfold"

    parser = argparse.ArgumentParser(
        description='Plots the pseudoexperiment distribution'
    )
    parser.add_argument("infile",
        default=None, type=str,
        help="The input file from Theta, which contains a TTree:products\
        , which has a leaf TH1D:%s" % brname
    )
    args = parser.parse_args()


    logger.info("Loading pseudoexperiments from file %s" % args.infile)
    fi = ROOT.TFile(args.infile)
    t = fi.Get("unfolded")

    #Make a histogram with a nonspecific binning just to have a memory address
    hi = Hist(1, 0, 1, type='D')
    #ROOT wants a pointer, use AddressOf
    t.SetBranchAddress(brname, ROOT.AddressOf(hi))
    #Initialize the histogram
    t.GetEntry(0)

    #Now we can have a proper histogram with the right bins
    binning = list(hi.x())
    logger.info("Binning: %s" % str(binning))
    hi = Hist(binning, type='D')
    t.SetBranchAddress(brname, ROOT.AddressOf(hi))
    nbins = len(binning)
    nentries = t.GetEntries()

    #Create a vector for the bin contents. Rows - histos, cols - bins
    bins = np.empty((nentries, nbins), dtype='f')
    i=0

    #The asymmetry distribution
    hasym = Hist(100, -0.51, -0.2, name='asymmetry', title='posterior PE')

    #Find the bin index where costheta=0 (center)
    center = find_bin_idx(binning, 0)+1

    logger.info("Central bin index = %d" % center)
    
    #Fill the bin contents vector and the asymmetry histogram by looping over the events
    for ev in t:
        bins[i] = np.array(list(hi.y()), dtype='f')
        i += 1
        hasym.Fill(asymmetry(hi, center))
    logger.info("Looped over %d entries" % i)

    #The distribution of the unfolded costheta
    posterior = Hist(binning, type='D', name='posterior', title='posterior PE')

    #Fill the posterior histogram
    for i in range(nbins):
        posterior.SetBinContent(i+1, np.mean(bins[:,i]))
        posterior.SetBinError(i+1, np.std(bins[:,i]))

    I, E = calc_int_err(posterior)
    logger.info("Posterior costheta integral=%.2f" % I)
    of = OutputFolder(subdir='unfolding')

    canv = plot_hists([posterior], x_label="cos #Theta")
    leg = legend([posterior], styles=['p'])
    pmi = PlotMetaInfo('posterior_pseudoexp', 'final_2J1T', 'None', fi.GetPath())
    of.savePlot(canv, pmi)

    canv = plot_hists([hasym], x_label="asymmetry")
    leg = legend([hasym], styles=['p'], legend_pos='top-left')
    pmi = PlotMetaInfo('asymmetry_pseudoexp', 'final_2J1T', 'None', fi.GetPath())
    of.savePlot(canv, pmi)
    logger.info("Asymmetry PE mean=%.2f, stddev=%.2f" % (hasym.GetMean(), hasym.GetRMS()))
    print "All done"
