import sys
import ROOT
from ROOT import TMVA
import numpy as np

from adder import setup_mva, rv, zero_buffers, treename

def main():
    infiles = sys.argv[1:]
    print infiles

    mvas = dict()
    mvas[13] = setup_mva("qcd", "../qcd_mva/weights/anti_QCD_MVA_10_01_qcdBDT_mu.weights.xml")
    mvas[11] = setup_mva("qcd", "../qcd_mva/weights/anti_QCD_MVA_10_01_qcdBDT_ele.weights.xml")

    varmaps = dict()
    varmaps[13] = {"mu_mtw":"mtw"}
    varmaps[11] = {"ele_mtw":"mtw"}

    mvaname = "bdt_qcd"
    for infn in infiles:
        print "Processing file",infn
        #get the events tree
        inf = ROOT.TFile(infn)
        tree = inf.Get(treename)

        if not tree:
            raise Exception("Could not open TTree '%s' in %s" % (treename, infn))

        ofn = infn.replace(".root", "_mva_%s.csv" % mvaname)

        ofile = open(ofn, "w")
        ofile.write("# filename=%s\n" % infn)
        ofile.write("bdt\n")

        nproc = 0
        for event in tree:

            #make sure the TBranch buffers have a 0 values
            for (k, mva) in mvas.items():
                zero_buffers(mva[1])

            lepton_type, lepton_type_isna = rv(event, "lepton_type")
            if lepton_type_isna:
                continue

            mvareader, varbuffers = mvas[lepton_type]
            isna = False

            varmap = varmaps[lepton_type]
            for var in varbuffers.keys():
                if var in varmap.keys():
                    varn = varmap[var]
                else:
                    varn = var

                v, isna = rv(event, varn)
                if not isna:
                    varbuffers[var][0] = v

            if (isna) or not event.passes:
                x = "NA" #MVA(..., NA, ...) -> NA
            else:
#                print [(x, y[0]) for x,y in varbuffers.items()]
                x = mvareader.EvaluateMVA(mvaname)

#            print x
            ofile.write(str(x) + "\n")
            nproc += 1

        ofile.write("# ntree=%d nproc=%d\n" % (tree.GetEntries(), nproc))
        inf.Close()
        ofile.close()


if __name__=="__main__":
    main()
