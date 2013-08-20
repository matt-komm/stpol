#!/bin/bash

SYSTEMATIC="
tchan 
wzjets
top
qcd
Res
En
UnclusteredEn
btaggingBC
btaggingL
leptonID
leptonIso
leptonTrigger
wjets_flat
wjets_shape
"
INPUTHIST="/home/fynu/mkomm/mu_cos_theta_mva_0_09/data.root"
RESPONSEMATRIX="/home/fynu/mkomm/mu_cos_theta_mva_0_09/matrix.root:matrix"
FITRESULT="/home/fynu/mkomm/mu_cos_theta_mva_0_09/fitresult.txt"
python run.py \
--output="muon/sys_nominal" \
--modelName="nominal" \
--histFile=$INPUTHIST \
--responseMatrix=$RESPONSEMATRIX \
--fitResult=$FITRESULT \
-f &
sleep 1s

for sys in $SYSTEMATIC
do
    python run.py \
    --output="muon/sys_"$sys \
    --modelName="sys_"$sys \
    --histFile=$INPUTHIST \
    --responseMatrix=$RESPONSEMATRIX \
    --fitResult=$FITRESULT \
    --excludeSys=$sys \
    -f &
    sleep 1s
done

python run.py \
--output="muon/sys_mcstat" \
--modelName="sys_mcstat" \
--histFile=$INPUTHIST \
--responseMatrix=$RESPONSEMATRIX \
--fitResult=$FITRESULT \
--noMCUncertainty \
-f &
sleep 1s

python run.py \
--output="muon/sys_stat" \
--modelName="sys_stat" \
--histFile=$INPUTHIST \
--responseMatrix=$RESPONSEMATRIX \
--fitResult=$FITRESULT \
--noStatUncertainty \
-f &
sleep 1s

python run.py \
--includeSys="" \
--output="muon/sys_totalsys" \
--modelName="sys_totalsys" \
--histFile=$INPUTHIST \
--responseMatrix=$RESPONSEMATRIX \
--fitResult=$FITRESULT \
--noMCUncertainty \
-f &
sleep 1s

