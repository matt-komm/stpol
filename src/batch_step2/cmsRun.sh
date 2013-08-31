#!/bin/bash
source $STPOL_DIR/setenv.sh
OFILE=out_$SLURM_JOBID.root
cmsRun $@ outputFile=$OFILE
