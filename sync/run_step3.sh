#!/bin/bash

echo "step3 sync"
echo "inclusive"
(echo "inclusive/step2.root" | $STPOL_DIR/CMSSW_5_3_8/bin/slc5_amd64_gcc462/Step3_EventLoop $STPOL_DIR/runconfs/step3_eventloop_sync.py --outputFile=$STPOL_DIR/sync/inclusive/step3.root) &> $STPOL_DIR/sync/inclusive/log_step3.txt
echo "exclusive"
(echo "exclusive/step2.root" | $STPOL_DIR/CMSSW_5_3_8/bin/slc5_amd64_gcc462/Step3_EventLoop $STPOL_DIR/runconfs/step3_eventloop_sync.py --outputFile=$STPOL_DIR/sync/exclusive/step3.root) &> $STPOL_DIR/sync/exclusive/log_step3.txt
echo "step3 done"
