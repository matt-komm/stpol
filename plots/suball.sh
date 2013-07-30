#!/bin/bash
#Submits the analysis plots into the cluster, putting the output into the default output of OutputFolder
#which is at the moment out/plots
CMD=$STPOL_DIR/control_plots/all_plots/make_all_plots.py
python $STPOL_DIR/plots/common/plot_defs.py | while read line
do
    sbatch -p short $CMD -p $line --cluster -i ~mario/Summer13/stpol/Step3_Jul26
done
