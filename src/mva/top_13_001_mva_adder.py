import sys
import ROOT
from ROOT import TMVA
import numpy as np

from adder import setup_mva, rv, zero_buffers, treename, mva_loop_lepton_separate, STPOL_DIR

mvaname = "bdt_sig_bg_top_13_001"
def main():
    infiles = sys.argv[1:]
    print infiles

    mvas = dict()
#    mvas[13] = setup_mva(mvaname, STPOL_DIR + "/mvatools/weights/stop_mu_BDT.weights.xml")
#    mvas[11] = setup_mva(mvaname, STPOL_DIR + "/mvatools/weights/stop_ele_BDT.weights.xml")
    mvas[13] = setup_mva(mvaname, STPOL_DIR + "/mvatools/weights/stop_mu_BDT_with_top_mass_eta_lj_C_mu_pt_mt_mu_met_mass_bj_pt_bj_mass_lj.weights.xml")
    mvas[11] = setup_mva(mvaname, STPOL_DIR + "/mvatools/weights/stop_ele_BDT_with_top_mass_C_eta_lj_el_pt_mt_el_pt_bj_mass_bj_met_mass_lj.weights.xml")

    varmaps = dict()

    varmap_general = {
        "mass_bj":"bjet_mass",
        "eta_lj":"ljet_eta",
        "mass_lj":"ljet_mass",
        "pt_bj":"bjet_pt",
        "C":"C_with_nu",
    }

    varmaps[13] = {"mt_mu":"mtw", "mu_pt":"lepton_pt"}
    varmaps[11] = {"mt_el":"mtw", "el_pt":"lepton_pt"}
    for (k, v) in varmaps.items():
        varmaps[k].update(varmap_general)

    mva_loop_lepton_separate(mvaname, infiles, mvas, varmaps)

if __name__=="__main__":
    main()
