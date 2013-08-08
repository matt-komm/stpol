#!/bin/bash

SYSTEMATIC="
tchan 
wzjets
top
qcd
En
Res
UnclusteredEn
btaggingBC
btaggingL
wjets_flat
wjets_shape
ttbar_scale
ttbar_matching
"
INPUTHIST="/home/fynu/mkomm/mu_cos_theta_mva_0_09/data.root"
RESPONSEMATRIX="/home/fynu/mkomm/mu_cos_theta_mva_0_09/matrix.root:matrix"
FITRESULT="/home/fynu/mkomm/mu_cos_theta_mva_0_09/fitresult.txt"
python run.py \
--modelName="nominal" \
--histFile=$INPUTHIST \
--responseMatrix=$RESPONSEMATRIX \
--fitResult=$FITRESULT \
-f &
sleep 1s

for sys in $SYSTEMATIC
do
    INPUTHIST="/home/fynu/mkomm/mu_cos_theta_mva_0_09/data.root"
    RESPONSEMATRIX="/home/fynu/mkomm/mu_cos_theta_mva_0_09/matrix.root:matrix"
    FITRESULT="/home/fynu/mkomm/mu_cos_theta_mva_0_09/fitresult.txt"
    python run.py \
    --modelName="sys_"$sys \
    --histFile=$INPUTHIST \
    --responseMatrix=$RESPONSEMATRIX \
    --fitResult=$FITRESULT \
    --excludeSys=$sys \
    -f &
    sleep 1s
done

