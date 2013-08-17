import os
import logging
import shutil
import argparse
from efficiency import *
from plots.common.cuts import *
from plots.common.make_systematics_histos import generate_out_dir, generate_systematics, make_systematics_histos
#from binning import *
logging.basicConfig(level=logging.DEBUG)

"""
Prepare histograms needed for unfolding
The main amount of work goes to creating the same systematic histograms as makehistos.py, just that now they're for cos_theta and with a cut on MVA (or final cut-based selection)
Also created are histograms for generated and reconstructed signal events, selection efficiency of those and a transfer matrix needed for the unfolding.
Currently, 6 bins are used for generated events and 12 for reconstructed. This (6<12) is needed for the unfolding to work properly (and we don't 0 in the middle of any bin)

Command-lina arguments are mostly the same as for makehistos.py, except for:
'--eta' if you want to fit on eta
'--mva_var' instead of '--var' specifies variable if using MVA ('--eta' not specified)
'--cut' the cut on MVA as float (MVA > [value specified])

./makeUnfoldingHistos.sh  is used to run a scan over MVA cut values producing histograms for each
"""

def make_histos(binning, cut_str, cut_str_antiiso, indir, channel, mva_cut, coupling, asymmetry):
    systematics = generate_systematics(channel, coupling)
    var = "cos_theta"
    subdir = generate_out_dir(channel, var, mva_cut, coupling, asymmetry)
    outdir = '/'.join([os.environ["STPOL_DIR"], "unfold", "histos", "input", subdir])
    make_systematics_histos(var, cut_str, cut_str_antiiso, systematics, outdir, indir, channel, coupling, plot_range=binning, asymmetry=asymmetry)
    shutil.move('/'.join([os.environ["STPOL_DIR"], "unfold", "histos", "input", subdir])+"/lqeta.root", '/'.join([os.environ["STPOL_DIR"], "unfold", "histos", subdir])+"/data.root")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Makes systematics histograms for unfolding')
    parser.add_argument('--channel', dest='channel', choices=["mu", "ele"], required=True, help="The lepton channel used")
    parser.add_argument('--path', dest='path', default="$STPOL_DIR/step3_latest/", required=True)
    parser.add_argument('--eta', action='store_true', default=False, help="Use eta cut, not MVA")
    parser.add_argument('--mva_var', dest='mva_var', default=None, help="MVA variable name")
    parser.add_argument('--cut', dest='cut', type=float, default=-1, help="MVA cut value")
    parser.add_argument('--coupling', dest='coupling', choices=["powheg", "comphep", "anomWtb-0100", "anomWtb-unphys"], default="powheg", help="Coupling used for signal sample")
    #Not used currently    
    #parser.add_argument('--binning', dest='binning', help="File from which to load a pre-calculated binning")
    parser.add_argument('--asymmetry', dest='asymmetry', help="Asymmetry to reweight generated distribution to", default=None)
    args = parser.parse_args()

    indir = args.path    

    #indir = '/'.join([os.environ["STPOL_DIR"], "step3_latest"])
    if(not args.eta):
        if not args.mva_var:
            if args.channel=='mu':
                args.mva_var = 'mva_BDT_with_top_mass_eta_lj_C_mu_pt_mt_mu_met_mass_bj_pt_bj_mass_lj'
            elif args.channel=='ele':
                args.mva_var = 'mva_BDT_with_top_mass_C_eta_lj_el_pt_mt_el_pt_bj_mass_bj_met_mass_lj'        
        cut_str = str(Cuts.mva_iso(args.channel, args.cut, args.mva_var))
        cut_str_antiiso = str(Cuts.mva_antiiso(args.channel, args.cut, args.mva_var))
    else:
        cut_str = str(Cuts.final_iso(args.channel))
        cut_str_antiiso = str(Cuts.final_antiiso(args.channel))
    weight = str(Weights.total_weight(args.channel))
    
    #Ignore the binning stuff, just same sized bins now
    bins_rec = [12, -1, 1]
    bins_gen = [6, -1, 1]
    
    efficiency(cut_str, weight, bins_gen, bins_rec, indir, args.channel, args.cut, args.coupling, args.asymmetry)
    make_histos(bins_rec, cut_str, cut_str_antiiso, indir, args.channel, args.cut, args.coupling, args.asymmetry)
    print "finished"

    #These were used with Steffen's rebinning system. Save here for reference, maybe still needed
    """bins_gen = 7
    bins_rec = bins_gen * 2
    zerobin_gen = 2
    zerobin_rec = 4
    if args.binning and len(args.binning) > 0:
        (bin_list_gen, bin_list_rec) = load_binning(args.binning)
    else:
        (bin_list_gen, bin_list_rec) = findbinning(bins_gen, cut_str, weight, indir, args.channel, args.coupling, zerobin_gen, zerobin_rec, args.asymmetry)
    #bin_list_gen = numpy.array([-1.,    -0.2632, 0.0,   0.19,    0.3528,  0.5062,  0.6652,  1.    ])
    #bin_list_rec = numpy.array([-1.,     -0.4496, -0.2254, -0.069,   0.0,   0.1478,  0.2346,  0.3174,  0.3956,   0.4738,  0.545,   0.6112,  0.6866,  0.7714,  1.    ])
    system.exit(1)
    binning_file = open('binnings/'+generate_out_dir(args.channel, "cos_theta", args.mva_cut, args.coupling, args.asymmetry)+'.txt', 'w')
    binning_file.write(str(bin_list_gen)+';\n')
    binning_file.write(str(bin_list_rec))
    binning_file.close()
    
    print "found binning: ", bin_list_gen, ";", bin_list_rec
    """
    #rebin(cut_str, weight, bins_gen, bin_list_gen, bins_rec, bin_list_rec, indir, args.channel, args.mva_cut, args.coupling, args.asymmetry)
    #efficiency_rebinned(cut_str, weight, bin_list_gen, indir, args.channel, args.mva_cut, args.coupling, args.asymmetry)
    #make_histos_rebinned(bin_list_rec, cut_str, cut_str_antiiso, indir, args.channel, args.mva_cut, args.coupling, args.asymmetry)
    
