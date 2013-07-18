#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys,os

try:
    from theta_auto import *
except Exception as e:
    sys.stderr.write("You need a working version of theta in your PATH. See the script $STPOL_DIR/setup/install_theta.sh and $STPOL_DIR/setenv.sh.\n")
    raise e

from ROOT import *

from make_input_histos import *
from fit_with_theta import fit_qcd
from plot_fit import *
from FitConfig import FitConfig
from util_scripts import *
from DataLumiStorage import *

try:
    from plots.common.cross_sections import lumi_iso, lumi_antiiso
except Exception as e:
    sys.stderr.write("You need to run `source $STPOL_DIR/setenv.sh` to use the custom python libraries\n")
    raise e

def get_yield(var, filename, cutMT, mtMinValue, fit_result, dataGroup):
    infile = "fits/"+var.shortName+"_fit_"+filename+".root"
    f = TFile(infile)
    #QCDRATE = fit_result.qcd
    hQCD = f.Get(var.shortName+"__qcd")
    hQCDShapeOrig = dataGroup.getHistogram(var, "Nominal", "antiiso")
    print "QCD scale factor:", hQCD.Integral()/hQCDShapeOrig.Integral(), hQCD.Integral(), hQCDShapeOrig.Integral()
    hQCDShapeOrig.Scale(hQCD.Integral()/hQCDShapeOrig.Integral())
    #print fit_result
    if cutMT:
        bin1 = hQCD.FindBin(mtMinValue)
        bin2 = hQCD.GetNbinsX() + 1
        #print hQCD.Integral(), y.Integral()
        error = array('d',[0.])
        err = array('d',[0.])
        y = hQCD.IntegralAndError(bin1,bin2,error)
        print "QCD yield from original shape:", hQCDShapeOrig.IntegralAndError(bin1,bin2,err), "+-",err, " - use only in fit regions not covering whole mT/MET"
        return (y, error[0])
        #return (hQCD.Integral(6,20), hQCD.Integral(6,20)*(fit_result.qcd_uncert/fit_result.qcd))
    else:
        print "QCD yield from original shape:", hQCDShape.IntegralAndError(0,100,err), "+-",err, " - use only in fit regions not covering whole mT/MET"
        return (hQCD.Integral(), hQCD.Integral()*(fit_result.qcd_uncert/fit_result.qcd))

def get_qcd_yield(var, cuts, cutMT, mtMinValue, dataGroup, lumis, MCGroups, systematics, openedFiles, useMCforQCDTemplate, QCDGroup):
    (y, fit) = get_qcd_yield(var, cuts, cutMT, mtMinValue, dataGroup, lumis, MCGroups, systematics, openedFiles, mtMinValue, useMCforQCDTemplate, QCDGroup)
    return y

def get_qcd_yield_with_fit(var, cuts, cutMT, mtMinValue, dataGroup, lumis, MCGroups, systematics, openedFiles, useMCforQCDTemplate, QCDGroup):
    fit = Fit()
    make_histos_with_cuts(var, cuts, dataGroup, MCGroups, systematics, lumis, openedFiles, fit, mtMinValue, useMCforQCDTemplate, QCDGroup)
    fit_qcd(var, cuts.name, fit)
    dataHisto = dataGroup.getHistogram(var,  "Nominal", "iso", cuts.name)
    fit.var = var
    fit.dataHisto = dataHisto
    return (get_yield(var, cuts.name, cutMT, mtMinValue, fit, dataGroup), fit)


def get_qcd_yield_with_selection(cuts, channel = "mu", base_path="$STPOL_DIR/step3_new/", do_systematics=False):
#    do_systematics = True
#
#    if channel == "ele":
#        do_systematics = False
#
    print "QCD estimation in " + channel + " channel"

    #Specify variable on which to fit
    if channel == "mu":
        var = Variable("mt_mu", 0, 200, 20, "mtwMass", "m_{T }")
    elif channel == "ele":
        var = Variable("met", 0, 200, 40, "MET", "MET")
    else:
        raise ValueError("channel must be 'mu' or 'ele': %s" % channel)
    base_path = base_path + channel + "/"

    #Do you want to get the resulting yield after a cut on the fitted variable?
    #If yes, specify minumum value for the variable the cut. Obviously change to MET for electrons
    #Remember that the cut should be on the edge of 2 bins, otherwise the result will be inaccurate

    if channel == "mu":
        cutMT = True
        mtMinValue = 50.01 # M_T>50
    elif channel == "ele":
        cutMT = True
        mtMinValue = 45.01 # MET>45

    #Use Default cuts for final selection. See FitConfig for details on how to change the cuts.


    if channel == "ele":
        cuts.setTrigger("1") #  || HLT_Ele27_WP80_v9==1 || HLT_Ele27_WP80_v8==1")
        cuts.setIsolationCut("el_mva > 0.9 & el_reliso < 0.1")
        cuts.setAntiIsolationCut("el_reliso > 0.1 & el_reliso < 0.5")
        cuts.setAntiIsolationCutUp("el_reliso > 0.11 & el_reliso < 0.55") # check +-10% variation
        cuts.setAntiIsolationCutDown("el_reliso > 0.09 & el_reliso < 0.45")
        lepton_weight = "*electron_triggerWeight*electron_IDWeight"
    elif channel == "mu":
        lepton_weight = "*muon_TriggerWeight*muon_IsoWeight*muon_IDWeight"
        #cuts.setTrigger("1")

    cuts.setWeightMC("pu_weight*b_weight_nominal"+lepton_weight)
    #Recreate all necessary cuts after manual changes
    cuts.calcCuts()
    #Luminosities for each different set of data have to be specified.
    #Now only for iso and anti-iso. In the future additional ones for systematics.
    #See DataLumiStorage for details if needed

    if channel == "mu":
        dataLumiIso = lumi_iso["mu"]
        dataLumiAntiIso = lumi_antiiso["mu"]

    if channel == "ele":
        dataLumiIso = lumi_iso["ele"]
        dataLumiAntiIso = lumi_antiiso["ele"]

    lumis = DataLumiStorage(dataLumiIso, dataLumiAntiIso)

    #Different groups are defined in init_data. Select one you need or define a new one.
    if channel == "mu":
        dataGroup = dgDataMuons
    if channel == "ele":
        dataGroup = dgDataElectrons

    #MC Default is a set muon specific groups with inclusive t-channel for now. MC Groups are without QCD
    #MCGroups = MC_groups_noQCD_InclusiveTCh
    MCGroups = MC_groups_noQCD_AllExclusive

    #Do you want to get QCD template from MC?
    useMCforQCDTemplate = False

    #QCD MC group from init_data
    QCDGroup = None #can change to dgQCDMu, for example

    #Open files
    if do_systematics:
        systematics = ["Nominal", "En", "Res", "UnclusteredEn"]
    else:
        systematics = ["Nominal"]

    #Generate path structure as base_path/iso/systematic, see util_scripts
    #If you have a different structure, change paths manually
    paths = generate_paths(systematics, base_path)
    #For example:
    paths["iso"]["Nominal"] = base_path+"/iso/nominal/"
    paths["antiiso"]["Nominal"] = base_path+"/antiiso/nominal/"
    #Then open files
    print "opening data and MC files"
    openedFiles = open_all_data_files(dataGroup, MCGroups, QCDGroup, paths)

    #Before Running make sure you have 'templates' and 'fits' subdirectories where you're running
    #Root files with templates and fit results will be saved there.
    #Name from FitConfig will be used in file names

    return get_qcd_yield_with_fit(var, cuts, cutMT, mtMinValue, dataGroup, lumis, MCGroups, systematics, openedFiles, useMCforQCDTemplate, QCDGroup)

if __name__=="__main__":
    try:
        sys.path.append(os.environ["STPOL_DIR"] )
    except KeyError as e:
        print "Could not find the STPOL_DIR environment variable, did you run `source setenv.sh` in the code base directory?"
        raise e

    if "theta-auto.py" not in sys.argv[0]:
        raise Exception("Must run as `$STPOL_DIR/theta/utils2/theta-auto.py get_qcd_yield.py`")

    cuts_final = FitConfig( "final_selection", trigger="1.0")
    cuts_2j0t = FitConfig( "2j0t_selection", trigger="1.0")
    cuts_mva = FitConfig( "mva_selection", trigger="1.0")
    cuts_mva.setFinalCuts("1")
    cuts_2j0t.setBaseCuts("n_jets == 2 && n_tags == 0 && n_veto_mu==0 && n_veto_ele==0")
    cuts_final_without_eta = FitConfig( "final_selection_without_eta_cut", trigger="1.0")
    cuts_final_without_eta.setFinalCuts("top_mass < 220 && top_mass > 130")

    cuts = {}
    cuts["final"] = cuts_final
    cuts["2j0t"] = cuts_2j0t
    cuts["final_without_eta"] = cuts_final_without_eta
    cuts["mva"] = cuts_mva
    
    #Remove the name of this script from the argument list in order to not confuse ArgumentParser
    try:
        sys.argv.pop(sys.argv.index("get_qcd_yield.py"))
    except ValueError:
        pass
    import argparse
    parser = argparse.ArgumentParser(description='Does the QCD fit using theta-auto')
    parser.add_argument('--lepton', dest='lepton', choices=["mu", "ele"], required=True, help="The lepton channel used for the fit")
    parser.add_argument('--cut', dest='cut', choices=cuts.keys(), required=True, help="The cut region to use in the fit")
    parser.add_argument('--doSystematics', dest='doSystematics', action="store_true", default=False)
    args = parser.parse_args()

    cut = cuts[args.cut]
    ((y, error), fit) = get_qcd_yield_with_selection(cut, args.lepton, do_systematics=args.doSystematics)
    print "Selection: %s" % cut.name
    print "QCD yield in selected region: %.2f +- %.2f, ratio to template from ONLY data %.3f" % (y, error, y/fit.orig["qcd_no_mc_sub"])
    print "Total: QCD: %.2f +- %.2f, ratio to template from data %.3f" % (fit.qcd, fit.qcd_uncert, fit.qcd/fit.orig["qcd"])
    print "W+Jets: %.2f +- %.2f, ratio to template: %.2f" % (fit.wjets, fit.wjets_uncert, fit.wjets/fit.wjets_orig)
    print "Other MC: %.2f +- %.2f, ratio to template: %.2f" % (fit.nonqcd, fit.nonqcd_uncert, fit.nonqcd/fit.nonqcd_orig)

    print "Fit info:"
    print fit
    plot_fit(fit.var, cut, fit.dataHisto, fit)
