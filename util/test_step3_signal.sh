#!/bin/bash
echo "Running step3 test"
cd "$STPOL_DIR"
source setenv.sh
OFDIR="$STPOL_DIR"/testing/step3/signal
if [ -d "$OFDIR" ]; then
    echo "removing '"$OFDIR"'"
    rm -Rf "$OFDIR"
fi
mkdir -p "$OFDIR"
echo "Calling ""$CMSSW_BASE"/bin/"$SCRAM_ARCH"/Step3_EventLoop
head -n5 filelists/step2/latest/iso/nominal/mc/T_t_ToLeptons.txt |  "$CMSSW_BASE"/bin/"$SCRAM_ARCH"/Step3_EventLoop "$CMSSW_BASE""/src/SingleTopPolarization/Analysis/python/runconfs/step3/test.py" --doControlVars --isMC --outputFile="$OFDIR"/out.root --cutString="mu_pt>50 && abs(eta_lj)>2.5" &> "$OFDIR"/log_step3.txt
tail -n10 "$OFDIR"/log_step3.txt
