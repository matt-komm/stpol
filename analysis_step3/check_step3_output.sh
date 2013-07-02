#!/bin/bash

dir=$1

echo "total split files"
find $dir -name "x*" -type f | wc -l
echo "total slurm jobs started"
find $dir -name "*.out" -type f | wc -l
echo "total slurm jobs successfully finished"
find $dir -name "*.out" -type f -exec grep "processing speed" {} \; | wc -l
echo "total slurm jobs with error"
$STPOL_DIR/analysis_step3/failed_tasks.sh $dir
