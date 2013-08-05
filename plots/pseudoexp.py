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
from plots.fit_scale_factors import fitpars
from plots.common.cross_sections import lumis
import argparse

def find_bin_idx(binning, val):
    for b, i in zip(binning, range(len(binning))):
        if b>val:
            return i+1

def get_binning(hi):
    return [hi.GetBinLowEdge(i) for i in range(1, hi.GetNbinsX()+2)]

def get_bin_widths(hi):
    return [hi.GetBinWidth(i) for i in range(1, hi.GetNbinsX()+1)]

def asymmetry(hist, center):
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
    args = parser.parse_args()


    ROOT.TH1F.AddDirectory(False)
    def get_posterior(fn):
        logger.info("Loading pseudoexperiments from file %s" % fn)
        fi = ROOT.TFile(fn)
        t = fi.Get("unfolded")

        #Make a histogram with a nonspecific binning just to have a memory address
        hi = ROOT.TH1D()
        #ROOT wants a pointer, use AddressOf
        t.SetBranchAddress(brname, ROOT.AddressOf(hi))
        #Initialize the histogram
        t.GetEntry(0)


        #Now we can have a proper histogram with the right bins
        binning = get_binning(hi)
        logger.info("Binning: %s" % str(binning))
        logger.info("widths: %s" % str(get_bin_widths(hi)))
        hi = Hist(binning, type='D')
        logger.debug("hi binning = %s" % (str(get_binning(hi))))
        t.SetBranchAddress(brname, ROOT.AddressOf(hi))
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
            else:
                posterior.SetBinError(i+1, hi.GetBinError(i))

        logger.debug("Posterior binning B = %s" % (str(get_binning(posterior))))
        return posterior, hasym, binning

    lep = "mu"
    lumi = lumis["83a02e9_Jul22"]["iso"][lep]

    pe_post, pe_asym, binning = get_posterior(args.infileMC)
    data_post, data_asym, binning = get_posterior(args.infileD)
    data_post.SetTitle("unfolded data")
    data_asym.SetTitle("unfolded data")

    s = Sample.fromFile("data/Jul26/%s/mc/iso/nominal/Jul15/T_t_ToLeptons.root" % lep)
    htrue = s.drawHistogram("true_cos_theta", str(Cuts.true_lepton(lep)), binning=binning)
    s1 = Sample.fromFile("data/Jul26/%s/mc/iso/nominal/Jul15/Tbar_t_ToLeptons.root" % lep)
    htrue1 = s1.drawHistogram("true_cos_theta", str(Cuts.true_lepton(lep)), binning=binning)
    htrue = htrue + htrue1

    #FIXME: correct scale factor
    htrue.Scale(fitpars['final_2j1t_mva'][lep][0][1])

    htrue.SetTitle("generated")
    print "gen binning", get_binning(htrue)
    print "PE binning", get_binning(pe_post)
    print "Generated asymmetry =", asymmetry(htrue, find_bin_idx(list(htrue.x()), 0))
    from plots.common.sample_style import Styling
    Styling.mc_style(pe_post, 'T_t')
    Styling.mc_style(htrue, 'T_t')
    htrue.SetLineColor(ROOT.kGreen)
    htrue.SetFillColor(ROOT.kGreen)
    Styling.data_style(data_post)

    hi = [data_post, pe_post, htrue]
    for h in hi:
        logger.debug("%s int=%.2f" % (h.title, h.Integral()))
        logger.debug("last low edge %.2f, last width %.2f" % (h.GetBinLowEdge(h.GetNbinsX()), h.GetBinWidth(h.GetNbinsX())))
    for h in hi[1:]:
        h.SetMarkerSize(0)
    of = OutputFolder(subdir='unfolding')
    htrue.Scale(s.lumiScaleFactor(lumi))
    #htrue.Scale(pe_post.Integral() / htrue.Integral())
    canv = plot_hists(hi, x_label="cos #Theta", draw_cmd=["E1", "E1", "E1"], do_chi2=True)
    leg = legend(hi, styles=['p', 'f', 'f'], legend_pos='top-left', nudge_x=-0.08)
    lb = lumi_textbox(lumi,
            pos='top-right',
            line2="A=%.2f (meas.), %.2f #pm %.2f (exp.)" % (data_asym.GetMean(), pe_asym.GetMean(), pe_asym.GetRMS())
        )
    #canv.SaveAs("cos_theta_unfolded.pdf")
    pmi = PlotMetaInfo('costheta_unfolded', 'genlevel', 'None', [args.infileMC, args.infileD])
    of.savePlot(canv, pmi)

    hi = [pe_asym]
    Styling.mc_style(pe_asym, 'T_t')
    pe_asym.SetMarkerSize(0)
    Styling.data_style(data_asym)
    canv = plot_hists(hi, x_label="asymmetry", draw_cmd=["l2"])
    #canv.SetLogy()
    line = ROOT.TLine(data_asym.GetMean(), 0, data_asym.GetMean(), 0.5*pe_asym.GetMaximum())
    lb = lumi_textbox(lumi, line2="A=%.2f (meas.), %.2f #pm %.2f (exp.)" % (data_asym.GetMean(), pe_asym.GetMean(), pe_asym.GetRMS()))
    #line.SetTitle("measured")
    line.Draw("SAME")
    leg = legend(hi, styles=['f'])
    #canv.SaveAs("asymmetry.pdf")
    pmi = PlotMetaInfo('asymmetry', 'genlevel', 'None', [args.infileMC, args.infileD])
    of.savePlot(canv, pmi)
    print "Expected %.2f ± %.2f, measured %.2f" % (pe_asym.GetMean(), pe_asym.GetRMS(), data_asym.GetMean())

    htrue1 = s.drawHistogram("true_cos_theta", str(Cuts.true_lepton(lep)), plot_range=[20, -1, 1])
    idx= find_bin_idx(list(htrue1.x()), 0)
    print asymmetry(htrue1, idx), idx
    # I, E = calc_int_err(posterior)
    # logger.info("Posterior costheta integral=%.2f" % I)

    # canv = plot_hists([posterior], x_label="cos #Theta")
    # leg = legend([posterior], styles=['p'])
    # pmi = PlotMetaInfo('posterior_pseudoexp', 'final_2J1T', 'None', fi.GetPath())
    # of.savePlot(canv, pmi)

    # canv = plot_hists([hasym], x_label="asymmetry")
    # leg = legend([hasym], styles=['p'], legend_pos='top-left')
    # pmi = PlotMetaInfo('asymmetry_pseudoexp', 'final_2J1T', 'None', fi.GetPath())
    # of.savePlot(canv, pmi)
    # logger.info("Asymmetry PE mean=%.2f, stddev=%.2f" % (hasym.GetMean(), hasym.GetRMS()))
    print "All done"
