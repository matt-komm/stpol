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
OUTDIR=$2
CONF="${*:3}"

mkdir -p $OUTDIR
OUTDIR=`readlink -f $OUTDIR`
cd $OUTDIR
echo $0 $@ > $OUTDIR/job

if [[ ! -s $INFILE ]]; then
    echo "Input file is empty, exiting!"
    exit 0
fi

#split input file into N-line pieces
#Special treatment for signal and nominal samples
#Signal is produced unskimmed and contains very many events, nominal samples must run PDFs which are slow
if [[ "$INFILE" == *T_t* ]] || [[ "$INFILE" == *Tbar_t* ]]; then
    N=1;
elif [[ "$INFILE" == *nominal* ]]; then
    N=5;
else
    N=20;
fi

split $INFILE -a8 -l $N -d
for file in x*
do
    echo "Submitting step3 job $CONF on file $file"

#save the task
    CMD="sbatch -p prio,main $STPOL_DIR/analysis_step3/run_step3_eventloop.sh `readlink -f $file` $OUTDIR $CONF"
    echo $CMD > task_$file
    
#try to submit until successfully submitted
    eval $CMD
done
