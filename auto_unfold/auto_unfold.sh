#!/bin/bash

INPUTHIST="/home/fynu/mkomm/mu_cos_theta_mva_0_09/data.root"
RESPONSEMATRIX="/home/fynu/mkomm/mu_cos_theta_mva_0_09/matrix.root:matrix"
FITRESULT="/home/fynu/mkomm/mu_cos_theta_mva_0_09/fitresult.txt"
python run.py \
--includeSys="" \
--output="test" \
--modelName="test" \
--histFile=$INPUTHIST \
--responseMatrix=$RESPONSEMATRIX \
--fitResult=$FITRESULT \
--noMCUncertainty \
-f


