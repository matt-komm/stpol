#!/bin/bash
echo "Running step3 test"
cd "$STPOL_DIR"
source setenv.sh
OFDIR="$STPOL_DIR"/test_step3
if [ -d "$OFDIR" ]; then
    echo "removing '"$OFDIR"'"
    rm -Rf "$OFDIR"
fi
mkdir "$OFDIR"
echo "Calling ""$CMSSW_BASE"/bin/"$SCRAM_ARCH"/Step3_EventLoop
find testing/step2/ttbar -name "*.root" |  $CMSSW_BASE/bin/$SCRAM_ARCH/Step3_EventLoop $CMSSW_BASE/src/SingleTopPolarization/Analysis/python/runconfs/step3/test.py --doControlVars --isMC --outputFile=$OFDIR/out.root &> $OFDIR/log_step3.txt
tail -n10 "$OFDIR"/log_step3.txt
