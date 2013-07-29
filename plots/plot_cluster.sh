#!/bin/bash
source $STPOL_DIR/setenv.sh
time python $STPOL_DIR/control_plots/all_plots/make_all_plots.py $@
