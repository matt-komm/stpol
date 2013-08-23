#!/bin/bash
OFILE="hists-$SLURM_JOBID.root"
source $STPOL_DIR/setenv.sh
echo "Calling tree.py"
$STPOL_DIR/plots/histogramming/histo.py .$OFILE.tmp $1
mv .$OFILE.tmp $OFILE


