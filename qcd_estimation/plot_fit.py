#!/usr/bin/python
# -*- coding: utf-8 -*-

import math

from ROOT import *

from Variable import *
#from DatasetGroup import *
from legend import legend
from utils import lumi_textbox
from tdrstyle import *
import os
import logging
#from plots.common.distribution_plot import plot_hists

def plot_fit(var, fitConf, hData, fit_result, lumi):
    tdrstyle()
    canvases = []
    infile = "fits/"+var.shortName+"_fit_"+fitConf.name+".root"
    outfile_wd = "fits/"+var.shortName+"_fit_"+fitConf.name+"_withData.root"
    f = TFile(infile)
    f2 = TFile(outfile_wd, "recreate")
    f2.cd()

    try:
        os.mkdir("fit_plots")
    except Exception as e:
        logging.warning(str(e))

    outfile_name = "fit_plots/"+var.shortName+"_Fit_"+fitConf.name

    #print fit_result
    QCDRATE = fit_result.qcd
    #QCDRATE_UP = fit_result.qcd + fit_result.qcd_uncert
    #QCDRATE_DOWN = fit_result.qcd - fit_result.qcd_uncert
    QCDRATE_UP = fit_result.qcd * math.e**((fit_result.result["qcd"]["beta_signal"][0][0]+fit_result.result["qcd"]["beta_signal"][0][1])) / math.e**((fit_result.result["qcd"]["beta_signal"][0][0]))
    QCDRATE_DOWN = fit_result.qcd * math.e**((fit_result.result["qcd"]["beta_signal"][0][0]-fit_result.result["qcd"]["beta_signal"][0][1])) / math.e**((fit_result.result["qcd"]["beta_signal"][0][0]))
    #NONQCDRATE = fit_result.nonqcd
    #NONQCDRATE_UP = fit_result.nonqcd + fit_result.nonqcd_uncert
    #NONQCDRATE_DOWN = fit_result.nonqcd - fit_result.nonqcd_uncert
    NONQCDRATE = math.e**((fit_result.result["qcd"]["nonqcd_rate"][0][0])*fit_result.coeff["nonqcd"])
    NONQCDRATE_UP = math.e**((fit_result.result["qcd"]["nonqcd_rate"][0][0]+fit_result.result["qcd"]["nonqcd_rate"][0][1])*fit_result.coeff["nonqcd"])
    NONQCDRATE_DOWN = math.e**((fit_result.result["qcd"]["nonqcd_rate"][0][0]-fit_result.result["qcd"]["nonqcd_rate"][0][1])*fit_result.coeff["nonqcd"])

    WJETS = math.e**((fit_result.result["qcd"]["wjets_rate"][0][0])*fit_result.coeff["wjets"])
    WJETS_UP = math.e**((fit_result.result["qcd"]["wjets_rate"][0][0]+fit_result.result["qcd"]["wjets_rate"][0][1])*fit_result.coeff["wjets"])
    WJETS_DOWN = math.e**((fit_result.result["qcd"]["wjets_rate"][0][0]-fit_result.result["qcd"]["wjets_rate"][0][1])*fit_result.coeff["wjets"])

    print "Results with fit uncertainty included"
    print "QCD: ", QCDRATE, "+", (QCDRATE_UP - QCDRATE), "-", (QCDRATE - QCDRATE_DOWN)
    print "Non-QCD: ", NONQCDRATE, "+", (NONQCDRATE_UP - NONQCDRATE), "-", (NONQCDRATE - NONQCDRATE_DOWN)
    print "W+jets: ", WJETS, "+", (WJETS_UP - WJETS), "-", (WJETS - WJETS_DOWN)

    #WJETS = fit_result.wjets
    #WJETS_UP = fit_result.wjets + fit_result.wjets_uncert
    #WJETS_DOWN = fit_result.wjets - fit_result.wjets_uncert
    
    cst = TCanvas("Histogram_"+fitConf.name,fitConf.name,10,10,1000,1000)

    hNonQCD = TH1D(f.Get(var.shortName+"__nonqcd"))
    hNonQCD.Write()
    hNonQCD.SetTitle("Non-QCD")
    hNonQCD.SetLineColor(kRed)

    hNonQCDp=TH1D(hNonQCD)
    hNonQCDp.SetName(var.shortName+"__nonqcd__plus")
    hNonQCDp.Scale(NONQCDRATE_UP/NONQCDRATE)
    hNonQCDp.Write()
    hNonQCDm=TH1D(hNonQCD)
    
    hNonQCDm.Scale(NONQCDRATE_DOWN/NONQCDRATE)
    hNonQCDm.SetName(var.shortName+"__nonqcd__minus")
    hNonQCDm.Write()
    hNonQCDp.SetLineColor(kOrange)
    hNonQCDp.SetTitle("Non-QCD #pm 1 #sigma")
    hNonQCDm.SetLineColor(kOrange)
    hNonQCDm.SetTitle("non-QCD - 1 sigma")

    hWJets = TH1D(f.Get(var.shortName+"__wjets"))
    hWJets.Write()
    hWJets.SetTitle("W+Jets")
    hWJets.SetLineColor(kGreen+4)

    hWJetsp=TH1D(hWJets)
    hWJetsp.SetName(var.shortName+"__wjets_plus")
    hWJetsm=TH1D(hWJets)
    hWJetsm.SetName(var.shortName+"__wjets_minus")
    if WJETS>0:
        hWJetsp.Scale(WJETS_UP/WJETS)
        hWJetsm.Scale(WJETS_DOWN/WJETS)

    hWJetsp.Write()
    hWJetsm.Write()
    
    hWJetsp.SetLineColor(kGreen+8)
    hWJetsp.SetTitle("W+Jets #pm 1 #sigma")
    hWJetsm.SetLineColor(kGreen+8)
    hWJetsm.SetTitle("W+Jets - 1 sigma")

    hData.SetNameTitle(var.shortName+"__DATA", "Data")
    hData.Write()    
    hData.SetMarkerStyle(20)
     
    #print "data integral: ",hData.Integral()
    hQCD = f.Get(var.shortName+"__qcd")
    hQCD.Write()
    hQCD.SetNameTitle(var.shortName+"__qcd", "QCD")
    hQCD.SetLineColor(kYellow)

    hQCDp=TH1D(hQCD)
    hQCDp.Scale(QCDRATE_UP/QCDRATE)
    hQCDm=TH1D(hQCD)
    hQCDm.Scale(QCDRATE_DOWN/QCDRATE)
    hQCDp.SetName(var.shortName+"__qcd_plus")
    hQCDp.Write()
    hQCDm.SetName(var.shortName+"__qcd_minus")
    hQCDm.Write()

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
   
def plot_fit_shapes(var, fitConf, hData, fit_result, lumi, shapes):
   tdrstyle()
   canv = TCanvas("c", "c")
   canv.SetWindowSize(1000, 1000)
   canv.SetCanvasSize(1000, 1000)   
   outfile_name = "fit_plots/"+var.shortName+"_shapes_"+fitConf.name
   shapes[-1].SetTitle("QCD")
   canv = plot_hists(canv, {"shapes": shapes},
        x_label=var.displayName,
        #        title=process,
        max_bin_mult=1.4
   )
            
   #Draws the lumi box
   #lumibox = lumi_textbox(lumi_iso[channel])
            
   #Draw the legend
   leg = legend(
        shapes, # <<< need to reverse MC order here, mc3 is top-most
        styles=["l"],
        width=0.2,
        text_size=0.015
   )

   lumibox = lumi_textbox(lumi)

   leg.Draw()
          
   #print hNonQCD.Integral(), hData.Integral(), hQCD.Integral(), hTotal.Integral(), hQCDp.Integral(), hQCDm.Integral()
   canv.Update()
   canv.SaveAs(outfile_name+".png")
   canv.SaveAs(outfile_name+".pdf")
   canv.Draw()
    
   return canv


def plot_all_fit_shapes(var, fitConf, hData, fit_result, lumi):
   tdrstyle()
   canvases = []
   infile = "fits/"+var.shortName+"_fit_"+fitConf.name+".root"
   f = TFile(infile)
   
   print fitConf.name
   outfile_name = "fit_plots/"+var.shortName+"_all_shapes_"+fitConf.name
   
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
   
   max_bin = hQCD.GetMaximum()*1.3
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

   lumibox = lumi_textbox(lumi)

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


   
def plot_fit2(fit_templates_file, qcd_result, other_results, priors, extra = {}):
    templates_file = fit_templates_file.replace("reversecut", "nocut").replace("qcdcut", "nocut")
    var = templates_file.split("/")[1].split("__")[0]
    jt = templates_file.split("/")[1].split("__")[1]
    channel = templates_file.split("/")[1].split("__")[2]
    reg = fit_templates_file.split("/")[1].split("__")[3]
    added = fit_templates_file.split("/")[1].split("__")[4]
    
    f = TFile(templates_file)    
    print "using templates", templates_file
    extra_string = ""
    extra_id = ""
    for k,v in extra.items():
        extra_id += k+"_"+v
        vark = k.replace("varMC_QCDMC",", QCD from MC").replace("varMC_",", MC antiiso").replace("isovar", "Anti-iso range")
        extra_string += "%s %s" % (vark,v)

    display_var = var.replace("qcd_mva", "QCD BDT")
    
    print channel, jt    
    tdrstyle()
    gStyle.SetOptTitle(1)
    canvases = []
    #infile = "fits/"+var.shortName+"_fit_"+jt+"_"+channel+"_"+cutid+".root"
    #infile2 = "templates/"+var.shortName+"_templates_"+jt+"_"+channel+"_"+cutid+".root"
    #cutinfo = "_".join(cutid.split("_")[1:])
    #infile3 = "templates/"+var.shortName+"_templates_"+jt+"_"+channel+"_nocut_"+cutinfo+".root"
    
    #outfile_wd = "fits/"+var+"_fit_"+jt+"_"+channel+".root"
    #outf = TFile(outfile_wd, "recreate")
    #outf.cd()

    try:
        os.mkdir("fit_plots")
    except Exception as e:
        logging.warning(str(e))

    outfile_name = "fit_plots/"+var+"_Fit_"+jt+"_"+channel+"_"+reg+"_"+added+"_"+extra_id#+"_"+cutid


    hData = TH1D(f.Get(var+"__DATA"))
    hQCD = TH1D(f.Get(var+"__QCD"))
    #print qcd_result    
    print "initial"    
    print "QCD:", hQCD.Integral()
    print "Data:", hData.Integral()
    
    hQCD.Scale(qcd_result[0])
    hTotal = TH1D(hQCD)
    
    
    """cut = get_cut(var, channel)
    for bin in range(hData.GetNbinsX()+2):
        if abs(hData.GetBinLowEdge(bin) - cut) < 1e-8:
            low = bin        
    high = hData.GetNbinsX()+1
    """
    other_templates = {}
    #print other_results
    first = True 
    for temp in other_results.keys():
        other_templates[temp] = TH1D(f.Get(var+"__"+temp))
        #print other_templates[temp].Integral(),  other_results[temp][0], priors[temp]
        sf = math.e**(other_results[temp][0] * priors[temp])
        print temp, other_templates[temp].Integral()
        other_templates[temp].Scale(sf)
        if first:
            hNonQCD = TH1D(f.Get(var+"__"+temp))
            first = False
        else: 
            hNonQCD.Add(other_templates[temp])
        hTotal.Add(other_templates[temp])
        #print "SF",  temp, other_templates[temp].Integral()
    chi2 = hData.Chi2Test(hTotal, "UW CHI2/NDF")
    print "chi2", chi2
    
    cst = TCanvas("Histogram_","histo",10,10,1000,1000)
    cst.SetTopMargin(0.9)
    #print infile
    #print f
    #print f.Get(var.shortName+"__nonqcd")
    hNonQCD.SetTitle("Non-QCD")
    hNonQCD.SetLineColor(kRed)

    hData.SetMarkerStyle(20)
     
    hQCD.SetNameTitle("QCD", "QCD")
    hQCD.SetLineColor(kYellow)

    """hQCDp=TH1D(hQCD)
    hQCDp.Scale(QCDRATE_UP/QCDRATE)
    hQCDm=TH1D(hQCD)
    hQCDm.Scale(QCDRATE_DOWN/QCDRATE)
    hQCDp.SetName(var.shortName+"__qcd_plus")
    hQCDp.Write()
    hQCDm.SetName(var.shortName+"__qcd_minus")
    hQCDm.Write()

    hQCDp.SetLineColor(kGreen)
    hQCDp.SetTitle("QCD #pm 1 #sigma")
    hQCDm.SetLineColor(kGreen)
    hQCDm.SetTitle("QCD #pm 1 #sigma")
    
    hTotal=TH1D(hNonQCD)
    hTotal.Add(hQCD)
    """
    hTotal.SetLineColor(kBlue)
    hTotal.SetTitle("Fitted total")
    max_bin = hData.GetBinContent(hData.GetMaximumBin())*1.5
    hData.SetAxisRange(0, max_bin, "Y")
    hData.GetXaxis().SetTitle(display_var)
    #hTotal.Draw("")
    title = jt + ", "+channel
    hData.SetTitle(title)
    hData.SetMarkerStyle(20)
    #print "data", hData.Integral()
    hData.Draw("E1")
    #print "data", hData.Integral()
    #hNonQCDp.Draw("same")
    hQCD.SetLineColor(kGreen+2)
    hQCD.SetLineWidth(3)
    hQCD.Draw("same")
    hNonQCD.Draw("same hist")
    #hNonQCDm.Draw("same")
    #hQCDp.Draw("same")
    #hQCDm.Draw("same") 
   
    hTotal.Draw("same hist")
    
    #hData.SetTitle("QCD fit, "+title)
    hData.Draw("E1 same")

    lumi = 15311
    if channel == "ele":
        lumi = 16934
    lumibox = lumi_textbox(lumi)
    hDataCopy = TH1D(hData)
    hDataCopy.SetTitle("Data")
    
    leg = legend(
         [hDataCopy, hQCD, #hQCDp, 
            hNonQCD, #hNonQCDp, 
            hTotal],
         styles=["p", "l"],
         width=0.2
     )
    #outf.Close()
    cst.Update()
    cst.SaveAs(outfile_name+".png")
    cst.SaveAs(outfile_name+".pdf")
    #cst.Draw()

    print "final"    
    print "QCD:", hQCD.Integral()
    print "Data:", hData.Integral()
    print "other", hNonQCD.Integral()
    print "total", hTotal.Integral()

    """
    print fit_result
    QCDRATE = fit_result.qcd
    #QCDRATE_UP = fit_result.qcd * math.e**((fit_result.result["qcd"]["beta_signal"][0][0]+fit_result.result["qcd"]["beta_signal"][0][1])) / math.e**((fit_result.result["qcd"]["beta_signal"][0][0]))
    qcdsf_up = fit_result.result["qcd"]["beta_signal"][0][0] + fit_result.result["qcd"]["beta_signal"][0][1]
    QCDRATE_UP = fit_result.qcd * (qcdsf_up / qcdsf)
	#QCDRATE_DOWN = fit_result.qcd * math.e**((fit_result.result["qcd"]["beta_signal"][0][0]-fit_result.result["qcd"]["beta_signal"][0][1])) / math.e**((fit_result.result["qcd"]["beta_signal"][0][0]))
    qcdsf_down = fit_result.result["qcd"]["beta_signal"][0][0] - fit_result.result["qcd"]["beta_signal"][0][1]
    QCDRATE_DOWN = fit_result.qcd * (qcdsf_down / qcdsf)
    #NONQCDRATE = fit_result.nonqcd
    #NONQCDRATE_UP = fit_result.nonqcd + fit_result.nonqcd_uncert
    #NONQCDRATE_DOWN = fit_result.nonqcd - fit_result.nonqcd_uncert
    NONQCDRATE = math.e**((fit_result.result["qcd"]["nonqcd_rate"][0][0])*fit_result.coeff["nonqcd"])
    NONQCDRATE_UP = math.e**((fit_result.result["qcd"]["nonqcd_rate"][0][0]+fit_result.result["qcd"]["nonqcd_rate"][0][1])*fit_result.coeff["nonqcd"])
    NONQCDRATE_DOWN = math.e**((fit_result.result["qcd"]["nonqcd_rate"][0][0]-fit_result.result["qcd"]["nonqcd_rate"][0][1])*fit_result.coeff["nonqcd"])


    #WJETS = fit_result.wjets
    #WJETS_UP = fit_result.wjets + fit_result.wjets_uncert
    #WJETS_DOWN = fit_result.wjets - fit_result.wjets_uncert
    """
    
