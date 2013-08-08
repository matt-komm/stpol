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
from plots.common.cuts import Cuts
import logging
import rootpy
from systematics import *
logger = logging.getLogger("get_qcd_yield")

try:
    from plots.common.cross_sections import lumi_iso, lumi_antiiso
except Exception as e:
    sys.stderr.write("You need to run `source $STPOL_DIR/setenv.sh` to use the custom python libraries\n")
    raise e

def get_yield_withMT(histo, mtMinValue):
    bin1 = histo.FindBin(mtMinValue)
    bin2 = histo.GetNbinsX() + 1
    #print hQCD.Integral(), y.Integral()
    error = array('d',[0.])
    y = histo.IntegralAndError(bin1,bin2,error)
    return y

def get_yield(var, filename, cutMT, mtMinValue, fit_result, dataGroup):
    infile = "fits/"+var.shortName+"_fit_"+filename+".root"
    f = TFile(infile)
    #QCDRATE = fit_result.qcd
    hQCD = f.Get(var.shortName+"__qcd")
    hQCDShapeOrig = dataGroup.getHistogram(var, "Nominal", "antiiso")
    #print "QCD scale factor, no m_t cut:", hQCD.Integral()/fit_result.orig["qcd_no_mc_sub"], "from", fit_result.orig["qcd_no_mc_sub"], "to ", hQCD.Integral()
    hQCDShapeOrig.Scale(hQCD.Integral()/hQCDShapeOrig.Integral())
    #print fit_result
    err = array('d',[0.])
    #hQCD.SetDirectory(0)
    #fit_result.isoCut = hQCD.Clone()
    #fit_result.qcd_histo = hQCD.Clone()
    print "ft",fit_result
    print hQCD
    print "QCD", fit_result.qcd_histo
    bin1 = hQCD.FindBin(mtMinValue)
    bin2 = hQCD.GetNbinsX() + 1
    #print hQCD.Integral(), y.Integral()
    error = array('d',[0.])
    y = hQCD.IntegralAndError(bin1,bin2,error)
    #no error??
    error[0] = math.sqrt(fit_result.qcd_uncert**2 * y /fit_result.qcd)
    print "QCD yield from original shape:", hQCDShapeOrig.IntegralAndError(bin1,bin2,err), "+-",err, " - use only in fit regions not covering whole mT/MET"
    result = {}
    result["mt"] = (y, error[0])
    #return (hQCD.Integral(6,20), hQCD.Integral(6,20)*(fit_result.qcd_uncert/fit_result.qcd))
    
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
    print "QCD2", fit.qcd_histo
    #fit.qcd_histo = 
    return (get_yield(var, cuts.name, cutMT, mtMinValue, fit, dataGroup), fit)

def getMtMinValue(channel):
    if channel == "mu":
        #cutMT = True
        mtMinValue = 50.01 # M_T>50
    elif channel == "ele":
        #cutMT = True
        mtMinValue = 45.01 # MET>45
    return mtMinValue

def get_qcd_yield_with_selection(cuts, cutMT=True, channel = "mu", base_path=(os.environ["STPOL_DIR"] + "/step3_latest/"), do_systematics=False):

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
        cuts.setTrigger("(HLT_Ele27_WP80_v8 == 1 || HLT_Ele27_WP80_v9 == 1 || HLT_Ele27_WP80_v10 || HLT_Ele27_WP80_v11)")
        cuts.setIsolationCut("el_iso < 0.1")
        lepton_weight = "*electron_TriggerWeight*electron_IDWeight"
        if not args.doSystematicCuts: # switch off in case doing systematic checks with different isolation regions
            cuts.setAntiIsolationCut("el_iso > 0.15 & el_iso < 0.5")
            cuts.setAntiIsolationCutUp("el_iso > 0.17 & el_iso < 0.55") # check +-10% variation
            cuts.setAntiIsolationCutDown("el_iso > 0.13 & el_iso < 0.45")
    elif channel == "mu":
        lepton_weight = "*muon_TriggerWeight*muon_IsoWeight*muon_IDWeight"
        #cuts.setTrigger("1")
    
    cuts.setFinalCutsAntiIso("1") #remove top mass and eta cuts from template

    cuts.setWeightMC("pu_weight*b_weight_nominal*wjets_mg_flavour_flat_weight*wjets_mg_flavour_shape_weight"+lepton_weight)
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
        systematics = ["Nominal", "En"]
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
    print "QCD2.5",b, b.qcd_histo
    return (a,b)

if __name__=="__main__":
    try:
        sys.path.append(os.environ["STPOL_DIR"] )
    except KeyError as e:
        print "Could not find the STPOL_DIR environment variable, did you run `source setenv.sh` in the code base directory?"
        raise e

    if "theta-auto.py" not in sys.argv[0]:
        raise Exception("Must run as `$STPOL_DIR/theta/utils2/theta-auto.py get_qcd_yield.py`")

    #Create the cuts in a programmatic way
    cuts = {}
    final_cut = Cuts.top_mass_sig * Cuts.eta_lj
    for nj in [2, 3]:
        for nt in [0, 1, 2]:

            #Before eta and top mass cuts. Also for MVA
            c = "%dj%dt" % (nj, nt)
            cuts[c] = FitConfig(c)
            cuts[c].setBaseCuts("n_jets == %d && n_tags == %d && n_veto_ele==0 && n_veto_mu==0" % (nj,nt))
            cuts[c].setFinalCuts("1")

            #Eta Fit cut in Njets, Ntags
            c0 = "fit_%dj%dt" % (nj, nt)
            cuts[c0] = FitConfig(c0)
            cuts[c0].setBaseCuts("n_jets == %d && n_tags == %d && n_veto_ele==0 && n_veto_mu==0" % (nj,nt))
            cuts[c0].setFinalCuts(str(Cuts.top_mass_sig))

            #Final cut in Njets, Ntags
            #This is the _FINAL_ cut, where we show cos_theta
            c1 = "final__%dj%dt" % (nj, nt)
            cuts[c1] = FitConfig(c1)
            cuts[c1].setFinalCuts(
                str(final_cut)
            )
            cuts[c].setBaseCuts("n_jets == %d && n_tags == %d && n_veto_ele==0 && n_veto_mu==0" % (nj,nt))
            

        s = "%dj" % nj
        cuts[s] = FitConfig(s)
        bc = str(Cuts.n_jets(nj)*Cuts.rms_lj*Cuts.lepton_veto)
        cuts[s].setBaseCuts(bc)
        cuts[s].setFinalCuts("1")

        s = "final_%dj" % nj
        cuts[s] = FitConfig(s)
        bc = str(Cuts.n_jets(nj)*Cuts.rms_lj)
        cuts[s].setBaseCuts(bc)
        cuts[s].setFinalCuts(str(final_cut))
    #Remove the name of this script from the argument list in order to not confuse ArgumentParser
    try:
        sys.argv.pop(sys.argv.index("get_qcd_yield.py"))
    except ValueError:
        pass
    import argparse

    parser = argparse.ArgumentParser(description='Does the QCD fit using theta-auto')
    parser.add_argument('--channel', dest='channel', choices=["mu", "ele"], required=True, help="The lepton channel used for the fit")
    parser.add_argument('-c', '--cut',
        dest='cuts', choices=cuts.keys(), required=False, default=None,
        help="The cut region to use in the fit", action='append')
    parser.add_argument('--path', dest='path', default=(os.environ["STPOL_DIR"] + "/step3_latest/"), required=False)
    parser.add_argument('--doSystematics', action="store_true", default=False)
    parser.add_argument('--doSystematicCuts', action="store_true", default=False, help="Various anti-iso regions etc.")

    args = parser.parse_args()

    if args.doSystematicCuts == True and args.channel == "mu":
        cuts = systematics_cuts_mu()
        args.cuts = cuts.keys()
        print "Considering the systematic variations: " + str(args.cuts)
    if args.doSystematicCuts == True and args.channel == "ele":
        cuts = systematics_cuts_ele()
        args.cuts = cuts.keys()
        print "Considering the systematic variations: " + str(args.cuts)
        
    elif not args.cuts: #No cuts specified, do them all
        args.cuts = cuts.keys()

    ofdir = "fitted/" + args.channel
    try:
        os.makedirs(ofdir)
    except:
        pass


    failed = []
    print args.cuts
    for cutn in args.cuts:
        print cutn
        cut = cuts[cutn]
        try:
            (results, fit) = get_qcd_yield_with_selection(cut, True, args.channel, base_path=args.path, do_systematics=args.doSystematics)
        except rootpy.ROOTError:
            failed += [cutn]
            continue
        (y, error) = results["mt"]
        (y_nomtcut, error_nomtcut) = results["nomt"]
        print "FT2", fit
        print "QCD3", fit.qcd_histo
        qcd_sf = y/fit.orig["qcd_no_mc_sub"]
        qcd_sf_nomt = y_nomtcut/fit.orig["qcd_no_mc_sub_nomtcut"]
        
        print "QCD scale factor, with m_t/met cut:", qcd_sf, "from", fit.orig["qcd_no_mc_sub"], "to ", y
        print "QCD scale factor, without m_t/met cut:", qcd_sf_nomt, "from", fit.orig["qcd_no_mc_sub_nomtcut"], "to ", y_nomtcut
        print "Fit information", fit
        print "QCD scale factor with MC subtraction, with m_t/met cut:", y/fit.orig["qcd"], "from", fit.orig["qcd"], "to ", y
        #print "QCD scale factor with MC subtraction, without m_t/met cut:", qcd_sf_nomt, "from", fit.orig["qcd_nomtcut"], "to ", y_nomtcut
        
        plot_fit(fit.var, cut, fit.dataHisto, fit, lumi_iso[args.channel])
        
        n_bins = fit.dataHisto.GetNbinsX()
    
        print "n_bins", n_bins
        infile = "fits/"+fit.var.shortName+"_fit_"+cut.name+".root"
        f = TFile(infile)
        error = array('d',[0.])
        hQCD = f.Get(fit.var.shortName+"__qcd")
        
        #fit.orig_shape["qcd"]
        for bin in range(1, n_bins+1):
            lowedge = fit.dataHisto.GetBinLowEdge(bin)
            y = hQCD.IntegralAndError(bin, n_bins+1, error)
            with open(ofdir + "/%s_no_MC_subtraction_mt_%i_plus.txt" % (cut.name, int(lowedge)), "w") as of:
                qcd_sf = y / fit.orig_shape["qcd_no_mc_sub"].Integral(bin, n_bins+1)
                of.write("%f %f %f\n" % (qcd_sf, y, error[0]))
                of.write("Iso data yield %f\n" % fit.dataHisto.Integral(bin, n_bins+1))
                of.write("Cut string (iso) %s\n" % (cut.isoCutsMC))
            with open(ofdir + "/%s_mt_%i_plus.txt" % (cut.name, int(lowedge)), "w") as of:
                qcd_sf = y / fit.orig_shape["qcd"].Integral(bin, n_bins+1)
                of.write("%f %f %f\n" % (qcd_sf, y, error[0]))
                of.write("Iso data yield %f\n" % fit.dataHisto.Integral(bin, n_bins+1))
                of.write("Cut string (iso) %s\n" % (cut.isoCutsMC))
        """with open(ofdir + "/%s_nomtcut.txt" % cut.name, "w") as of:
            of.write("%f %f %f\n" % (qcd_sf_nomt, y_nomtcut, error_nomtcut))
            of.write("Iso data yield %f\n" % (fit.dataHisto.Integral()))
            of.write("Cut string (iso) %s\n" % (cut.isoCutsMC))"""

    print "Failed to converge: ", str(failed)

    # print "Selection: %s" % cut.name
    # print "QCD yield in selected region: %.2f +- %.2f, ratio to template from ONLY data %.3f" % (y, error, y/fit.orig["qcd_no_mc_sub"])
    # print "Total: QCD: %.2f +- %.2f, ratio to template from data %.3f" % (fit.qcd, fit.qcd_uncert, fit.qcd/fit.orig["qcd"])
    # print "W+Jets: %.2f +- %.2f, ratio to template: %.2f" % (fit.wjets, fit.wjets_uncert, fit.wjets/fit.wjets_orig)
    # print "Other MC: %.2f +- %.2f, ratio to template: %.2f" % (fit.nonqcd, fit.nonqcd_uncert, fit.nonqcd/fit.nonqcd_orig)

    # print "Fit info:"
    # print fit
    # print "doMTCut=",args.mtcut
    # print "cut=",args.cut

    # #output to file
    # of = open("QCD_yield_%s.txt" % args.cut, "w")
    # of.write("%f %f" % (fit.qcd, fit.qcd_uncert))
    # of.write("\n")
    # of.close()

