#!/bin/bash

echo "$0: $@"
usage() {
    echo "$0 INFILE OUTDIR 'step3_cfg.py args'"
    exit 1
}
if [ ! -f $1 ]; then
    echo "Input file $1 does not exist"
    exit 1
fi
INFILE=`readlink -f $1`
OUTDIR=`readlink -f $2`
CONF="${*:3}"

mkdir -p $OUTDIR
cd $OUTDIR

#split input file into N-line pieces
split $INFILE -a4 -l 50 -d
for file in x*
do
    echo "Submitting step3 job $CONF on file $file"
    sbatch -x comp-d-[006,033,094] -p prio $STPOL_DIR/analysis_step3/run_step3_eventloop.sh `readlink -f $file` $OUTDIR $CONF
done
