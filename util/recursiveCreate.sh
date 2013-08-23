#!/bin/bash
WD=`pwd`
for i in `find $1 -type f -name "crab_*.cfg"`
do
    DIR=$(dirname ${i})
    CFG=$(basename ${i})
    cd $DIR
    if [ -f "./SKIP" ]; then
        echo "Skipping $DIR"
        cd $WD
        continue
    fi
    crab -cfg $CFG -create
    cd $WD
done

