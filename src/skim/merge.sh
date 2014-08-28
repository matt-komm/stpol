#!/bin/bash
set -e
\ls -1 /hdfs &> /dev/null
RET=$?
if [ $RET -ne 0 ]; then
    echo '/hdfs was not available'
fi

scpath=/home/joosep/Dropbox/kbfi/top/stpol/src
mvapath=/home/joosep/Dropbox/kbfi/top/stpol/src/mva

(
    source ~/local-sl6/root/bin/thisroot.sh
    python $mvapath/adder.py bdt_sig_bg_old $mvapath/weights/stpol_bdt_sig_bg_lepton_flavour.weights.xml $FILE_NAMES
    python $mvapath/adder.py bdt_sig_bg $mvapath/weights/stpol_bdt_sig_bg_mixed_lepton_flavour.weights.xml $FILE_NAMES 
    python $mvapath/qcd_mva_adder.py $FILE_NAMES
    python $mvapath/top_13_001_mva_adder.py $FILE_NAMES
)
~/.julia/CMSSW/julia $scpath/analysis/mergedf.jl @METADATAFILE@ $FILE_NAMES 
\ls -1 .
