from plots.common.make_systematics_histos import *    
from plots.common.utils import *
from plots.common.cuts import *
import argparse
import os

if __name__=="__main__":
    parser = argparse.ArgumentParser(description='Makes systematics histograms for final fit')
    parser.add_argument('--channel', dest='channel', choices=["mu", "ele"], required=True, help="The lepton channel used for the fit")
    parser.add_argument('--path', dest='path', default="$STPOL_DIR/step3_latest_kbfi/")
    #parser.add_argument('--mva_cut', dest='mva_cut', type=float, default=-1, help="MVA cut value, use larger values") #not needed any more?
    parser.add_argument('--var', dest='var', choices=["eta_lj", "mva_BDT"], default="eta_lj", help="Variable to fit on")
    parser.add_argument('--coupling', dest='coupling', choices=["powheg", "comphep", "anomWtb-0100", "anomWtb-unphys"], default="powheg", help="Coupling used for signal sample")
    args = parser.parse_args()

    if args.var == "mva_BDT":
        cut_str = str(Cuts.mva_iso(args.channel))
        cut_str_antiiso = str(Cuts.mva_antiiso(args.channel))        
        plot_range = [20, -1, 1]
    else:
        cut_str = str(Cuts.eta_fit(args.channel))
        cut_str_antiiso = str(Cuts.eta_fit_antiiso(args.channel))    
        var = "eta_lj"
        plot_range = [15, 0, 4.5]

    indir = args.path
    outdir = os.path.join(os.environ["STPOL_DIR"], "lqetafit", "histos", generate_out_dir(args.channel, args.var, "-1", args.coupling))
    systematics = generate_systematics(args.channel, args.coupling)
    make_systematics_histos(args.var, cut_str, cut_str_antiiso, systematics, outdir, indir, args.channel, args.coupling, plot_range=plot_range)
