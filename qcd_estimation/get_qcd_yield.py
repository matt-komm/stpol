#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys,os
from theta_auto import *
from ROOT import *

from make_input_histos import *
from fit_with_theta import fit_qcd
from plot_fit import plot_fit
from FitConfig import FitConfig
from util_scripts import *
from DataLumiStorage import *

def get_yield(var, filename, cutMT, mtMinValue, fit_result):
    infile = "fits/"+var.shortName+"_fit_"+filename+".root"
    f = TFile(infile)
    #QCDRATE = fit_result.qcd
    hQCD = f.Get(var.shortName+"__qcd")
    #print fit_result
    if cutMT:
        bin1 = hQCD.FindBin(mtMinValue)
        bin2 = hQCD.GetNbinsX() + 1
        #print hQCD.Integral(), y.Integral()
        error = array('d',[0.])
        y = hQCD.IntegralAndError(bin1,bin2,error)
        return (y, error[0])
        #return (hQCD.Integral(6,20), hQCD.Integral(6,20)*(fit_result.qcd_uncert/fit_result.qcd))
    else:
        return (hQCD.Integral(), hQCD.Integral()*(fit_result.qcd_uncert/fit_result.qcd))

def get_qcd_yield(var, cuts, cutMT, mtMinValue, dataGroup, lumis, MCGroups, systematics, openedFiles, useMCforQCDTemplate, QCDGroup):
    fit = Fit()
    make_histos_with_cuts(var, cuts, dataGroup, MCGroups, systematics, lumis, openedFiles, useMCforQCDTemplate, QCDGroup)
    fit_qcd(var, cuts.name, fit)
    return get_yield(var, cuts.name, cutMT, mtMinValue, fit)

#Run as ~andres/theta_testing/utils2/theta-auto.py get_qcd_yield.py
if __name__=="__main__":
    #Specify variable on which to fit
    var = Variable("mt_mu", 0, 200, 20, "mtwMass", "m_{T }")

    #Do you want to get the resulting yield after a cut on the fitted variable?
    cutMT = True
    #If yes, specify minumum value for the variable the cut. Obviously change to MET for electrons
    #Remember that the cut should be on the edge of 2 bins, otherwise the result will be inaccurate
    mtMinValue = 50. # M_T>50

    #Use Default cuts for final selection. See FitConfig for details on how to change the cuts.
    cuts = FitConfig("final_selection")
    #For example:
    cuts.setWeightMC("pu_weight*muon_IDWeight*muon_TriggerWeight*muon_IsoWeight*b_weight_nominal")
    from plots.common.cuts import Cuts
    cuts.setBaseCuts(str(Cuts.mu*Cuts.final(2,1)))
    #Recreate all necessary cuts after manual changes
    cuts.calcCuts()

    #Luminosities for each different set of data have to be specified.
    #Now only for iso and anti-iso. In the future additional ones for systematics.
    #See DataLumiStorage for details if needed

    lumiABIso = 5306
    lumiCIso = 6781
    lumiDIso = 7274
    dataLumiIso = lumiABIso + lumiCIso + lumiDIso
    lumiABAntiIso = 5306
    lumiCAntiIso = 6781
    lumiDAntiIso = 7274
    dataLumiAntiIso = lumiABAntiIso + lumiCAntiIso + lumiDAntiIso

    lumis = DataLumiStorage(dataLumiIso, dataLumiAntiIso)

    #Different groups are defined in init_data. Select one you need or define a new one.
    dataGroup = dgDataMuons

    #MC Default is a set muon specific groups with inclusive t-channel for now. MC Groups are without QCD
    MCGroups = MC_groups_noQCD_InclusiveTCh

    #Do you want to get QCD template from MC?
    useMCforQCDTemplate = False

    #QCD MC group from init_data
    QCDGroup = None #can change to dgQCDMu, for example

    #Open files
    systematics = ["Nominal"] #Systematics to be added in the future
    #Generate path structure as base_path/iso/systematic, see util_scripts
    #If you have a different structure, change paths manually
    base_path = "~/Documents/stpol/data/out_step3_05_27_13_58/"
    paths = generate_paths(systematics, base_path)
    #For example:
    paths["iso"]["Nominal"] = base_path+"/iso/nominal/"
    paths["antiiso"]["Nominal"] = base_path+"/antiiso/nominal/"
    #Then open files
    openedFiles = open_all_data_files(dataGroup, MCGroups, QCDGroup, paths)

    #Before Running make sure you have 'templates' and 'fits' subdirectories where you're running
    #Root files with templates and fit results will be saved there.
    #Name from FitConfig will be used in file names
    (y, error) = get_qcd_yield(var, cuts, cutMT, mtMinValue, dataGroup, lumis, MCGroups, systematics, openedFiles, useMCforQCDTemplate, QCDGroup)

    print "QCD yield with selection: %s" % cuts.name
    print y, "+-", error
