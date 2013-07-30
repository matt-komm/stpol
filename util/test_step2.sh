#!/bin/bash
IN=$STPOL_DIR/testing/step1/ttbar/out_step1_numEvent100_Skim.root
OFDIR="$STPOL_DIR"/testing/step2/ttbar

echo "Runnin step2 test on IN="$IN" with output to OFDIR="$OFDIR
if [ -d "$OFDIR" ]; then
    echo "Removing "$OFDIR 
    rm -Rf "$OFDIR"
fi

mkdir -p $OFDIR

cmsRun $CMSSW_BASE/src/SingleTopPolarization/Analysis/python/runconfs/step2/step2.py doDebug=True inputFiles=file:$IN isMC=True subChannel=TTbar outputFile=$OFDIR/out.root &> $OFDIR/log_step2.txt
EX=$?
echo "Exit code:"$EX 
if [ "$EX" -ne 0 ]
then
    grep -A50 "Exception" $OFDIR/log_step2.txt
fi
