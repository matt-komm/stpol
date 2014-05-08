#!/bin/bash

INFILE=`readlink -f $1`
OUTDIR=`readlink -f $2`
if [ -z "$INFILE" ]; then echo "Usage: $0 INFILE OUTDIR"; exit 1; fi
if [ -z "$OUTDIR" ]; then echo "Usage: $0 INFILE OUTDIR"; exit 1; fi
mkdir $OUTDIR
cd $OUTDIR

split $INFILE -l 100 -d
I=0
for file in x*
do
    $CMSSW_BASE/../analysis_step3/run_step3_eventloop.sh `readlink -f $file` $OUTDIR  &> "log_"$I".txt" &
    I=$(($I+1))
done
