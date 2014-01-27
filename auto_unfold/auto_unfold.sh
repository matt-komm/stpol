#!/bin/bash

#INPUTHIST="/home/fynu/mkomm/mu__cos_theta__mva_0_06/data.root"
#RESPONSEMATRIX="/home/fynu/mkomm/mu__cos_theta__mva_0_06/matrix.root:matrix"
#FITRESULT="/home/fynu/mkomm/mu__cos_theta__mva_0_06/fitresult.txt"
folder="mu__cos_theta__mva_0_0"
INPUTHIST="/home/fynu/mkomm/QCD_fixed/"$folder"__qcdfixed/data.root"
RESPONSEMATRIX="/home/fynu/mkomm/QCD_fixed/"$folder"__qcdfixed/rebinned_nominal.root:matrixEff"
FITRESULT="/home/fynu/mkomm/QCD_fixed/fitresult.txt"
python run.py \
--includeSys="" \
--output="test" \
--modelName="test" \
--histFile=$INPUTHIST \
--responseMatrix=$RESPONSEMATRIX \
--fitResult=$FITRESULT \
--scaleRegularization=1.0 \
--noMCUncertainty \
-f


