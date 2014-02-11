import sys
import ROOT
from ROOT import TMVA
import numpy as np

from adder import setup_mva, rv, zero_buffers, treename, mva_loop_lepton_separate

mvaname = "bdt_sig_bg_top_13_001"
def main():
    infiles = sys.argv[1:]
    print infiles

    mvas = dict()
    mvas[13] = setup_mva(mvaname, "../../mvatools/weights/stop_mu_BDT.weights.xml")
    mvas[11] = setup_mva(mvaname, "../../mvatools/weights/stop_ele_BDT.weights.xml")

    varmaps = dict()

    varmap_general = {
        "mass_bj":"bjet_mass",
        "eta_lj":"ljet_eta",
        "mass_lj":"ljet_mass",
        "pt_bj":"bjet_pt"
    }

    varmaps[13] = {"mt_mu":"mtw", "mu_pt":"lepton_pt"}
    varmaps[11] = {"mt_el":"mtw", "el_pt":"lepton_pt"}
    for (k, v) in varmaps.items():
        varmaps[k].update(varmap_general)

    mva_loop_lepton_separate(infiles, mvas, varmaps)

if __name__=="__main__":
    main()
