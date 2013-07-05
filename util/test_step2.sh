#!/bin/bash

#IN=`find $STPOL_DIR/testing_step1 -name "out*.root"`
IN=$STPOL_DIR/testing/step1/ttbar/out_step1_numEvent100_Skim.root
OFDIR="$STPOL_DIR"/testing_step2

echo "Runnin step2 test on IN="$IN" with output to OFIR="$OFDIR
if [ -d "$OFDIR" ]; then
    echo "Removing "$OFDIR 
    rm -Rf "$OFDIR"
fi

mkdir $OFDIR

cmsRun $STPOL_DIR/runconfs/step2_newCmdLine_cfg.py doDebug=True inputFiles=file:$IN isMC=True subChannel=TTbar outputFile=$OFDIR/out.root &> $OFDIR/log_step2.txt
EX=$?
echo "Exit code:"$EX 
if [ "$EX" -ne 0 ]
then
    grep -A50 "Exception" $OFDIR/log_step2.txt
fi
