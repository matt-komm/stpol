#!/usr/bin/python
# -*- coding: utf-8 -*-

from ROOT import *
from cuts import *
from plotting import *


def make_histos_with_cuts(var,
        cuts,
        dataGroup,
        MCGroups,
        systematics,
        lumis, 
        openedFiles,
        fit,
        mtMinValue,
        useMCforQCDTemplate = False,
        QCDGroup = dgQCDMu):

   QCD_FACTOR = 1000000.
    
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
         if useMCforQCDTemplate:
            make_histogram(var, QCDGroup, cuts.name, openedFiles, lumis, s, "antiiso", cuts.antiIsoCutsQCD)                    
         make_histogram(var, dataGroup, cuts.name, openedFiles, lumis, s, "antiiso", cuts.antiIsoCutsData)

         stack = make_stack(var, cuts.name+s, MCGroups, dataGroup, openedFiles, s, "antiiso", lumis, cuts.antiIsoCutsMC, cuts.antiIsoCutsData, "", cuts.name)
         stacks[var.name+s+"antiiso"] = stack
         
         #Iso down
         if useMCforQCDTemplate:
            make_histogram(var, QCDGroup, cuts.name+"iso down", openedFiles, lumis, s, "antiiso", cuts.antiIsoCutsQCDIsoDown, "_iso_down_")
         stack = make_stack(var, cuts.name+s+"iso down", MCGroups, dataGroup, openedFiles, s, "antiiso", lumis,  
                        cuts.antiIsoCutsMCIsoDown, cuts.antiIsoCutsDataIsoDown, "", "_iso_down_"+cuts.name)
         stacks[var.name+s+"antiiso"+"_iso_down"] = stack

         #Iso Up
         if useMCforQCDTemplate:
            make_histogram(var, QCDGroup, cuts.name+"iso up", openedFiles, lumis, s, "antiiso", cuts.antiIsoCutsQCDIsoUp, "_iso_up_")
         stack = make_stack(var, cuts.name+s+"iso up", MCGroups, dataGroup, openedFiles, s, "antiiso", lumis, 
                        cuts.antiIsoCutsMCIsoUp, cuts.antiIsoCutsDataIsoUp, "", "_iso_up_"+cuts.name)
         stacks[var.name+s+"antiiso"+"_iso_up"] = stack
         
                    
   #Write out stuff 
   outfile = TFile("templates/"+var.shortName+"_templates_"+cuts.name+".root", "recreate")
   outfile.cd()
   fit.orig = {}      
   #non-QCD
   for s in systematics:
      if s == "Nominal":
         stack = stacks[var.name+s+"iso"]
         h1 = TH1D(var.shortName+"__nonqcd", var.shortName+"__nonqcd", var.bins, var.lbound, var.ubound)
         hWJ = TH1D(var.shortName+"__wjets", var.shortName+"__wjets", var.bins, var.lbound, var.ubound)
         for h in stack.GetHists():
            if h.GetName().startswith("W+Jets"):
                hWJ.Add(h)            
            else:
                h1.Add(h)
         h1.Write()
         hWJ.Write()
         print "MC integral", h1.Integral()
         print "W+Jets integral", hWJ.Integral()
         fit.wjets_orig = hWJ.Integral()
         fit.nonqcd_orig = h1.Integral()
      else:
         for st in syst_type:
            if st == "Up":
               syst_string = "__"+s+"__plus"
            else:
               syst_string = "__"+s+"__minus"
            stack = stacks[var.name+s+st+"iso"]
            h1 = TH1D(var.shortName+"__nonqcd"+syst_string, var.shortName+"__nonqcd"+syst_string, var.bins, var.lbound, var.ubound)   
            hWJ = TH1D(var.shortName+"__wjets"+syst_string, var.shortName+"__wjets"+syst_string, var.bins, var.lbound, var.ubound)
            for h in stack.GetHists():
                if h.GetName().startswith("W+Jets"):
                    hWJ.Add(h)            
                else:
                    h1.Add(h)
            h1.Write()
            hWJ.Write()
   #Data
   #print dataGroup._histograms
   hData = dataGroup.getHistogram(var, "Nominal", "iso", cuts.name)
   hData.SetName(var.shortName+"__DATA")
   print "data integral", hData.Integral()
   hData.Write()
         
   #QCD
   fit.orig_shape = {}
   if useMCforQCDTemplate:
      for s in systematics:
         if s == "":
            hQCD = QCDGroup.getHistogram(var, s, "antiiso")
            hQCD.SetName(var.shortName+"__qcd")
            print "QCD Integral", hQCD.GetEntries(), hQCD.Integral()
            hQCD.Write()
            hQCDisoUp = QCDGroup.getHistogram(var, s, "antiiso", "_iso_plus")
            hQCDisoDown = QCDGroup.getHistogram(var, s, "antiiso", "_iso_minus")
         else:
            for st in syst_type:
               if st == "Up":
                  syst_string = "__"+s+"__plus"
               else:
                  syst_string = "__"+s+"__minus"
               hQCD = QCDGroup.getHistogram(var, s+st+"antiiso")
               hQCD.SetName(var.shortName+"__qcd"+syst_string)
               print "QCD integral "+s+st, hQCD.Integral()
               hQCD.Write()

   else:    #QCD template is from data
      hQCD = dataGroup.getHistogram(var, "Nominal", "antiiso")
      hQCD.SetName(var.shortName+"__qcd")
      hQCDisoUp = dataGroup.getHistogram(var, "Nominal", "antiiso", "_iso_up_"+cuts.name)
      hQCDisoDown = dataGroup.getHistogram(var, "Nominal", "antiiso", "_iso_down_"+cuts.name)

      bin1 = hQCD.FindBin(mtMinValue)
      bin2 = hQCD.GetNbinsX() + 1
      fit.orig_shape["qcd_no_mc_sub"] = hQCD.Clone()
      fit.orig_shape["qcd_no_mc_sub"].SetDirectory(0)
      fit.orig["qcd_no_mc_sub"] = hQCD.Integral(bin1, bin2)
      fit.orig["qcd_no_mc_sub_nomtcut"] = hQCD.Integral()
      #Subtract MC-s from QCD data template
      stack = stacks[var.name+"Nominalantiiso"]
      for h in stack.GetHists():
         hQCD.Add(h,-1)
                    
      stack = stacks[var.name+"Nominalantiiso_iso_up"]    
      for h in stack.GetHists():
         hQCDisoUp.Add(h, -1)
                
      stack = stacks[var.name+"Nominalantiiso_iso_down"]                
      for h in stack.GetHists():
         hQCDisoDown.Add(h, -1)
      
      print "QCD integral", hQCD.Integral()   
      fit.orig_shape["qcd"] = hQCD.Clone()
      fit.orig_shape["qcd"].SetDirectory(0)
          
      #Scale template to a large are (then fitted multiplier will be small, which theta likes
      if hQCD.Integral() > 0:
         print "ORIG QCD integral", hQCD.Integral(),hQCD.Integral(bin1,bin2)
         fit.orig["qcd"] = hQCD.Integral(bin1, bin2)
         fit.orig["qcd_nomtcut"] = hQCD.Integral()
         hQCD.Scale(QCD_FACTOR/hQCD.Integral())
      if hQCDisoUp.Integral() > 0:
         hQCDisoUp.Scale(QCD_FACTOR/hQCDisoUp.Integral())
      if hQCDisoDown.Integral() > 0:
         hQCDisoDown.Scale(QCD_FACTOR/hQCDisoDown.Integral())
      hQCD.Write()
      hQCDisoUp.SetName(var.shortName+"__qcd__ISO__plus")
      hQCDisoDown.SetName(var.shortName+"__qcd__ISO__minus")
      print "QCD isoUp integral", hQCDisoUp.GetEntries(), hQCDisoUp.Integral()
      print "QCD isoDown integral", hQCDisoDown.GetEntries(), hQCDisoDown.Integral()
      hQCDisoUp.Write()
      hQCDisoDown.Write()
   
   outfile.Write()   
   outfile.Close()



def make_histos_for_final_fit(var,
        cuts,
        dataGroup,
        MCGroups,
        systematics,
        lumis, 
        openedFiles,
        fit,
        qcd_yield,
        QCDGroup = dgQCDMu):

   syst_type = ["Up", "Down"]

   stacks =  {}
   #Iso region
   for s in systematics:
      if s == "Nominal":
         stack = make_stack(var, cuts.name, MCGroups, dataGroup, openedFiles, s, "iso", lumis, cuts.isoCutsMC, cuts.isoCutsData, "", cuts.name, None, True)
         stacks[var.name+s+"iso"] = stack
         print stack
         for h in stack.GetHists():
            print h.GetName(),h.GetTitle()
         
      else:
         for st in syst_type:
            stack = make_stack(var, cuts.name, MCGroups, dataGroup, openedFiles, s+st, "iso", lumis, cuts.isoCutsMC, cuts.isoCutsData, "", cuts.name, None, True)
            stacks[var.name+s+st+"iso"] = stack

   #Anti-iso region
   for s in systematics:
      if s == "Nominal":
         make_histogram(var, dataGroup, cuts.name, openedFiles, lumis, s, "antiiso", cuts.antiIsoCutsData, "",True)

         stack = make_stack(var, cuts.name+s, MCGroups, dataGroup, openedFiles, s, "antiiso", lumis, cuts.antiIsoCutsMC, cuts.antiIsoCutsData, "", cuts.name, None, True)
         stacks[var.name+s+"antiiso"] = stack
         #Iso down
         stack = make_stack(var, cuts.name+s+"iso down", MCGroups, dataGroup, openedFiles, s, "antiiso", lumis,  
                        cuts.antiIsoCutsMCIsoDown, cuts.antiIsoCutsDataIsoDown, "", "_iso_down_"+cuts.name, None, True)
         stacks[var.name+s+"antiiso"+"_iso_down"] = stack

         #Iso Up
         stack = make_stack(var, cuts.name+s+"iso up", MCGroups, dataGroup, openedFiles, s, "antiiso", lumis, 
                        cuts.antiIsoCutsMCIsoUp, cuts.antiIsoCutsDataIsoUp, "", "_iso_up_"+cuts.name, None, True)
         stacks[var.name+s+"antiiso"+"_iso_up"] = stack   
     
   #Write out stuff 
   outfile = TFile("templates/"+var.shortName+"_templates_final_fit.root", "recreate")
   outfile.cd()
           
   #non-QCD
   for s in systematics:
      if s == "Nominal":
         stack = stacks[var.name+s+"iso"]
         fit.orig = {}
         for h in stack.GetHists():
            h.SetName(var.shortName+"__"+h.GetTitle().replace("+", "").replace(" #bar{t}","tbar"))
            h.Write()
            fit.orig[h.GetTitle().replace("+", "").replace(" #bar{t}","tbar")] = h.Integral()
      else:
         for st in syst_type:
            if st == "Up":
               syst_string = "__"+s+"__plus"
            else:
               syst_string = "__"+s+"__minus"
            stack = stacks[var.name+s+st+"iso"]              
            for h in stack.GetHists():
                h.SetName(var.shortName+"__"+h.GetTitle().replace("+", "").replace(" #bar{t}","tbar")+syst_string)
                h.Write()   
    
   #Data
   #print dataGroup._histograms
   hData = dataGroup.getHistogram(var, "Nominal", "iso", cuts.name)
   hData.SetName(var.shortName+"__DATA")
   print "data integral", hData.Integral()
   hData.Write()
         
   hQCD = dataGroup.getHistogram(var, "Nominal", "antiiso")
   hQCD.SetName(var.shortName+"__qcd")
   hQCDisoUp = dataGroup.getHistogram(var, "Nominal", "antiiso", "_iso_up_"+cuts.name)
   hQCDisoDown = dataGroup.getHistogram(var, "Nominal", "antiiso", "_iso_down_"+cuts.name)
               
   #Subtract MC-s from QCD data template
   stack = stacks[var.name+"Nominalantiiso"]
   for h in stack.GetHists():
      hQCD.Add(h,-1)
                    
   #Scale template to a large area (then fitted multiplier will be small, which theta likes
   if hQCD.Integral() > 0:
      hQCD.Scale(qcd_yield/hQCD.Integral())
   
   print "QCD integral", hQCD.Integral()   
   hQCD.Write()
   
   outfile.Write()   
   outfile.Close()

