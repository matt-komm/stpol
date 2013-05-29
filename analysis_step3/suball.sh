#!/bin/bash
echo "$0: $@"

CONFSCRIPT="$STPOL_DIR/runconfs/step3_eventLoop_cfg.py $1"
OFDIR=`readlink -f $2`
INFILES="${*:3}"
if [ -z "$OFDIR" ]
then
    echo "Usage: $0 'args-for-pycfg' OFDIR INFILES"
    exit 1
fi
echo "Input files: $INFILES"
WD=$STPOL_DIR
SUBSCRIPT=$WD/analysis_step3/slurm_sub_step3.sh
for infile in $INFILES
do
    echo "Submitting job for $infile"
    fullpath=$(readlink -f $infile)
    filename=$(basename $infile)
    channel="${filename%.*}"
    $SUBSCRIPT "$fullpath" "$OFDIR/$channel" "$CONFSCRIPT" 
done
