import sys
import ROOT
from ROOT import TMVA
import numpy as np

from adder import setup_mva, rv, zero_buffers, treename, mva_loop_lepton_separate

mvaname = "bdt_qcd"

def main():
    infiles = sys.argv[1:]
    print infiles

    mvas = dict()
    mvas[13] = setup_mva(mvaname, "../qcd_mva/weights/anti_QCD_MVA_10_01_qcdBDT_mu.weights.xml")
    mvas[11] = setup_mva(mvaname, "../qcd_mva/weights/anti_QCD_MVA_10_01_qcdBDT_ele.weights.xml")

    varmaps = dict()
    varmaps[13] = {"mu_mtw":"mtw", "c":"C"}
    varmaps[11] = {"ele_mtw":"mtw", "c":"C"}

    mva_loop_lepton_separate(infiles, mvas, varmaps)

if __name__=="__main__":
    main()
