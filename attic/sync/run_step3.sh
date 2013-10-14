#!/bin/bash

CMD=$STPOL_DIR/CMSSW_5_3_11/bin/slc5_amd64_gcc462/Step3_EventLoop
echo "step3 sync"
echo "inclusive"
CFG=$CMSSW_BASE/src/SingleTopPolarization/Analysis/python/runconfs/step3/base_nocuts.py

(echo "inclusive/step2.root" | $CMD $CFG --outputFile=$STPOL_DIR/sync/inclusive/step3.root) &> $STPOL_DIR/sync/inclusive/log_step3.txt
tail -n10 inclusive/log_step3.txt
echo "exclusive"
(echo "exclusive/step2.root" | $CMD $CFG --outputFile=$STPOL_DIR/sync/exclusive/step3.root) &> $STPOL_DIR/sync/exclusive/log_step3.txt
tail -n10 exclusive/log_step3.txt
echo "step3 done"
