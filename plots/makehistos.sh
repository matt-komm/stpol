#!/bin/bash
OFILE="hists-$SLURM_JOBID.root"
source $STPOL_DIR/setenv.sh
echo "Calling tree.py"
$STPOL_DIR/CMSSW_5_3_11/src/SingleTopPolarization/Analysis/python/tree.py $1 .$OFILE.tmp
mv .$OFILE.tmp $OFILE


