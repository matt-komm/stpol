#!/bin/bash
CFG=$STPOL_DIR/CMSSW_5_3_11/src/SingleTopPolarization/Analysis/python/runconfs/step2/step2.py 
JOBNAME=`basename $1`
JOBNAME="${JOBNAME%.*}"

mkdir $JOBNAME
COUNTER=0

for line in `cat $1 | ./chunk.py`
do
    cd $JOBNAME
    echo sbatch ../cmsRun.sh $CFG isMC=True subChannel=WJets inputFiles=$line > job_$COUNTER
    cd ..

    COUNTER=$((COUNTER + 1))
done
