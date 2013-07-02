#!/bin/bash
echo "sync step2"

echo "inclusive"
(cmsRun $STPOL_DIR/runconfs/step2_newCmdLine_cfg.py inputFiles=file:$STPOL_DIR/sync/inclusive/step1_noSkim.root doDebug=True channel=signal subChannel=T_t outputFile=$STPOL_DIR/sync/inclusive/step2.root) &> $STPOL_DIR/sync/inclusive/log_step2.txt
echo "exclusive"
(cmsRun $STPOL_DIR/runconfs/step2_newCmdLine_cfg.py inputFiles=file:$STPOL_DIR/sync/exclusive/step1_noSkim.root channel=signal subChannel=T_t outputFile=$STPOL_DIR/sync/exclusive/step2.root) &> $STPOL_DIR/sync/exclusive/log_step2.txt
echo "step2 done"
