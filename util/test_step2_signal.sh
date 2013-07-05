#!/bin/bash
echo "Running step2 test on signal"
IN=$STPOL_DIR/filelists/step1/mc/latest/T_t.txt
OFDIR=$STPOL_DIR/testing/step2/signal
rm -Rf $OFDIR
mkdir $OFDIR

time cmsRun $STPOL_DIR/runconfs/step2_newCmdLine_cfg.py doDebug=True inputFiles_load=$IN isMC=True channel=signal subChannel=T_t outputFile=$OFDIR/out.root maxEvents=10000 &> $OFDIR/log.txt
EX=$?
echo "Exit code:"$EX 
if [ "$EX" -ne 0 ]
then
    grep "Exception" -A10 $OFDIR/log*.txt
fi
grep "CPU/real" $OFDIR/log*.txt
