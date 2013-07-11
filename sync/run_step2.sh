#!/bin/bash
echo "sync step2"

echo "inclusive"
CFG=$CMSSW_BASE/src/SingleTopPolarization/Analysis/python/runconfs/step2/step2.py
OPTS="doDebug=True subChannel=T_t doSync=True"
(cmsRun $CFG inputFiles=file:$STPOL_DIR/sync/inclusive/step1_noSkim.root $OPTS outputFile=$STPOL_DIR/sync/inclusive/step2.root) &> $STPOL_DIR/sync/inclusive/log_step2.txt
echo "exclusive"
(cmsRun $CFG inputFiles=file:$STPOL_DIR/sync/exclusive/step1_noSkim.root $OPTS outputFile=$STPOL_DIR/sync/exclusive/step2.root) &> $STPOL_DIR/sync/exclusive/log_step2.txt
echo "step2 done"
