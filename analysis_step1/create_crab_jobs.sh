#!/bin/bash
TAG=`git rev-parse HEAD`
timestamp=`eval date +%m_%d`_$TAG

python $STPOL_DIR/util/datasets.py -t stpol_step1_$timestamp -T $STPOL_DIR/crabs/crab_MC_step1.cfg -d S1_MC -o $STPOL_DIR/crabs/step1_MC_$timestamp
python $STPOL_DIR/util/datasets.py -t stpol_step1_$timestamp -T $STPOL_DIR/crabs/crab_MC_step1_glideInRemote.cfg -d S1_MC_syst -o $STPOL_DIR/crabs/step1_MC_syst_$timestamp
python $STPOL_DIR/util/datasets.py -t stpol_step1_$timestamp -T $STPOL_DIR/crabs/crab_Data_step1_glideInRemote.cfg -d S1_D -o $STPOL_DIR/crabs/step1_Data_$timestamp

