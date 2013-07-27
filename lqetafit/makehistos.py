from plots.common.make_systematics_histos import *    
from plots.common.utils import *
from plots.common.cuts import *
import argparse
import os

if __name__=="__main__":
    parser = argparse.ArgumentParser(description='Makes systematics histograms for final fit')
    parser.add_argument('--channel', dest='channel', choices=["mu", "ele"], required=True, help="The lepton channel used for the fit")
    parser.add_argument('--path', dest='path', default="$STPOL_DIR/step3_latest_kbfi/")
    args = parser.parse_args()

    cut_str = str(Cuts.eta_fit(args.channel))
    cut_str_antiiso = str(Cuts.eta_fit_antiiso(args.channel))
    var = "eta_lj"

    indir = args.path
    outdir = os.path.join(os.environ["STPOL_DIR"], "lqetafit", "histos")
    systematics = generate_systematics(args.channel)
    make_systematics_histos(var, cut_str, cut_str_antiiso, systematics, outdir, indir, args.channel, plot_range=[15, 0, 5])
