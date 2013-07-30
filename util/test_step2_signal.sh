#!/bin/bash
echo "Running step2 test on signal"
IN=file:$STPOL_DIR/testing/step1/signal/out_step1_numEvent1000_noSkim_noSlim.root
OFDIR=$STPOL_DIR/testing/step2/signal
rm -Rf $OFDIR
mkdir $OFDIR

time cmsRun $CMSSW_BASE/src/SingleTopPolarization/Analysis/python/runconfs/step2/step2.py doDebug=False inputFiles=file:$IN isMC=True subChannel=T_t outputFile=$OFDIR/out.root &> $OFDIR/log.txt
EX=$?
echo "Exit code:"$EX 
if [ "$EX" -ne 0 ]
then
    grep "Exception" -A10 $OFDIR/log*.txt
fi
grep "CPU/real" $OFDIR/log*.txt
