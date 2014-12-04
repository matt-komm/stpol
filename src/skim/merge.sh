#!/bin/bash
set -e
\ls -1 /hdfs &> /dev/null
RET=$?
if [ $RET -ne 0 ]; then
    echo '/hdfs was not available'
fi
echo "!!!"
env | grep "ROOT"
#scpath=/home/joosep/Dropbox/kbfi/top/stpol/src
#mvapath=/home/joosep/Dropbox/kbfi/top/stpol/src/mva
scpath=/home/andres/single_top/stpol_pdf/src
mvapath=/home/andres/single_top/stpol_pdf/src/mva

(
    source /home/software/root_v_5_34_21/bin/thisroot.sh
    python $mvapath/adder.py bdt_sig_bg_old $mvapath/weights/stpol_bdt_sig_bg_lepton_flavour.weights.xml $FILE_NAMES
    python $mvapath/adder.py bdt_sig_bg $mvapath/weights/stpol_bdt_sig_bg_mixed_lepton_flavour.weights.xml $FILE_NAMES 
    python $mvapath/qcd_mva_adder.py $FILE_NAMES
    python $mvapath/top_13_001_mva_adder.py $FILE_NAMES
)
source /home/software/root_v_5_34_21/bin/thisroot.sh && julia $scpath/analysis/mergedf.jl /home/andres/single_top/stpol_pdf/src/step3/metadata.json $FILE_NAMES 
\ls -1 .
