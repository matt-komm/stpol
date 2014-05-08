#!/bin/bash
#This script will take the out_step3 folder and generate merged the trees from all the subdirectories
#Use as haddDirs.sh /path/to/out_step3/

find $1 -name "*.root" -exec dirname {} \; | sort | uniq | $STPOL_DIR/local/bin/parallel hadd -O -f9 {}.root {}/out*.root 


#for f in $files
#do
#    if [[ ! -f $f.root ]]; then
#        hadd -O -f9 $f.root $f/out*.root
#    fi
#done
