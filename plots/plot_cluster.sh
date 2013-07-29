#!/bin/bash
cd $STPOL_DIR
source setenv.sh
time python $STPOL_DIR/control_plots/all_plots/make_all_plots.py $@
