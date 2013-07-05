#!/usr/bin/env python
from subprocess import check_call
from glob import glob
from plots.common.utils import get_sample_name
import os
import argparse
import datetime

if __name__=="__main__":
    parser = argparse.ArgumentParser(
        description='Runs step3 trees on the cluster'
    )
    parser.add_argument("-o", "--ofdir", type=str, default=None, required=False,
                        help="the output directory for the step3 trees")
    parser.add_argument("--cutStringProcessed", type=str,
        default="--doNJets --nJ=2,3 --doHLT --doLepton", required=False,
        help="Specify the cutstring for the step3 config, which will reduce the amount of events processed. For options, see step3_eventloop_base_nocuts_cfg.py"
    )
    parser.add_argument("--cutStringSelected", type=str,
        default="1.0", required=False,
        help="The additional cutstring for which to create an Events_selected TTree.")
    cmdline_args = parser.parse_args()

    fldir = "filelists/step2/latest"

    leptons = ["mu", "ele"]
    isos = ["iso", "antiiso"]
    systs = ["nominal"]

    signal_samples = ["T_t", "Tbar_t", "T_t_ToLeptons", "Tbar_t_ToLeptons"]
    data_samples = ["SingleMu", "SingleEle"]
    cutstr = cmdline_args.cutStringProcessed + ' --cutString="%s"' % cmdline_args.cutStringSelected
    if not cmdline_args.ofdir:
        cmdline_args.ofdir = "out_step3_%s_%s" % (os.getlogin(), datetime.datetime.now().strftime("%d_%m_%H_%M"))

    for iso in isos:
        for syst in systs:
            path = "/".join([fldir, iso, syst, "*"])
            files = glob(path + "/*.txt")
            for fi in files:
                sampn = get_sample_name(fi)
                isSignal = sampn in signal_samples
                isMC = not sampn in data_samples
                #if iso=="antiiso" and isMC: continue
                for lep in leptons:
                    args = "--lepton=%s" % lep
                    if isMC:
                        args += " --doControlVars --isMC"

                    #Signal sample must be processed unskimmed
                    if not isSignal:
                        args += " " + cutstr
                    ofpath = "/".join([cmdline_args.ofdir, lep, iso, syst])

                    try:
                        os.makedirs(ofpath)
                    except OSError:
                        pass

                    cmd = " ".join(["$STPOL_DIR/analysis_step3/suball.sh", "'"+args+"'", ofpath, fi])
                    print cmd
                    check_call(cmd, shell=True)



