#!/bin/bash
echo "Running step2 test on data"
IN=`head -n1 $STPOL_DIR/filelists/step1/data/latest/SingleMu.txt`
OFDIR=$STPOL_DIR/testing/step2/data
rm -Rf $OFDIR
mkdir -p $OFDIR

time cmsRun $STPOL_DIR/runconfs/step2_newCmdLine_cfg.py doDebug=True inputFiles=$IN isMC=False outputFile=$OFDIR/out.root maxEvents=10000 &> $OFDIR/log.txt
EX=$?
echo "Exit code:"$EX 
if [ "$EX" -ne 0 ]
then
    grep "Exception" -A10 $OFDIR/log*.txt
fi
grep "CPU/real" $OFDIR/log*.txt
