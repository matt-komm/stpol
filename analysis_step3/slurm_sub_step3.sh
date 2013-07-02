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
echo $0 $@ > $OUTDIR/job

#split input file into N-line pieces
split $INFILE -a4 -l 50 -d
for file in x*
do
    echo "Submitting step3 job $CONF on file $file"
    echo sbatch -x comp-d-[094] -p main $STPOL_DIR/analysis_step3/run_step3_eventloop.sh `readlink -f $file` $OUTDIR $CONF > task_$file
    until sbatch -x comp-d-[094] -p main $STPOL_DIR/analysis_step3/run_step3_eventloop.sh `readlink -f $file` $OUTDIR $CONF
    do 
        echo "ERROR!: could not submit slurm job on file $file, retrying after sleep..." >&2
        sleep 20
    done 
done
