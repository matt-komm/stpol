#!/bin/bash

if [ -z "$RUN" ]; then
    echo "Need to set RUN"
    exit 1
fi  

julia="/home/joosep/local-sl6/julia/julia"

mkdir $RUN

$julia sub.jl $RUN/iso iso.txt
#$julia sub.jl $RUN/data data.txt
#$julia sub.jl $RUN/tchan tchan_new.txt
#$julia sub.jl $RUN/wjets wjets_new.txt
#$julia sub.jl $RUN/ttjets ttjets.txt
