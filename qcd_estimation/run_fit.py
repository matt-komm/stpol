import os
from Variable import *
from DataLumiStorage import *
from init_data import *
from util_scripts import *
from Fit import Fit
from make_input_histos import make_histos_with_cuts
from fit_with_theta import fit_qcd
from ROOT import TFile
from array import array
import math
from plots.common.cuts import *

try:
    from plots.common.cross_sections import lumi_iso, lumi_antiiso
except Exception as e:
    sys.stderr.write("You need to run `source $STPOL_DIR/setenv.sh` to use the custom python libraries\n")
    raise e

def get_yield(var, filename, cutMT, mtMinValue, fit_result, dataGroup):
    infile = "fits/"+var.shortName+"_fit_"+filename+".root"
    f = TFile(infile)
    hQCD = f.Get(var.shortName+"__qcd")
    hQCDShapeOrig = dataGroup.getHistogram(var, "Nominal", "antiiso")
    hQCDShapeOrig.Scale(hQCD.Integral()/hQCDShapeOrig.Integral())
    err = array('d',[0.])
    bin1 = hQCD.FindBin(mtMinValue)
    bin2 = hQCD.GetNbinsX() + 1
    error = array('d',[0.])
    y = hQCD.IntegralAndError(bin1,bin2,error)
    #no error??
    error[0] = math.sqrt(fit_result.qcd_uncert**2 * y /fit_result.qcd)
    print "QCD yield from original shape:", hQCDShapeOrig.IntegralAndError(bin1,bin2,err), "+-",err, " - use only in fit regions not covering whole mT/MET"
    result = {}
    result["mt"] = (y, error[0])
    print "QCD yield from original shape, no M_T/MET cut,", hQCDShapeOrig.IntegralAndError(0, 100, err), "+-",err, " - use only in fit regions not covering whole mT/MET"
    result["nomt"] = (fit_result.qcd, fit_result.qcd_uncert)
    return result

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

def getMtMinValue(channel):
    if channel == "mu":
        #cutMT = True
        mtMinValue = 50.01 # M_T>50
    elif channel == "ele":
        #cutMT = True
        mtMinValue = 45.01 # MET>45
    return mtMinValue

def get_qcd_yield_with_selection(cuts, cutMT=True, channel = "mu", base_path=(os.environ["STPOL_DIR"] + "/step3_latest/"), do_systematics=False, doSystematicCuts = None):

    print "QCD estimation in " + channel + " channel"

    #Specify variable on which to fit
    if channel == "mu":
        var = Variable("mt_mu", 0, 200, 20, "mtwMass", "m_{T }")
    elif channel == "ele":
        var = Variable("met", 0, 200, 40, "MET", "MET")
    else:
        raise ValueError("channel must be 'mu' or 'ele': %s" % channel)

    #Do you want to get the resulting yield after a cut on the fitted variable?
    #If yes, specify minumum value for the variable the cut. Obviously change to MET for electrons
    #Remember that the cut should be on the edge of 2 bins, otherwise the result will be inaccurate


    mtMinValue = getMtMinValue(channel)

    #Use Default cuts for final selection. See FitConfig for details on how to change the cuts.

    if channel == "ele":
        cuts.setTrigger(str(Cuts.hlt_isoele))
        cuts.setIsolationCut(str(Cuts.electron_iso))
        lepton_weight = "*electron_TriggerWeight*electron_IDWeight"
        if not doSystematicCuts: # switch off in case doing systematic checks with different isolation regions
            cuts.setAntiIsolationCut(str(Cuts.electron_antiiso))
            cuts.setAntiIsolationCutUp(str(Cuts.electron_antiiso_up)) # check +-10% variation
            cuts.setAntiIsolationCutDown(str(Cuts.electron_antiiso_down))
    elif channel == "mu":
        lepton_weight = "*muon_TriggerWeight*muon_IsoWeight*muon_IDWeight"
        #cuts.setTrigger("1")
    
    cuts.setFinalCutsAntiIso("1") #remove top mass and eta cuts from template

    cuts.setWeightMC(str(Weights.total_weight(channel)))
    cuts.setWeightQCD("pu_weight"+lepton_weight)

    #Recreate all necessary cuts after manual changes
    cuts.calcCuts()
    #Luminosities for each different set of data have to be specified.
    #Now only for iso and anti-iso. In the future additional ones for systematics.
    #See DataLumiStorage for details if needed
    print cuts
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
    paths = generate_paths(systematics, base_path, channel)
    #For example:
    #paths["iso"]["Nominal"] = base_path+"/iso/nominal/"
    #paths["antiiso"]["Nominal"] = base_path+"/antiiso/nominal/"
    #Then open files
    print "opening data and MC files"
    openedFiles = open_all_data_files(dataGroup, MCGroups, QCDGroup, paths)

    #Before Running make sure you have 'templates' and 'fits' subdirectories where you're running
    #Root files with templates and fit results will be saved there.
    #Name from FitConfig will be used in file names
    (a, b) = get_qcd_yield_with_fit(var, cuts, cutMT, mtMinValue, dataGroup, lumis, MCGroups, systematics, openedFiles, useMCforQCDTemplate, QCDGroup)
    return (a,b)

