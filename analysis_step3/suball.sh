#!/bin/bash
echo "$0: $@"

CONFSCRIPT="$CMSSW_BASE/src/SingleTopPolarization/Analysis/python/runconfs/step3/base_nocuts.py $1"
OFDIR=`readlink -f $2`
INFILES="${*:3}"
if [ -z "$OFDIR" ]
then
    echo "Usage: $0 'args-for-pycfg' OFDIR INFILES"
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
    echo $SUBSCRIPT "$fullpath" "$OFDIR/$channel" "$CONFSCRIPT" > $OFDIR/$channel/job 
    $SUBSCRIPT "$fullpath" "$OFDIR/$channel" "$CONFSCRIPT" 
done
