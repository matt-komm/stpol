#!/bin/bash
#Resubmits the step3 job based on the failed slurm-JOBID.out file as the argument
if [ -z "$1" ]; then
    echo "Usage: $0 /path/to/failed/slurm-12345.out"
    echo "This script will look for the x* file in the slurm.out and resubmit the task based on the corresponding task_x*"
    exit 1
fi
infile=`readlink -f $1`
TASKCODE=$(grep "Input file is" $infile | grep -oe "x[0-9]*")
JOBID=$(grep "SLURM job ID" $infile | grep -oe "=[0-9]*")
JOBID=${JOBID:1}
basedir=$(dirname $infile)
rm $basedir/*$JOBID*
SUBCMD=`cat $basedir/task_$TASKCODE`
cd $basedir
eval $SUBCMD
