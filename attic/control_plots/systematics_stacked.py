#/usr/bin/python
# -*- coding: utf-8 -*-

import math
from ROOT import *

#from make_histos import *
from plotting import make_histogram, make_stack, make_histograms
from init_data import *
from Variable import *
from FitConfig import *
from DataLumiStorage import *
from util_scripts import *
from plots.common.tdrstyle import *
from plots.common.legend import legend
from plots.common.utils import lumi_textbox
from plots.common.odict import OrderedDict
from plots.common.cross_sections import lumi_iso, lumi_antiiso
#from get_qcd_yield import get_qcd_yield_with_selection
import tdrstyle

#Sorry, hacky stuff, but works
def reorder_stack(var, oldStack, hQCD):
    i = 0
    histos = []    
    stack = THStack("Stack", "stackName")
    stack.Add(hQCD)
    while i<7:
        for histo in oldStack.GetHists():
            if histo.GetTitle()=="Dibosons" and i==0:
                stack.Add(histo)
                i+=1 
            elif histo.GetTitle()=="Z+Jets" and i==1:
                stack.Add(histo)
                i+=1
            elif histo.GetTitle()=="W+Jets" and i==2:
                stack.Add(histo)
                i+=1
            elif histo.GetTitle()=="t #bar{t}" and i==3:
                stack.Add(histo)
                i+=1
            elif histo.GetTitle()=="tW-channel" and i==4:
                stack.Add(histo)
                i+=1
            elif histo.GetTitle()=="s-channel" and i==5:
                stack.Add(histo)
                i+=1
            elif histo.GetTitle()=="t-channel" and i==6:
                stack.Add(histo)
                i+=1
            #print histos
    return stack

if __name__=="__main__":
    "/iso/Nominal/"
    var = Variable("mt_mu", 0, 200, 20, "mtwMass", "m_{T }")    
    var = Variable("cos_theta", -1, 1, 10, "cos_theta", "cos_theta")
   
    lepton = "mu"
    cuts = FitConfig( "final_selection" )
        
    #((QCD_YIELD, error), fit) = get_qcd_yield_with_selection(lepton, selection)
    #Just use the calculated value
    QCD_YIELD = 284.0
    #cuts.setTrigger("1")
    cuts.setFinalCuts("top_mass < 220 && top_mass > 130 && abs(eta_lj)>2.5 && mt_mu>50")
    cuts.calcCuts()
    #print cuts
    lumis = DataLumiStorage(lumi_iso["mu"], lumi_antiiso["mu"])
    systematics = ["Nominal", "En", "Res", "UnclusteredEn"]

    #Generate path structure as base_path/iso/systematic, see util_scripts
    #If you have a different structure, change paths manually
    base_path = "~/single_top/stpol/out_step3_06_01"
    #base_path = "~liis/SingleTopJoosep/stpol/out_step3_05_31_18_43/mu"
    paths = generate_paths(systematics, base_path)
    dataGroup = dgDataMuons 
    QCDGroup = None#dgQCDMu
    MCGroups = MC_groups_noQCD_AllExclusive
    openedFiles = open_all_data_files(dataGroup, MCGroups, QCDGroup, paths)
    
    syst_type = ["Up", "Down"]

    stacks =  {}
    #Iso region
    for s in systematics:
      if s == "Nominal":
         stack = make_stack(var, cuts.name, MCGroups, dataGroup, openedFiles, s, "iso", lumis, cuts.isoCutsMC, cuts.isoCutsData, "", cuts.name)
         stacks[var.name+s+"iso"] = stack
      else:
         for st in syst_type:
            stack = make_stack(var, cuts.name, MCGroups, dataGroup, openedFiles, s+st, "iso", lumis, cuts.isoCutsMC, cuts.isoCutsData, "", cuts.name)
            stacks[var.name+s+st+"iso"] = stack

    
    #Anti-iso region
    for s in systematics:
      if s == "Nominal":
         make_histogram(var, dataGroup, cuts.name, openedFiles, lumis, s, "antiiso", cuts.antiIsoCutsData)

         stack = make_stack(var, cuts.name+s, MCGroups, dataGroup, openedFiles, s, "antiiso", lumis, cuts.antiIsoCutsMC, cuts.antiIsoCutsData, "", cuts.name)
         stacks[var.name+s+"antiiso"] = stack
         
    #print "cuts",cuts.isoCutsData

    tdrstyle.tdrstyle()
    cst = TCanvas("Histogram","Jet Systematics in final selection",10,10,1000,1000)

    lumibox = lumi_textbox(lumi_iso["mu"])    
    histos = []

    hData=dataGroup.getHistogram(var, "Nominal", "iso"+cuts.name)
    #hQCDShapeOrig = dataGroup.getHistogram(var, "Nominal", "antiiso")
    hData.Draw("e1")
    hData.SetMarkerStyle(20)
    hData.SetAxisRange(0,1000,"Y")
    stackSys = THStack("Stacksys", "stackName")
    for s in systematics:
      if s == "Nominal":
         stackNom = stacks[var.name+s+"iso"]
      else:
         for st in syst_type:
            stack = stacks[var.name+s+st+"iso"]              
            h1 = TH1D(var.shortName+"_"+s+st, var.shortName+" "+s+st, var.bins, var.lbound, var.ubound)
            if st == "Up":            
                h1.SetMarkerStyle(22)
            else:
                h1.SetMarkerStyle(23)
            if s == "En":
                h1.SetLineColor(kBlue)
            elif s == "UnclusteredEn":
                h1.SetLineColor(kCyan)
            elif s == "Res":
                h1.SetLineColor(kMagenta)
            for h in stack.GetHists():
                h.SetLineColor(kBlack)
                h1.Add(h)                
                #h1.Draw("same hist")
            histos.append(h1)
            stackSys.Add(h1)
    
    hQCD = dataGroup.getHistogram(var, "Nominal", "antiiso")
    hQCD.SetTitle("QCD")
    hQCD.SetFillColor(kGray)
               
    #Subtract MC-s from QCD data template
    stackAI = stacks[var.name+"Nominalantiiso"]
    for h in stackAI.GetHists():
         hQCD.Add(h,-1)
    hQCD.Scale(QCD_YIELD/hQCD.Integral())
    for h in histos:
        h.Add(hQCD)
    #stack.Add(hQCD)
    #stack.Draw("same hist")
    stack = reorder_stack(var, stackNom, hQCD)
    stack.Draw("hist same")
    for h in histos:
        h.Draw("same *h")   

    hData.Draw("e1 same")
    #Draws the lumi box
    from plots.common.utils import lumi_textbox
    lumibox = lumi_textbox(lumi_iso["mu"], "top-right")
    
    stacks_d = OrderedDict() #<<< need to use OrderedDict to have data drawn last (dict does not preserve order)
    stacks_d["sys"] = histos
    stacks_d["mc"] = list(reversed(stack.GetHists()))
    stacks_d["data"] = [hData]
    #print stacks_d
    #Draw the legend
    
    leg_histos = [hData]
    leg_histos.extend(histos)
    leg_histos.extend(list(reversed(stack.GetHists())))
    from plots.common.legend import legend
    leg = legend(
        leg_histos,# <<< need to reverse MC order here, mc3 is top-most
        pos="top-left",
        styles=["p", "pl", "pl", "pl", "pl", "pl", "pl", "f"],
        width=0.2,
        text_size=0.015
    )

    filename = "plots/systematics_stack"
    cst.SaveAs(filename+".png")
    cst.SaveAs(filename+".pdf")
    #return cst
