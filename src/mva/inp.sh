#!/bin/bash
#generated file lists

SKIM_DIR="/hdfs/local/joosep/stpol/mva/"

TAG=$1
BDT=$2

mkdir -p input/$BDT

find $SKIM_DIR/$TAG/tchan -name "*.root" > input/$BDT/sig.txt
find $SKIM_DIR/$TAG/ttjets -name "*.root" > input/$BDT/bg.txt
find $SKIM_DIR/$TAG/wjets -name "*.root" >> input/$BDT/bg.txt

#separate inclusive files
grep "/T_t/" input/$BDT/sig.txt > input/$BDT/train.txt
grep "/Tbar_t/" input/$BDT/sig.txt >> input/$BDT/train.txt
grep "/TTJets_MassiveBinDECAY/" input/$BDT/bg.txt >> input/$BDT/train.txt
grep "/WJets_inclusive/" input/$BDT/bg.txt >> input/$BDT/train.txt
