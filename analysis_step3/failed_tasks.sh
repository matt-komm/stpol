#!/bin/bash
dir=$1
FAILED=$(find $dir -name "*.out" -type f -exec grep -e "step3 exit code: [^0]" {} \; -print0 | grep "out")
for f in $FAILED
do
    echo $f
done
