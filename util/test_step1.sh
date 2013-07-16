#!/bin/bash
#IN=/store/relval/CMSSW_5_3_6-START53_V14/RelValTTbar/GEN-SIM-RECO/v2/00000/62B0DFF3-F729-E211-9754-001A92811744.root
#IN=/store/relval/CMSSW_5_3_2-START53_V6/RelValTTbar/GEN-SIM-RECO/v1/0000/0A0607D6-7AB9-E111-AB16-002618943886.root
IN=file:/hdfs/cms/store/mc/Summer12_DR53X/TToLeptons_t-channel_8TeV-powheg-tauola/AODSIM/PU_S10_START53_V7A-v1/0000/646D8F72-D8DE-E111-859A-00259073E456.root
OFDIR=$STPOL_DIR/testing/step1/signal
echo "Running test_step1 with input $IN and output to $OFDIR"
rm -Rf $OFDIR
mkdir -p $OFDIR
cmsRun $CMSSW_BASE/src/SingleTopPolarization/Analysis/python/runconfs/step1/step1.py doDebug=True inputFiles=$IN outputFile=$OFDIR/out_step1.root maxEvents=10000 &> $OFDIR/log_step1.txt
EX=$?
echo "Exit code:"$EX 
if [ "$EX" -ne 0 ]
then
    tail -n 50 $OFDIR/log*.txt
fi
