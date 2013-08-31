#!/bin/bash

for fi in `find $STPOL_DIR/filelists/Jul10_5a56de/step1/mc/wjets_FSIM_Summer12/ -name "*.txt"`
do
    $STPOL_DIR/src/batch_step2/step2.sh $fi
done
