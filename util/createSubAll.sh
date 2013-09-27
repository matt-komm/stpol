#!/bin/bash

for f in *.cfg
do
	crab -cfg $f -create
    WD=`cat $f | egrep -o "ui_working_dir = .*" | cut -f 3 -d' '`
    crab -c $WD -submit 500
done

for f in WD_*
do
    for i in {1..3}
    do
        crab -c $f -submit 500
        if [ $? -ne 0 ]; then break; fi
    done
done
