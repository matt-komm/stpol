#!/usr/bin/env python
"""
NB! QCD estimation has to be run before as the script takes results straight from qcd_estimation/fitted
For MVA fitting the fit '2j1t' is needed and for eta_j' 'fit_2j1t'

The script creates histograms named in theta format for 3 components - signal ('tchan'), W/Z+jets with WW ('wzjets') and Top processes (ttbar, tW-channel, s-channel) plus QCD ('other') for all the systematic variations
The systematics themselves are defined in plots.common/make_systematics_histos.py (sorry, poorly written code) and are divided into 3 groups (1. having separate files for each dataset (En, Res, UnclusteredEn);
  2. having separate files, but applying only to a few datasets; 3. altering weights). Each group is treated differently. 
If tou want to add a new systematic, it is added to this file (or uncomment one of the premade ones which didn't have datasets available before).
TODO: add pileup, ttbar and PDF uncertainties when available and tchan_scale once new data processing completes
The loading of the samples is done in plots.common.load_samples.py (also messy, sorry about that). Adding a new weight-based systematic should require no change in this file, however when adding a systematics that
deals with separate files, then these should be processed there.

Possible command-line arguments are the following:
'--channel', '--path' - as previously
'--var' - variable of the histograms, possible choices: ["eta_lj", "C", "mva_BDT", "mva_BDT_with_top_mass_eta_lj_C_mu_pt_mt_mu_met_mass_bj_pt_bj_mass_lj", "mva_BDT_with_top_mass_C_eta_lj_el_pt_mt_el_pt_bj_mass_bj_met_mass_lj"],
'--coupling' - by default we are using the powheg samples for signal. Here we can use comphep or anomalous couplings instead. choices=["powheg", "comphep", "anomWtb-0100", "anomWtb-unphys"], default="powheg"]
'--asymmetry' - reweigh the generated asymmetry value to something else. Used for linearity tests and estimating uncertainties if the measured result largely differs from the generated one
'--mtmetcut' - use an alternative value for MTW/MET cut, used for cross-checks
"""

import logging
logging.basicConfig(level=logging.WARNING)

from plots.common.make_systematics_histos import generate_out_dir, generate_systematics, make_systematics_histos
from plots.common.cuts import *

from rootpy.io import File
from os.path import join
from plots.common.histogram import norm
from plots.common.utils import NestedDict, mkdir_p
from fit import *
import argparse
from plots.common.tdrstyle import tdrstyle
from plots.common.sample import Sample

if __name__=="__main__":
    parser = argparse.ArgumentParser(description='Makes systematics histograms for final fit')
    parser.add_argument('--channel', choices=["mu", "ele"], required=True, help="The lepton channel used for the fit")
    parser.add_argument('--path', default="$STPOL_DIR/step3_latest_kbfi/")
    parser.add_argument(
        '--var',
        choices=[
            "eta_lj", "C", "mva_BDT",
            "mva_BDT_with_top_mass_eta_lj_C_mu_pt_mt_mu_met_mass_bj_pt_bj_mass_lj", "mva_BDT_with_top_mass_C_eta_lj_el_pt_mt_el_pt_bj_mass_bj_met_mass_lj"
        ],
        default=None, help="Variable to fit on"
    )

    parser.add_argument('--coupling', choices=["powheg", "comphep", "anomWtb-0100", "anomWtb-unphys"], default="powheg", help="Coupling used for signal sample")
    parser.add_argument('--asymmetry', help="Asymmetry to reweight generated distribution to", default=None)
    parser.add_argument('--mtmetcut', help="MT/MET cut", default=None)
    parser.add_argument('--extra', help="String to describe fit properties", default=None)
    args = parser.parse_args()

    #Most likely we'll want to fit on the BDT, so set this by default
    if not args.var:
        if args.channel=='mu':
            args.var = 'mva_BDT_with_top_mass_eta_lj_C_mu_pt_mt_mu_met_mass_bj_pt_bj_mass_lj'
        elif args.channel=='ele':
            args.var = 'mva_BDT_with_top_mass_C_eta_lj_el_pt_mt_el_pt_bj_mass_bj_met_mass_lj'

    if args.var == "C" or args.var.startswith("mva"):
        cut_str = str(Cuts.mva_iso(args.channel, mva_var=args.var, mtcut=args.mtmetcut))
        cut_str_antiiso = str(Cuts.mva_antiiso(args.channel, mva_var=args.var, mtcut=args.mtmetcut))
        if args.var.startswith("mva"):
            plot_range = [20, -1, 1]
        else:
            plot_range = [20, 0, 1]
    else:
        cut_str = str(Cuts.eta_fit(args.channel, mtcut=args.mtmetcut))
        cut_str_antiiso = str(Cuts.eta_fit_antiiso(args.channel, mtcut=args.mtmetcut))
        var = "eta_lj"
        plot_range = [15, 0, 4.5]
    indir = args.path
    outdir = os.path.join(os.environ["STPOL_DIR"], "final_fit", "histos", "input", generate_out_dir(args.channel, args.var, "-1", args.coupling, args.asymmetry, args.mtmetcut, extra=args.extra))
    outdir_final = os.path.join(os.environ["STPOL_DIR"], "final_fit", "histos")
    #generate the systematics to use
    systematics = generate_systematics(args.channel, args.coupling)
    #make histograms with all the systematic variations
    make_systematics_histos(args.var, cut_str, cut_str_antiiso, systematics, outdir, indir, args.channel, args.coupling, plot_range=plot_range, asymmetry=args.asymmetry, mtmetcut=args.mtmetcut)
    mkdir_p(outdir_final)
    #move results file from temporary location    
    shutil.move(
        '/'.join([outdir, "lqeta.root"]),
        '/'.join([
            outdir_final,
            generate_out_dir(args.channel, args.var, "-1", args.coupling, args.asymmetry, args.mtmetcut, extra=args.extra)+ ".root"]
        )
    )
    print "finished"
