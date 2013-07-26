#!/usr/bin/python
# -*- coding: utf-8 -*-

import math

from ROOT import *

from Variable import *
from DatasetGroup import *
from plots.common.legend import legend
from plots.common.utils import lumi_textbox
from plots.common.tdrstyle import *
import os
import logging

def plot_fit(var, fitConf, hData, fit_result, lumi):
    tdrstyle()
    canvases = []
    infile = "fits/"+var.shortName+"_fit_"+fitConf.name+".root"
    f = TFile(infile)

    try:
        os.mkdir("fit_plots")
    except Exception as e:
        logging.warning(str(e))

    outfile_name = "fit_plots/"+var.shortName+"_Fit_"+fitConf.name

    #print fit_result
    QCDRATE = fit_result.qcd
    QCDRATE_UP = fit_result.qcd + fit_result.qcd_uncert
    QCDRATE_DOWN = fit_result.qcd - fit_result.qcd_uncert
    NONQCDRATE = fit_result.nonqcd
    NONQCDRATE_UP = fit_result.nonqcd + fit_result.nonqcd_uncert
    NONQCDRATE_DOWN = fit_result.nonqcd - fit_result.nonqcd_uncert
    WJETS = fit_result.wjets
    WJETS_UP = fit_result.wjets + fit_result.wjets_uncert
    WJETS_DOWN = fit_result.wjets - fit_result.wjets_uncert
    
    cst = TCanvas("Histogram_"+fitConf.name,fitConf.name,10,10,1000,1000)

    hNonQCD = TH1D(f.Get(var.shortName+"__nonqcd"))
    hNonQCD.SetTitle("Non-QCD")
    hNonQCD.SetLineColor(kRed)

    hNonQCDp=TH1D(hNonQCD)
    hNonQCDp.Scale(NONQCDRATE_UP/NONQCDRATE)
    hNonQCDm=TH1D(hNonQCD)
    hNonQCDm.Scale(NONQCDRATE_DOWN/NONQCDRATE)

    hNonQCDp.SetLineColor(kOrange)
    hNonQCDp.SetTitle("Non-QCD #pm 1 #sigma")
    hNonQCDm.SetLineColor(kOrange)
    hNonQCDm.SetTitle("non-QCD - 1 sigma")

    hWJets = TH1D(f.Get(var.shortName+"__wjets"))
    hWJets.SetTitle("W+Jets")
    hWJets.SetLineColor(kGreen+4)

    hWJetsp=TH1D(hWJets)
    hWJetsm=TH1D(hWJets)
    if WJETS>0:
        hWJetsp.Scale(WJETS_UP/WJETS)
        hWJetsm.Scale(WJETS_DOWN/WJETS)

    hWJetsp.SetLineColor(kGreen+8)
    hWJetsp.SetTitle("W+Jets #pm 1 #sigma")
    hWJetsm.SetLineColor(kGreen+8)
    hWJetsm.SetTitle("W+Jets - 1 sigma")

    hData.SetNameTitle(var.shortName+"__DATA", "Data")
    hData.SetMarkerStyle(20)
     
    #print "data integral: ",hData.Integral()
    hQCD = f.Get(var.shortName+"__qcd")
    hQCD.SetNameTitle(var.shortName+"__qcd", "QCD")
    hQCD.SetLineColor(kYellow)

    hQCDp=TH1D(hQCD)
    hQCDp.Scale(QCDRATE_UP/QCDRATE)
    hQCDm=TH1D(hQCD)
    hQCDm.Scale(QCDRATE_DOWN/QCDRATE)

    hQCDp.SetLineColor(kGreen)
    hQCDp.SetTitle("QCD #pm 1 #sigma")
    hQCDm.SetLineColor(kGreen)
    hQCDm.SetTitle("QCD #pm 1 #sigma")

    hTotal=TH1D(hNonQCD)
    hTotal.Add(hQCD)
    hTotal.Add(hWJets)
    hTotal.SetLineColor(kBlue)
    hTotal.SetTitle("Fitted total")
    max_bin = hData.GetMaximum()*1.6
    hData.SetAxisRange(0, max_bin, "Y")
    hData.GetXaxis().SetTitle(var.displayName)
    #hTotal.Draw("")
    title = fit_result.getTitle()
    hData.SetMarkerStyle(20)
    hData.Draw("E1")
    hNonQCDp.Draw("same")
    hQCD.Draw("same")
    hNonQCD.Draw("same")
    hNonQCDm.Draw("same")
    hQCDp.Draw("same")
    hQCDm.Draw("same") 
   
    hWJets.Draw("same")
    hWJetsp.Draw("same")
    hWJetsm.Draw("same")
    hTotal.Draw("same")
    #hData.SetTitle("QCD fit, "+title)
    hData.Draw("E1 same")

    lumibox = lumi_textbox(lumi)

    leg = legend(
         [hData, hQCD, hQCDp, hNonQCD, hNonQCDp, hWJets, hWJetsp, hTotal],
         styles=["p", "l"],
         width=0.2
     )

    leg.Draw()

    #print hNonQCD.Integral(), hData.Integral(), hQCD.Integral(), hTotal.Integral(), hQCDp.Integral(), hQCDm.Integral()
    cst.Update()
    cst.SaveAs(outfile_name+".png")
    cst.SaveAs(outfile_name+".pdf")
    cst.Draw()
    return cst
   
def plot_fit_shapes(var, fitConf, hData, fit_result):
   tdrstyle()
   canvases = []
   infile = "fits/"+var.shortName+"_fit_"+fitConf.name+".root"
   f = TFile(infile)
   
   print fitConf.name
   outfile_name = "fit_plots/"+var.shortName+"_shapes_"+fitConf.name
   
   cst = TCanvas("Histogram_"+fitConf.name,fitConf.name,10,10,1000,1000)
   
   hNonQCD = TH1D(f.Get(var.shortName+"__nonqcd"))
   hNonQCD.SetTitle("Non-QCD")   
   hNonQCD.SetLineColor(kRed)
   hNonQCD.Scale(1/hNonQCD.Integral())
      
   hWJets = TH1D(f.Get(var.shortName+"__wjets"))
   hWJets.SetTitle("W+Jets")   
   hWJets.SetLineColor(kGreen+4)
   hWJets.Scale(1/hWJets.Integral())
   
   hData.SetNameTitle(var.shortName+"__DATA", "Data")
   hData.SetMarkerStyle(20)
   hData.Scale(1/hData.Integral())

   #print "data integral: ",hData.Integral()
   hQCD = f.Get(var.shortName+"__qcd")
   hQCD.SetNameTitle(var.shortName+"__qcd", "QCD")
   hQCD.SetLineColor(kGray)
   hQCD.Scale(1/hQCD.Integral())   
   
   max_bin = hData.GetMaximum()*1.6
   hData.SetAxisRange(0, max_bin, "Y")
   hData.GetXaxis().SetTitle(var.displayName)
   #hTotal.Draw("")
   title = fit_result.getTitle()
   hData.SetMarkerStyle(20)
   hData.Draw("E1")
   hQCD.Draw("same")
   hNonQCD.Draw("same") 
   hWJets.Draw("same")
   #hData.SetTitle("QCD fit, "+title)
   hData.Draw("E1 same")

   lumibox = lumi_textbox(19739)

   leg = legend(
        [hData, hQCD, hNonQCD, hWJets],
        styles=["p", "l"],
        width=0.2
    ) 

   leg.Draw()
          
   #print hNonQCD.Integral(), hData.Integral(), hQCD.Integral(), hTotal.Integral(), hQCDp.Integral(), hQCDm.Integral()
   cst.Update()
   cst.SaveAs(outfile_name+".png")
   cst.SaveAs(outfile_name+".pdf")
   cst.Draw()
   return cst
