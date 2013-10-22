#!/bin/bash

if [ -z "$RUN" ]; then
    echo "Need to set RUN"
    exit 1
fi  

julia="/home/joosep/local-sl6/julia/julia"

mkdir -p $RUN

$julia sub.jl $RUN/iso_csvm iso_csvm.txt
$julia sub.jl $RUN/iso_csvt iso_csvt.txt
