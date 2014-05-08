#!/bin/bash
CFG=$STPOL_DIR/CMSSW_5_3_11/src/SingleTopPolarization/Analysis/python/runconfs/step2/step2.py 
JOBNAME=`basename $1`
JOBNAME="${JOBNAME%.*}"
JOBNAME="WD_"$JOBNAME
mkdir $JOBNAME
COUNTER=0

for line in `cat $1 | $STPOL_DIR/src/batch_step2/chunk.py`
do
    cd $JOBNAME
    echo sbatch $STPOL_DIR/src/batch_step2/cmsRun.sh $CFG isMC=True subChannel=WJets inputFiles=$line > job_$COUNTER
    cd ..

    COUNTER=$((COUNTER + 1))
done
