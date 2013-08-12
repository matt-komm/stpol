#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Produces QCD fit by taking QCD shape from anti-isolated data and other processes from MC. Specific cuts are defined in FitConfig.py with on-the-fly modifications for different cut regions
Fit is done on 3 components: QCD, W+Jets and all other MC, on the MTW variable for muons and MET for electrons.
Fit results are saved in the directory "fitted" for all possible MTW/MET cut values. 
Separate files are created for scale factors to apply to template taken from anti-isolated region whether or not anti-isolated MC is subtracted from the templated.
The fit itself uses the template with MC subtraction.
Fit plots are produced in the 'fit_plots' directory while the fitted distributions are saved 'fits' and templates in 'templates'

Command line parameters:
  '--channel' - "mu" or "ele"
  '--cut' - list of cut regions to perform the QCD estimation. Most important ones:
      '2j1t' - pre-MVA cut, always applies when MVA used from fit onwards
      'final__2j1t' - final selection, cut-based
      'fit__2j1t' - for cut-based fit__2j1t
      If no key is specified, QCD estimation will be done for all possible cases
  '--path' - where to take step3 output from
  '--noSystematics' - do not take into account shape systematics of JES, JER and UnclusteredEn in the estimation
  '--doSystematicCuts' - perform QCD estimation for a set of special cuts with varied anti-isolated region which are defined in systematics.py
  
  Other files of interest:
  init_data.py: definitions of datasets and files - TODO: update when new step2 add new files for data
  FitConfig.py: defines the cuts used in the fit, for different iso regions, etc.
"""

import sys,os

try:
    from theta_auto import *
except Exception as e:
    sys.stderr.write("You need a working version of theta in your PATH. See the script $STPOL_DIR/setup/install_theta.sh and $STPOL_DIR/setenv.sh.\n")
    raise e

from systematics import *
import logging
from plots.common.cuts import Cuts
from FitConfig import FitConfig
import rootpy
from run_fit import *
from plot_fit import *
logger = logging.getLogger("get_qcd_yield")

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
    parser.add_argument('--doSystematics', action="store_true", default=True)
    parser.add_argument('--noSystematics', dest="doSystematics", action="store_false")
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
    for cutn in args.cuts:
        cut = cuts[cutn]
        try:
            (results, fit) = get_qcd_yield_with_selection(cut, True, args.channel, base_path=args.path, do_systematics=args.doSystematics, doSystematicCuts = args.doSystematicCuts)
        except rootpy.ROOTError:
            failed += [cutn]
            continue
        (y, error_mtcut) = results["mt"]
        (y_nomtcut, error_nomtcut) = results["nomt"]
        qcd_sf = y/fit.orig["qcd_no_mc_sub"]
        qcd_sf_nomt = y_nomtcut/fit.orig["qcd_no_mc_sub_nomtcut"]
        
        print "QCD scale factor, with m_t/met cut:", qcd_sf, "from", fit.orig["qcd_no_mc_sub"], "to ", y
        print "QCD scale factor, without m_t/met cut:", qcd_sf_nomt, "from", fit.orig["qcd_no_mc_sub_nomtcut"], "to ", y_nomtcut
        print "Fit information", fit
        print "QCD scale factor with MC subtraction, with m_t/met cut:", y/fit.orig["qcd"], "from", fit.orig["qcd"], "to ", y
        #print "QCD scale factor with MC subtraction, without m_t/met cut:", qcd_sf_nomt, "from", fit.orig["qcd_nomtcut"], "to ", y_nomtcut
        
        plot_fit(fit.var, cut, fit.dataHisto, fit, lumi_iso[args.channel])
        
        n_bins = fit.dataHisto.GetNbinsX()
    
        infile = "fits/"+fit.var.shortName+"_fit_"+cut.name+".root"
        f = TFile(infile)
        error = array('d',[0.])
        hQCD = f.Get(fit.var.shortName+"__qcd")
        
        #fit.orig_shape["qcd"]
        for bin in range(1, n_bins+1):
            lowedge = fit.dataHisto.GetBinLowEdge(bin)
            y = hQCD.IntegralAndError(bin, n_bins+1, error)
            if bin == 1:
                error[0] = error_nomtcut
            elif (lowedge == 45 and args.channel == "ele") or (lowedge == 50 and args.channel == "mu"):
                error[0] = error_mtcut
            with open(ofdir + "/%s_no_MC_subtraction_mt_%i_plus.txt" % (cut.name, int(lowedge)), "w") as of:
                qcd_sf = 0
                if fit.orig_shape["qcd_no_mc_sub"].Integral(bin, n_bins+1) > 0:
                    qcd_sf = y / fit.orig_shape["qcd_no_mc_sub"].Integral(bin, n_bins+1)
                of.write("%f %f %f\n" % (qcd_sf, y, error[0]))
                of.write("Iso data yield %f\n" % fit.dataHisto.Integral(bin, n_bins+1))
                of.write("Cut string (iso) %s\n" % (cut.isoCutsMC))
            with open(ofdir + "/%s_mt_%i_plus.txt" % (cut.name, int(lowedge)), "w") as of:
                qcd_sf = 0
                if fit.orig_shape["qcd"].Integral(bin, n_bins+1) > 0:
                    qcd_sf = y / fit.orig_shape["qcd"].Integral(bin, n_bins+1)
                of.write("%f %f %f\n" % (qcd_sf, y, error[0]))
                of.write("Iso data yield %f\n" % fit.dataHisto.Integral(bin, n_bins+1))
                of.write("Cut string (iso) %s\n" % (cut.isoCutsMC))        
    print "Failed to converge: ", str(failed)

