#!/bin/bash
#IN=/store/relval/CMSSW_5_3_6-START53_V14/RelValTTbar/GEN-SIM-RECO/v2/00000/62B0DFF3-F729-E211-9754-001A92811744.root
IN=/store/data/Run2012D/SingleMu/AOD/22Jan2013-v1/10000/0015EC7D-EAA7-E211-A9B9-E0CB4E5536A7.root
OFDIR=$STPOL_DIR/testing/step1/data
echo "Running test_step1 with input $IN and output to $OFDIR"
rm -Rf $OFDIR
mkdir -p $OFDIR
cmsRun $CMSSW_BASE/src/SingleTopPolarization/Analysis/python/runconfs/step1/step1.py inputFiles=$IN outputFile=$OFDIR/out_step1.root maxEvents=100 isMC=False &> $OFDIR/log_step1.txt
EX=$?
echo "Exit code:"$EX 
if [ "$EX" -ne 0 ]
then
    tail -n 50 $OFDIR/log*.txt
fi
