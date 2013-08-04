#!/bin/bash
#Submits the analysis plots into the cluster, putting the output into the default output of OutputFolder
#which is at the moment out/plots
CMD=$STPOL_DIR/control_plots/all_plots/make_all_plots.py
python $STPOL_DIR/plots/common/plot_defs.py | while read line
do
    sbatch -p short $CMD -p $line --cluster -i ~joosep/singletop/stpol/Aug4_c6a4b11_puw
done
