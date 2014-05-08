#!/bin/bash
CFG=$STPOL_DIR/CMSSW_5_3_11/src/SingleTopPolarization/GenLevelCosThetaStudy/geninfoproducer_cfg.py
JOBNAME=`basename $1`
JOBNAME="${JOBNAME%.*}"
JOBNAME="WD_"$JOBNAME
mkdir $JOBNAME
COUNTER=0

for line in `cat $1 | $STPOL_DIR/src/batch_step2/chunk.py`
do
    cd $JOBNAME
    echo sbatch -p prio,cms,ied,phys $STPOL_DIR/src/batch_step2/cmsRun.sh $CFG inputFiles=$line > job_$COUNTER
    cd ..

    COUNTER=$((COUNTER + 1))
done
