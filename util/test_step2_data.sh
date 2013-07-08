#!/bin/bash
echo "Running step2 test on data"
IN=$STPOL_DIR/testing/step1/data/out_step1_numEvent100_Skim.root
OFDIR=$STPOL_DIR/testing/step2/data
rm -Rf $OFDIR
mkdir -p $OFDIR

time cmsRun $CMSSW_BASE/src/SingleTopPolarization/Analysis/python/runconfs/step2/step2.py doDebug=True inputFiles=file:$IN isMC=False outputFile=$OFDIR/out.root maxEvents=10000 &> $OFDIR/log.txt
EX=$?
echo "Exit code:"$EX 
if [ "$EX" -ne 0 ]
then
    grep "Exception" -A10 $OFDIR/log*.txt
fi
grep "CPU/real" $OFDIR/log*.txt
