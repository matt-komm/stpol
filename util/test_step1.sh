#!/bin/bash
#IN=/store/relval/CMSSW_5_3_6-START53_V14/RelValTTbar/GEN-SIM-RECO/v2/00000/62B0DFF3-F729-E211-9754-001A92811744.root
IN=/store/relval/CMSSW_5_3_2-START53_V6/RelValTTbar/GEN-SIM-RECO/v1/0000/0A0607D6-7AB9-E111-AB16-002618943886.root
OFDIR=$STPOL_DIR/testing/step1/ttbar
echo "Running test_step1 with input $IN and output to $OFDIR"
rm -Rf $OFDIR
mkdir -p $OFDIR
cmsRun $STPOL_DIR/runconfs/step1_newCmdLine_cfg.py doDebug=True inputFiles=$IN outputFile=$OFDIR/out_step1.root maxEvents=100 &> $OFDIR/log_step1.txt
EX=$?
echo "Exit code:"$EX 
if [ "$EX" -ne 0 ]
then
    tail -n 50 $OFDIR/log*.txt
fi
