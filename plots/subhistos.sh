#!/bin/bash
WD="hists_"`git rev-parse HEAD`
mkdir $WD
cd $WD

for i in `find $1 -type f -name "*.root"`
do
    sbatch -p cms,ied,phys,prio $STPOL_DIR/plots/makehistos.sh $i
done
