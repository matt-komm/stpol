#!/bin/bash
echo "DEPRECATED: You may want to use utils/haddDirs.sh out_step3_ to recursively hadd all the stuff in your step3 output"
exit 1

INDIR=$1
if [ -z "$INDIR" ]; then echo "Usage: $0 INDIR"; exit 1; fi

for d in $INDIR/*
do
    INFILES=`find $d -name "*.root"`
    hadd $d".root" $INFILES 
done
