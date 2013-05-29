#!/bin/bash
echo "Running step3 test"
cd "$STPOL_DIR"
source setenv.sh CMSSW_5_3_8
OFDIR="$STPOL_DIR"/test_step3
if [ -d "$OFDIR" ]; then
    echo "removing '"$OFDIR"'"
    rm -Rf "$OFDIR"
fi
mkdir "$OFDIR"
echo "Calling ""$CMSSW_BASE"/bin/"$SCRAM_ARCH"/Step3_EventLoop
head -n5 "$STPOL_DIR"/filelist_step2_latest/iso/nominal/mc/TTJets_MassiveBinDECAY.txt |  "$CMSSW_BASE"/bin/"$SCRAM_ARCH"/Step3_EventLoop "$STPOL_DIR"/runconfs/step3_eventloop_test.py --isMC --outputFile="$OFDIR"/out.root &> "$OFDIR"/log_step3.txt
tail -n10 "$OFDIR"/log_step3.txt
