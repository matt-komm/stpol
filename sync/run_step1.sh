#!/bin/bash
echo "step1 sync"
echo "Inclusive sample"
CFG=$CMSSW_BASE/src/SingleTopPolarization/Analysis/python/runconfs/step1/step1.py
OPTS="doSkimming=False doDebug=False doSync=True"
SYNC_DIR=$STPOL_DIR/sync
time cmsRun $CFG $OPTS inputFiles_load=$STPOL_DIR/sync/inclusive/files.txt outputFile=$SYNC_DIR/inclusive/step1.root &> $SYNC_DIR/inclusive/log_step1.txt &
echo "Exclusive sample"
time cmsRun $CFG $OPTS inputFiles_load=$STPOL_DIR/sync/exclusive/files.txt outputFile=$SYNC_DIR/exclusive/step1.root &> $SYNC_DIR/exclusive/log_step1.txt &
