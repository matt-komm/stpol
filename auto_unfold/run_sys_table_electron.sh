#!/bin/bash

SYSTEMATIC="
tchan 
wzjets
Res
En
other
UnclusteredEn
btaggingBC
btaggingL
leptonID
leptonTrigger
wjets_flat
wjets_shape
"
INPUTHIST="/home/fynu/mkomm/ele__cos_theta__mva_0_13/data.root"
RESPONSEMATRIX="/home/fynu/mkomm/ele__cos_theta__mva_0_13/matrix.root:matrix"
FITRESULT="/home/fynu/mkomm/ele__cos_theta__mva_0_13/fitresult.txt"
REGSCALE=3.0
nice -n 10 python run.py \
--output="electron/sys_nominal" \
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
    --output="electron/sys_"$sys \
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
--output="electron/sys_mcstat" \
--modelName="sys_mcstat" \
--histFile=$INPUTHIST \
--responseMatrix=$RESPONSEMATRIX \
--fitResult=$FITRESULT \
--noMCUncertainty \
--scaleRegularization=$REGSCALE \
-f &
sleep 1s

nice -n 10 python run.py \
--output="electron/sys_stat" \
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
--output="electron/sys_totalsys" \
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
--output="electron/electron_data" \
--modelName="electron_data" \
--histFile=$INPUTHIST \
--responseMatrix=$RESPONSEMATRIX \
--fitResult=$FITRESULT \
--noMCUncertainty \
--scaleRegularization=$REGSCALE \
-f &

