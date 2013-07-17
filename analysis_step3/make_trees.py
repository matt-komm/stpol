#!/usr/bin/env python
from subprocess import check_call
from glob import glob
from plots.common.utils import get_sample_name
import os
import argparse
import datetime
from SingleTopPolarization.Analysis import sample_types

if __name__=="__main__":
    parser = argparse.ArgumentParser(
        description='Runs step3 trees on the cluster'
    )
    parser.add_argument(
        "-o", "--ofdir", type=str, default="out/step3", required=False,
        help="the output directory for the step3 trees"
    )
    parser.add_argument("--cutStringProcessed", type=str,
        default="--doNJets --nJ=2,3 --doHLT --doLepton --doEventShape", required=False,
        help="Specify the cutstring for the step3 config, which will reduce the amount of events processed. For options, see step3_eventloop_base_nocuts_cfg.py"
    )
    parser.add_argument("--cutStringSelected", type=str,
        default="1.0", required=False,
        help="The additional cutstring for which to create an Events_selected TTree.")
    parser.add_argument("--applyCutsToSignal", type=bool,
        default=False, required=False,
        help="Should the processing cuts be applied on the signal samples?"
    )
    parser.add_argument("--dryRun",
        default=False, action="store_true",
        help="Don't really submit the jobs."
    )
    cmdline_args = parser.parse_args()
    print cmdline_args
    fldir = "filelists/Jul15_partial"

    data_samples = ["SingleMu", "SingleEle"]
    if not cmdline_args.ofdir:
        cmdline_args.ofdir = "out_step3_%s_%s" % (os.getlogin(), datetime.datetime.now().strftime("%d_%m_%H_%M"))
    leptons = ["mu", "ele"]

    cmdline_args.cutStringSelected = cmdline_args.cutStringSelected.strip().replace(" ","")

    for root, dirs, files in os.walk(fldir):
        for fi in files:
            fi = root+"/" + fi
            if not fi.endswith(".txt"):
                continue
            sampn = get_sample_name(fi)
            is_signal = sample_types.is_signal(sampn)
            isMC = not sampn in data_samples
            #if iso=="antiiso" and isMC: continue
            for lep in leptons:
                args = "--lepton=%s" % lep
                if isMC:
                    args += " --doControlVars --isMC"

                #Always apply the selection cuts
                args += ' --cutString="%s"' % cmdline_args.cutStringSelected

                #Apply the processing cuts
                if not is_signal or (is_signal and cmdline_args.applyCutsToSignal):
                    args += " " + cmdline_args.cutStringProcessed

                ofpath = root.replace("filelists", cmdline_args.ofdir).replace("step2", lep)
                try:
                    os.makedirs(ofpath)
                except OSError:
                    pass

                cmd = " ".join(["$STPOL_DIR/analysis_step3/suball.sh", "'"+args+"'", ofpath, fi])
                print cmd
                if not cmdline_args.dryRun:
                    check_call(cmd, shell=True)

#    ofpath = "/".join([cmdline_args.ofdir, lep, iso, "wjets_sherpa"])
#    args = "--lepton=mu --doControlVars --isMC"
#    fi = "filelists/step2/WJets_sherpa_06_10/*.txt"
#    cmd = " ".join(["$STPOL_DIR/analysis_step3/suball.sh", "'"+args+"'", ofpath, fi])
#    check_call(cmd, shell=True)

