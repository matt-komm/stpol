#!/bin/bash
echo "Running step2 test on signal"
IN=file:~/single_top/stpol/testing_step1_signal/out_step1_numEvent1000_noSkim_noSlim.root
OFDIR=$STPOL_DIR/testing/step2/presel
rm -Rf $OFDIR
mkdir -p $OFDIR

time cmsRun $STPOL_DIR/runconfs/step2/preselection.py doDebug=True inputFiles=$IN subChannel=T_t outputFile=$OFDIR/out.root maxEvents=10000 &> $OFDIR/log_step2.txt
EX=$?
echo "Exit code:"$EX 
if [ "$EX" -ne 0 ]
then
    grep "Exception" -A10 $OFDIR/log*.txt
fi
grep "CPU/real" $OFDIR/log*.txt
