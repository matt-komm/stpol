#!/usr/bin/env python
from subprocess import check_call
from glob import glob
from plots.common.utils import get_sample_name
import os
import argparse
import datetime
from SingleTopPolarization.Analysis import sample_types
import pdb

if __name__=="__main__":
    parser = argparse.ArgumentParser(
        description='Runs step3 trees on the cluster'
    )

    parser.add_argument("indir",
        default=None, type=str,
        help="Input directory with the file lists"
    )

    parser.add_argument(
        "-o", "--ofdir", type=str, default="out/step3", required=False,
        help="the output directory for the step3 trees"
    )
    parser.add_argument("--cutStringProcessed", type=str,
        default="--doNJets --nJ=2,3 --doHLT --doLepton", required=False,
        help="Specify the cutstring for the step3 config, which will reduce the amount of events processed. For options, see step3_eventloop_base_nocuts_cfg.py"
    )
    parser.add_argument("--applyCutsToSignal", type=bool,
        default=False, required=False,
        help="Should the processing cuts be applied on the signal samples?"
    )
    parser.add_argument("--dryRun",
        default=False, action="store_true",
        help="Don't really submit the jobs."
    )
    parser.add_argument("--syst-on", dest="syst",
        default=True, required=False, action="store_true",
        help="Do the systematics"
    )
    cmdline_args = parser.parse_args()
    print cmdline_args
    print "Input directory is %s" % cmdline_args.indir

    if not cmdline_args.ofdir:
        cmdline_args.ofdir = "out_step3_%s_%s" % (os.getlogin(), datetime.datetime.now().strftime("%d_%m_%H_%M"))
    leptons = ["mu", "ele"]

    flist = []
    if os.path.isdir(cmdline_args.indir):
        for root, dirs, files in os.walk(cmdline_args.indir):
            for fi in files:
                flist.append(os.path.join(root, fi))
    elif os.path.isfile(cmdline_args.indir):
        for line in open(cmdline_args.indir):
            flist.append(line.strip())

    for fi in flist:
        if not fi.endswith(".txt"):
            continue
        sampn = get_sample_name(fi)
        is_signal = sample_types.is_signal(sampn)
        isMC = sample_types.is_mc(sampn)
        for lep in leptons:
            if sampn.startswith("SingleMu") and lep=="ele":
                continue
            if sampn.startswith("SingleEle") and lep=="mu":
                continue
            args = " --doControlVars --lepton=%s" % lep
            if isMC:
                args += " --isMC"

                #!!!!!!!FIXME: cleverer way of getting the systematic scenario
                if "nominal" in fi:
                    args += " --systematic=nominal"

                elif not cmdline_args.syst:
                    continue
                else:
                    spl = fi.split("/")
                    try:
                        idx = spl.index("mc")
                    except:
                        idx = spl.index("mc_syst")
                    syst = spl[idx+2]
                    args += " --systematic="+syst

            #Apply the processing cuts
            if not is_signal or (is_signal and cmdline_args.applyCutsToSignal):
                args += " " + cmdline_args.cutStringProcessed

            ofpath = os.path.dirname(fi.replace("filelists", cmdline_args.ofdir).replace("step2", lep))
            try:
                os.makedirs(ofpath)
            except OSError:
                pass

            cmd = " ".join(["$STPOL_DIR/analysis_step3/suball.sh", "'"+args+"'", ofpath, fi])
            print cmd
            if not cmdline_args.dryRun:
                check_call(cmd, shell=True)
