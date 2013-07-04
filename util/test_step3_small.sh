#!/bin/bash
echo "Running step3 test"
cd "$STPOL_DIR"
source setenv.sh
OFDIR="$STPOL_DIR"/testing_step3
if [ -d "$OFDIR" ]; then
    echo "removing '"$OFDIR"'"
    rm -Rf "$OFDIR"
fi
mkdir "$OFDIR"
echo "Calling ""$CMSSW_BASE"/bin/"$SCRAM_ARCH"/Step3_EventLoop
find testing_step2 -name "*.root" |  "$CMSSW_BASE"/bin/"$SCRAM_ARCH"/Step3_EventLoop "$STPOL_DIR"/runconfs/step3_eventloop_test.py --doControlVars --isMC --outputFile="$OFDIR"/out.root &> "$OFDIR"/log_step3.txt
tail -n10 "$OFDIR"/log_step3.txt
