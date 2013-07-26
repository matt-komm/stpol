#!/bin/bash
#This script will take the out_step3 folder and generate merged the trees from all the subdirectories
#Use as haddDirs.sh /path/to/out_step3/

files=`find $1 -name "*.root" -exec dirname {} \; | sort | uniq`

for f in $files
do
    if [[ ! -f $f.root ]]; then
        hadd $f.root $f/out*.root
    fi
done
