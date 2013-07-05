#!/bin/bash
TAG=`git rev-parse HEAD`
timestamp=`eval date +%m_%d`_$TAG
OFDIR=$STPOL_DIR/crabs/step1_$timestamp
python $STPOL_DIR/util/datasets.py -t stpol_step1_$timestamp -T $STPOL_DIR/crabs/crab_MC_step1.cfg -d S1_MC -o $OFDIR/mc/nominal
python $STPOL_DIR/util/datasets.py -t stpol_step1_$timestamp -T $STPOL_DIR/crabs/crab_MC_step1_glideInRemote.cfg -d S1_MC_syst -o $OFDIR/mc/systematic
python $STPOL_DIR/util/datasets.py -t stpol_step1_$timestamp -T $STPOL_DIR/crabs/crab_Data_step1_glideInRemote.cfg -d S1_D -o $OFDIR/data
python $STPOL_DIR/util/datasets.py -t stpol_step1_$timestamp -T $STPOL_DIR/crabs/crab_MC_step1_glideInRemote.cfg -d S1_FSIM_WJ -o $OFDIR/mc/fastsim

