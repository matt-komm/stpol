#!/bin/bash

if [ -z "$1" ]
then
    echo "Usage: $0 step2_output_dir"
    exit 1
fi

for i in `find $1 -type d`
do
    foldername=`basename $i`
    i=`readlink -f $i` 
    find $i -name "*.root" | $STPOL_DIR/util/dedupe.py | $STPOL_DIR/util/prependPrefix.py file:
done
