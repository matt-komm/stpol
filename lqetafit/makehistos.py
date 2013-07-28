from plots.common.make_systematics_histos import *    
from plots.common.utils import *
from plots.common.cuts import *
import argparse
import os

if __name__=="__main__":
    parser = argparse.ArgumentParser(description='Makes systematics histograms for final fit')
    parser.add_argument('--channel', dest='channel', choices=["mu", "ele"], required=True, help="The lepton channel used for the fit")
    parser.add_argument('--path', dest='path', default="$STPOL_DIR/step3_latest_kbfi/")
    parser.add_argument('--mva', dest='mva', action='store_true', default=False, help="Use MVA option")
    parser.add_argument('--mva_cut', dest='mva_cut', type=float, default=0.3, help="MVA cut value")args = parser.parse_args()

    if(args.mva):
        cut_str = str(Cuts.mva_iso(args.mva_cut, args.channel))
        cut_str_antiiso = str(Cuts.mva_antiiso(args.mva_cut, args.channel))
    else:
        cut_str = str(Cuts.eta_fit(args.channel))
        cut_str_antiiso = str(Cuts.eta_fit_antiiso(args.channel))    
    var = "eta_lj"

    indir = args.path
    outdir = os.path.join(os.environ["STPOL_DIR"], "lqetafit", "histos", generate_out_dir(args.channel, args.mva_cut))
    systematics = generate_systematics(args.channel)
    make_systematics_histos(var, cut_str, cut_str_antiiso, systematics, outdir, indir, args.channel, plot_range=[15, 0, 5])
