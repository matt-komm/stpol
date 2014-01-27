#!/bin/bash

SYSTEMATIC="
tchan 
wzjets
other
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
INPUTHIST="/home/fynu/mkomm/mu__cos_theta__mva_0_06/data.root"
RESPONSEMATRIX="/home/fynu/mkomm/mu__cos_theta__mva_0_06/matrix.root:matrix"
FITRESULT="/home/fynu/mkomm/mu__cos_theta__mva_0_06/fitresult.txt"
REGSCALE=3.0
nice -n 10 python run.py \
--output="muon/sys_nominal" \
--modelName="nominal" \
--histFile=$INPUTHIST \
--responseMatrix=$RESPONSEMATRIX \
--fitResult=$FITRESULT \
--scaleRegularization=$REGSCALE \
-f &
sleep 1s

for sys in $SYSTEMATIC
do
    nice -n 10 python run.py \
    --output="muon/sys_"$sys \
    --modelName="sys_"$sys \
    --histFile=$INPUTHIST \
    --responseMatrix=$RESPONSEMATRIX \
    --fitResult=$FITRESULT \
    --excludeSys=$sys \
    --scaleRegularization=$REGSCALE \
    -f &
    sleep 1s
done

nice -n 10 python run.py \
--output="muon/sys_mcstat" \
--modelName="sys_mcstat" \
--histFile=$INPUTHIST \
--responseMatrix=$RESPONSEMATRIX \
--fitResult=$FITRESULT \
--noMCUncertainty \
--scaleRegularization=$REGSCALE \
-f &
sleep 1s

nice -n 10 python run.py \
--output="muon/sys_stat" \
--modelName="sys_stat" \
--histFile=$INPUTHIST \
--responseMatrix=$RESPONSEMATRIX \
--fitResult=$FITRESULT \
--noStatUncertainty \
--scaleRegularization=$REGSCALE \
-f &
sleep 1s

nice -n 10 python run.py \
--includeSys="" \
--output="muon/sys_totalsys" \
--modelName="sys_totalsys" \
--histFile=$INPUTHIST \
--responseMatrix=$RESPONSEMATRIX \
--fitResult=$FITRESULT \
--noMCUncertainty \
--scaleRegularization=$REGSCALE \
-f &
sleep 1s

nice -n 10 python run.py \
--runOnData \
--includeSys="" \
--output="muon/muon_data" \
--modelName="muon_data" \
--histFile=$INPUTHIST \
--responseMatrix=$RESPONSEMATRIX \
--fitResult=$FITRESULT \
--noMCUncertainty \
--scaleRegularization=$REGSCALE \
-f &
sleep 1s

