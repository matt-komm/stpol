from plots.common.make_systematics_histos import generate_out_dir, generate_systematics, make_systematics_histos
#from plots.common.utils import *
from plots.common.cuts import *
#import argparse

from rootpy.io import File
from os.path import join
#from plots.common.hist_plots import plot_hists_dict
from plots.common.histogram import norm
from plots.common.utils import NestedDict
from fit import *
import argparse
from plots.common.tdrstyle import tdrstyle
from plots.common.sample import Sample

if __name__=="__main__":
    parser = argparse.ArgumentParser(description='Makes systematics histograms for final fit')
    parser.add_argument('--channel', dest='channel', choices=["mu", "ele"], required=True, help="The lepton channel used for the fit")
    parser.add_argument('--path', dest='path', default="$STPOL_DIR/step3_latest_kbfi/")
    parser.add_argument('--var', dest='var', choices=["eta_lj", "C", "mva_BDT", "mva_BDT_with_top_mass_eta_lj_C_mu_pt_mt_mu_met_mass_bj_pt_bj_mass_lj", "mva_BDT_with_top_mass_C_eta_lj_el_pt_mt_el_pt_bj_mass_bj_met_mass_lj"], default="eta_lj", help="Variable to fit on")
    parser.add_argument('--coupling', dest='coupling', choices=["powheg", "comphep", "anomWtb-0100", "anomWtb-unphys"], default="powheg", help="Coupling used for signal sample")
    parser.add_argument('--asymmetry', dest='asymmetry', help="Asymmetry to reweight generated distribution to", default=None)
    parser.add_argument('--mtmetcut', dest='mtmetcut', help="MT/MET vut", default=None)
    args = parser.parse_args()

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
    outdir = os.path.join(os.environ["STPOL_DIR"], "final_fit", "histos", "input", generate_out_dir(args.channel, args.var, "-1", args.coupling, args.asymmetry, args.mtmetcut))
    outdir_final = os.path.join(os.environ["STPOL_DIR"], "final_fit", "histos")
    systematics = generate_systematics(args.channel, args.coupling)
    make_systematics_histos(args.var, cut_str, cut_str_antiiso, systematics, outdir, indir, args.channel, args.coupling, plot_range=plot_range, asymmetry=args.asymmetry, mtmetcut=args.mtmetcut)
    mkdir_p(outdir_final)
    shutil.move('/'.join([outdir, "lqeta.root"]), '/'.join([outdir_final, generate_out_dir(args.channel, args.var, "-1", args.coupling, args.asymmetry)+".root"]))
    print "finished"
