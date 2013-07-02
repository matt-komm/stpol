#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys,os
from theta_auto import *

from make_input_histos import *
from fit_with_theta import fit_qcd
from plot_fit import plot_fit
from FitConfig import *
from DataLumiStorage import *
from get_qcd_yield import *

def select_cuts():
    cuts = []
    cutsFinal = FitConfig("2J_1T_SR")
    cuts.append(cutsFinal)

    cutsSB = FitConfig("2J_1T_SB")
    cutsSB.setFinalCuts("abs(eta_lj)>2.5 && (top_mass > 220 || top_mass < 130)")
    cutsSB.calcCuts()
    cuts.append(cutsSB)

    cuts2J1T = FitConfig("2J_1T")
    cuts2J1T.setFinalCuts("abs(eta_lj)>2.5")
    cuts2J1T.calcCuts()
    cuts.append(cuts2J1T)

    cutsMtwMass50 = FitConfig("2J_1T_m_T_50minus")
    cutsMtwMass50.setFinalCuts("abs(eta_lj)>2.5 && top_mass < 220 && top_mass > 130 && mt_mu < 50")
    cutsMtwMass50.calcCuts()
    cuts.append(cutsMtwMass50)

    cutsMtwMass70 = FitConfig("2J_1T_m_T_70minus")
    cutsMtwMass70.setFinalCuts("abs(eta_lj)>2.5 && top_mass < 220 && top_mass > 130 && mt_mu < 70")
    cutsMtwMass70.calcCuts()
    cuts.append(cutsMtwMass70)

    cutsMtwMass20plus = FitConfig("2J_1T_m_T_20plus")
    cutsMtwMass20plus.setFinalCuts("abs(eta_lj)>2.5 && top_mass < 220 && top_mass > 130 && mt_mu > 20")
    cutsMtwMass20plus.calcCuts()
    cuts.append(cutsMtwMass20plus)

    cuts_iso_0_3_plus = FitConfig("2J_1T_SR_iso_0_3_plus")
    cuts_iso_0_3_plus.setAntiIsolationCut("mu_iso>0.3")
    cuts_iso_0_3_plus.setAntiIsolationCutUp("mu_iso>0.33")
    cuts_iso_0_3_plus.setAntiIsolationCutDown("mu_iso>0.27")
    cuts_iso_0_3_plus.calcCuts()
    cuts.append(cuts_iso_0_3_plus)

    cuts_iso_0_5_plus = FitConfig("2J_1T_SR_iso_0_5_plus")
    cuts_iso_0_5_plus.setAntiIsolationCut("mu_iso>0.5")
    cuts_iso_0_5_plus.setAntiIsolationCutUp("mu_iso>0.55")
    cuts_iso_0_5_plus.setAntiIsolationCutDown("mu_iso>0.45")
    cuts_iso_0_5_plus.calcCuts()
    cuts.append(cuts_iso_0_5_plus)

    cuts_iso_0_2_to_0_5 = FitConfig("2J_1T_SR_iso_0_22_to_0_5")
    cuts_iso_0_2_to_0_5.setAntiIsolationCut("mu_iso>0.22 && mu_iso<0.5")
    cuts_iso_0_2_to_0_5.setAntiIsolationCutUp("mu_iso>0.242 && mu_iso<0.55")
    cuts_iso_0_2_to_0_5.setAntiIsolationCutDown("mu_iso>0.2 && mu_iso<0.45")
    cuts_iso_0_2_to_0_5.calcCuts()
    cuts.append(cuts_iso_0_2_to_0_5)

    """cuts2J0T = FitConfig("2J_0T_SR")
    cuts2J0T.setBaseCuts("n_jets == 2 && n_tags == 0")
    cuts2J0T.calcCuts()
    cuts.append(cuts2J0T)"""
    """cutsMC = FitConfig("2J_1T_SR_MC")
    cutsMC.isMC = True
    cuts.append(cutsMC)
    """

    return cuts

def do_fit(var,fit, systematics, open_files):
   make_histos(var, fit, systematics, open_files)
   qcd_yield=fit_qcd(fit)
   print fit.getLabel(), "yield:", qcd_yield
   print fit.result



if __name__=="__main__":
    raise Expcetion("This file is not supposed to be run, superseded by get_qcd_yield.py!")
#    channel = "ele"
    channel = "mu"

    print "QCD estimation in " + channel + " channel"

    #Specify variable on which to fit
    if channel == "mu":
        var = Variable("mt_mu", 0, 200, 20, "mtwMass", "m_{T }")
    elif channel == "ele":
        var = Variable("met", 0, 200, 20, "MET", "MET")
    else:
        print "Set either 'ele' or 'mu' as channel"
        sys.exit(1)

    #Do you want to get the resulting yield after a cut on the fitted variable?
    cutMT = True
    #If yes, specify minumum value for the variable the cut. Obviously change to MET for electrons
    #Remember that the cut should be on the edge of 2 bins, otherwise the result will be inaccurate
    mtMinValue = 50.01 # M_T>50

    #Use Default cuts for final selection. See FitConfig for details on how to change the cuts.
    cuts = FitConfig("final_selection")
    #For example:

    #Recreate all necessary cuts after manual changes
    cuts.calcCuts()

    dataLumiIso = 19739
    dataLumiAntiIso = 19739
    lumis = DataLumiStorage(dataLumiIso, dataLumiAntiIso)

    dataGroup = dgDataMuons

    #MC Default is a set muon specific groups with inclusive t-channel for now. MC Groups are without QCD
    #MCGroups = MC_groups_noQCD_InclusiveTCh
    MCGroups = MC_groups_noQCD_AllExclusive

    #QCD MC group from init_data
    QCDGroup = None#dgQCDMu #can change to dgQCDMu, for example

    #Open files
    systematics = ["Nominal", "En", "Res", "UnclusteredEn"]
    #Generate path structure as base_path/iso/systematic, see util_scripts
    #If you have a different structure, change paths manually

    base_path = "/home/andres/single_top/stpol/out_step3_06_01"

    paths = generate_paths(systematics, base_path)
    #For example:
    paths["iso"]["Nominal"] = base_path+"/iso/Nominal/"
    paths["antiiso"]["Nominal"] = base_path+"/antiiso/Nominal/"
    #Then open files
    print "opening data and MC files"
    openedFiles = open_all_data_files(dataGroup, MCGroups, QCDGroup, paths)

    cutconfs = select_cuts()
    canvases = []
    for cuts in cutconfs:
        #cuts.setTrigger("1")
        cuts.calcCuts()
        print cuts
        ((y, error), fit) = get_qcd_yield_with_fit(var, cuts, cutMT, mtMinValue, dataGroup, lumis, MCGroups, systematics, openedFiles, cuts.isMC, QCDGroup)
        #print cuts
        print "Selection: %s" % cuts.name
        print "QCD yield in selected region: ", y, "+-", error
        print "Total: QCD: %.2f +- %.2f" % (fit.qcd, fit.qcd_uncert)
        print "W+Jets: %.2f +- %.2f, ratio to template: %.2f" % (fit.wjets, fit.wjets_uncert, fit.wjets/fit.wjets_orig)
        print "Other MC: %.2f +- %.2f, ratio to template: %.2f" % (fit.nonqcd, fit.nonqcd_uncert, fit.nonqcd/fit.nonqcd_orig)

        print fit
        #clear_histos(data_group, mc_groups)
        dataHisto = dataGroup.getHistogram(var,  "Nominal", "iso", cuts.name)
        canvases.append(plot_fit(var, cuts, dataHisto, fit))
        clear_histos(dataGroup, MCgroups)
