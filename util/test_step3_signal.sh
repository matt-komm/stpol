#!/bin/bash
echo "Running step3 test"
cd "$STPOL_DIR"
source setenv.sh
OFDIR="$STPOL_DIR"/testing/step3/signal
TESTFILE=filelists/Aug1_5a0165/step2/mc/iso/nominal/Jul15/T_t_ToLeptons.txt
if [ -d "$OFDIR" ]; then
    echo "removing '"$OFDIR"'"
    rm -Rf "$OFDIR"
fi
mkdir -p "$OFDIR"
echo "Calling ""$CMSSW_BASE"/bin/"$SCRAM_ARCH"/Step3_EventLoop with output to $OFDIR
#head -n5  $TESTFILE |  $CMSSW_BASE/bin/$SCRAM_ARCH/Step3_EventLoop $CMSSW_BASE/src/SingleTopPolarization/Analysis/python/runconfs/step3/test.py --doControlVars --isMC --outputFile=$OFDIR/out.root --generator=powheg &> $OFDIR/log_step3.txt
echo "/hdfs/cms/store/user/joosep/Sep6_760158_powheg_genparticles/iso/nominal/Tbar_t_ToLeptons/output_2_1_caa.root" | $CMSSW_BASE/bin/$SCRAM_ARCH/Step3_EventLoop $CMSSW_BASE/src/SingleTopPolarization/Analysis/python/runconfs/step3/test.py --doControlVars --isMC --outputFile=$OFDIR/out.root --generator=powheg &> $OFDIR/log_step3.txt
tail -n10 "$OFDIR"/log_step3.txt
