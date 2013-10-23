#!/bin/bash
#set -e #Abort if errors
uname -a
set -e
unset DISPLAY
echo "SLURM job ID="$SLURM_JOBID
WD=$STPOL_DIR
INFILE=$1
OUTDIR=$2
CONF="${*:3}"

OFNAME=$SLURM_JOB_ID
if [ -z $OFNAME ]
then
    OFNAME=`python -c 'import uuid; print uuid.uuid1()'`
fi

cd $WD
source setenv.sh
for i in `seq 1 5`;
        do
                echo "checking for /hdfs, try "$i
                ls /hdfs
                if [ $? -gt 0 ]; then
                    echo `date`" ERROR could not see /hdfs"
                    tail -n10 /tmp/health.check
                    sleep 60 
                else
                    echo `date`" /hdfs was seen"
                    break
                fi
        done    

cd $OUTDIR
echo $CONF
echo "Input file is "$INFILE
cat $INFILE | $CMSSW_BASE/bin/slc5_amd64_gcc462/Step3_EventLoop $CONF --outputFile=out_step3_$OFNAME.root
cd $STPOL_DIR/mvatools
echo "Adding MVA"
./addMVAasFriend.py -f $OUTDIR/out_step3_$OFNAME.root
cd $WD
SAMPNAME="${INFILE##*.}"
echo "step3 exit code: "$?
