#!/bin/bash
for i in `find $1 -type f -name "*.root"`
do
    j=`uuidgen`
    SLURM_JOBID=local-$j $STPOL_DIR/plots/makehistos.sh $i &> local-$j.out &
    echo $i 
    sleep 2
done
