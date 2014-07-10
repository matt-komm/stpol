#!/bin/bash

ORIGDIR=`pwd`
for f in `find . -name "crab_*.cfg"`
do
    DIR=$(dirname ${f})
    CFG=$(basename ${f})
    cd $DIR
    WD=`cat $CFG | egrep -o "ui_working_dir = .*" | cut -f 3 -d' '`
    if [ ! -d "$WD" ]; then
        echo "Creating $DIR/$CFG"
        crab -cfg $CFG -create >> create.log 2>&1
        CREATION_CODE=$?
        echo "creation exit code: "$CREATION_CODE
        if [ $CREATION_CODE -ne 0 ]; then
            echo "ERROR creating job "$WD
        fi
        crab -c $WD -submit 500 >> create.log 2>&1
        echo "submission exit code: ", $?
    else
        echo "Skipping config $DIR/$CFG, directory $DIR/$WD exists"
    fi
    cd $ORIGDIR
done
