#!/usr/bin/env python
from subprocess import check_call
from glob import glob
from plots.common.utils import get_sample_name
import os

if __name__=="__main__":
    fldir = "filelists/step2/latest"

    leptons = ["mu", "ele"]
    isos = ["iso", "antiiso"]
    systs = ["nominal"]

    signal_samples = ["T_t", "Tbar_t", "T_t_ToLeptons", "Tbar_t_ToLeptons"]
    data_samples = ["SingleMu", "SingleEle"]
    cutstr = "--doNJets --nJ=2,3 --doHLT --doLepton"
    ofdir = "out_step3_test3"

    for iso in isos:
        for syst in systs:
            path = "/".join([fldir, iso, syst, "*"])
            files = glob(path + "/*.txt")
            for fi in files:
                sampn = get_sample_name(fi)
                isSignal = sampn in signal_samples
                isMC = not sampn in data_samples
                if iso=="antiiso" and isMC: continue
                for lep in leptons:
                    args = "--lepton=%s" % lep
                    if isMC:
                        args += " --doControlVars --isMC"

                    #Signal sample must be processed unskimmed
                    if not isSignal:
                        args += cutstr
                    ofpath = "/".join([ofdir, lep, iso, syst])

                    try:
                        os.makedirs(ofpath)
                    except OSError:
                        pass

                    cmd = " ".join(["$STPOL_DIR/analysis_step3/suball.sh", "'"+args+"'", ofpath, fi])
                    print cmd
                    check_call(cmd, shell=True)



