#!/bin/bash

echo "$0: $@"
usage() {
    echo "$0 NLINES INFILE OUTDIR 'step3_cfg.py args'"
    exit 1
}
if [ ! -f $2 ]; then
    echo "Input file $2 does not exist"
    exit 1
fi
NLINES=$1
INFILE=`readlink -f $2`
OUTDIR=$3
CONF="${*:4}"

mkdir -p $OUTDIR
OUTDIR=`readlink -f $OUTDIR`
cd $OUTDIR
echo $0 $@ > $OUTDIR/job

if [[ ! -s $INFILE ]]; then
    echo "Input file is empty, exiting!"
    exit 0
fi

#split input file into N-line pieces
split $INFILE -a4 -l $NLINES -d
for file in x*
do
    echo "Submitting step3 job $CONF on file $file"

#save the task
    CMD="sbatch -p cms,phys,ied,prio $STPOL_DIR/analysis_step3/run_step3_eventloop.sh `readlink -f $file` $OUTDIR $CONF > task_$file"

#try to submit until successfully submitted
    until `eval $CMD`
    do 
        echo "ERROR!: could not submit slurm job on file $file, retrying after sleep..." >&2
        sleep 1
    done 
done
