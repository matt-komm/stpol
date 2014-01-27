#!/bin/bash

INPUTFOLDERS="
mu__cos_theta__mva_-0_2
mu__cos_theta__mva_-0_17
mu__cos_theta__mva_-0_15
mu__cos_theta__mva_-0_12
mu__cos_theta__mva_-0_1
mu__cos_theta__mva_-0_07
mu__cos_theta__mva_-0_05
mu__cos_theta__mva_-0_02
mu__cos_theta__mva_0_0
mu__cos_theta__mva_0_02
mu__cos_theta__mva_0_05
mu__cos_theta__mva_0_07
mu__cos_theta__mva_0_1
mu__cos_theta__mva_0_12
mu__cos_theta__mva_0_15
mu__cos_theta__mva_0_17
mu__cos_theta__mva_0_2
mu__cos_theta__mva_0_22
mu__cos_theta__mva_0_25
mu__cos_theta__mva_0_27
mu__cos_theta__mva_0_3
mu__cos_theta__mva_0_32
mu__cos_theta__mva_0_35
mu__cos_theta__mva_0_37
mu__cos_theta__mva_0_4
mu__cos_theta__mva_0_42
mu__cos_theta__mva_0_45
mu__cos_theta__mva_0_47
mu__cos_theta__mva_0_5
"


INPUTFOLDERS="mu__cos_theta__mva_-0_4 mu__cos_theta__mva_-0_3 mu__cos_theta__mva_-0_2 mu__cos_theta__mva_-0_1 mu__cos_theta__mva_0_0 mu__cos_theta__mva_0_1 mu__cos_theta__mva_0_2 mu__cos_theta__mva_0_3 mu__cos_theta__mva_0_4 mu__cos_theta__mva_0_5"
FITRESULT="/home/fynu/mkomm/QCD_fixed/fitresult.txt"
REGSCALE=1.0

for folder in $INPUTFOLDERS
do
    INPUTHIST="/home/fynu/mkomm/QCD_fixed/"$folder"__qcdfixed/data.root"
    RESPONSEMATRIX="/home/fynu/mkomm/QCD_fixed/"$folder"__qcdfixed/rebinned_nominal.root:matrixEff"
    rm -rf "muon/scan/"$folder
    mkdir "muon/scan/"$folder
    
    nice -n 10 python run.py \
    --output="muon/scan/"$folder"/total" \
    --modelName="total" \
    --histFile=$INPUTHIST \
    --responseMatrix=$RESPONSEMATRIX \
    --fitResult=$FITRESULT \
    --scaleRegularization=$REGSCALE \
    -f &
    sleep 1s
    
    nice -n 10 python run.py \
    --includeSys="" \
    --output="muon/scan/"$folder"/sysonly" \
    --modelName="sysonly" \
    --histFile=$INPUTHIST \
    --responseMatrix=$RESPONSEMATRIX \
    --fitResult=$FITRESULT \
    --scaleRegularization=$REGSCALE \
    -f &
    sleep 1s
    
    nice -n 10 python run.py \
    --output="muon/scan/"$folder"/statonly" \
    --modelName="statonly" \
    --histFile=$INPUTHIST \
    --responseMatrix=$RESPONSEMATRIX \
    --fitResult=$FITRESULT \
    --scaleRegularization=$REGSCALE \
    --noStatUncertainty \
    -f &
    sleep 1s
    
    nice -n 10 python run.py \
    --output="muon/scan/"$folder"/mconly" \
    --modelName="mconly" \
    --histFile=$INPUTHIST \
    --responseMatrix=$RESPONSEMATRIX \
    --fitResult=$FITRESULT \
    --scaleRegularization=$REGSCALE \
    --noMCUncertainty \
    -f &
    sleep 1s
    
    nice -n 10 python run.py \
    --output="muon/scan/"$folder"/nothing" \
    --modelName="nothing" \
    --includeSys="" \
    --histFile=$INPUTHIST \
    --responseMatrix=$RESPONSEMATRIX \
    --fitResult=$FITRESULT \
    --scaleRegularization=$REGSCALE \
    --noMCUncertainty \
    --noStatUncertainty \
    -f &
    
    sleep 10s
done


