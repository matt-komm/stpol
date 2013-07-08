#!/bin/bash

if [ -z "$1" ]
then
    echo "Usage: $0 step2_input_dir step2_output_dir - creates the whole structure of input in output"
    exit 1
fi

for iso in "Iso" "antiIso"
do
    for syst in `find $1/$iso -maxdepth 1 -name '*' -type d`
    do   
        if [ "$syst" = "$1/$iso" ]
        then continue 
        fi
        echo "syst $syst"
            
        length=`expr length $1`
        length2=`expr length $syst`
        out_dir=$2/${syst:$length+1}
        mkdir -p $out_dir
        for i in `find $syst -maxdepth 1 -name '*' -type d`
        do
            if [ "$syst" = "$i" ]
                then continue 
            fi
            out_file=$2/${i:$length+1}.txt
            #echo "out_dir $out_dir"
            echo "out_file $out_file"
            find $i -name "*.root" | $CMSSW_BASE/../util/dedupe.py | $CMSSW_BASE/../util/prependPrefix.py file: > $out_file
        done
    done
done
