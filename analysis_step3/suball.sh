#!/bin/bash
echo "$0: $@"

NLINES=$1
CONFSCRIPT="$CMSSW_BASE/src/SingleTopPolarization/Analysis/python/runconfs/step3/base_nocuts.py $2"
OFDIR=`readlink -f $3`
INFILES="${*:4}"
if [ -z "$OFDIR" ]
then
    echo "Usage: $0 NLINES 'args-for-pycfg' OFDIR INFILES"
    exit 1
fi
echo "conf=($CONFSCRIPT)"
echo "Output directory: $OFDIR"
echo "Input files: $INFILES"
WD=$STPOL_DIR
SUBSCRIPT=$WD/analysis_step3/slurm_sub_step3.sh
for infile in $INFILES
do
    echo "Submitting job for $infile"
    fullpath=$(readlink -f $infile)
    filename=$(basename $infile)
    channel="${filename%.*}"
    mkdir $OFDIR/$channel
    CMD='$SUBSCRIPT $NLINES "$fullpath" "$OFDIR/$channel" "$CONFSCRIPT"'
    echo $CMD > $OFDIR/$channel/job
    eval `$CMD`
done
