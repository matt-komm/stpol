#!/bin/bash

INPUTFOLDERS="
mu__cos_theta__mva_0_0
mu__cos_theta__mva_0_25
mu__cos_theta__mva_0_5
"

FITRESULT="/home/fynu/mkomm/stpol/auto_unfold/fitresultS.txt"
REGSCALE=1.0


for folder in $INPUTFOLDERS
do
    INPUTHIST="/home/fynu/mkomm/histos_bins_6_12/"$folder"/data.root"
    RESPONSEMATRIX="/home/fynu/mkomm/histos_bins_6_12/"$folder"/rebinned.root:matrixEff"
    rm -rf "muon/mctest/"$folder
    mkdir "muon/mctest/"$folder
    
    nice -n 10 python run.py \
    --output="muon/mctest/"$folder"/total" \
    --modelName="total" \
    --histFile=$INPUTHIST \
    --responseMatrix=$RESPONSEMATRIX \
    --fitResult=$FITRESULT \
    --scaleRegularization=$REGSCALE \
    -f &
    sleep 1s
    
    nice -n 10 python run.py \
    --includeSys="" \
    --output="muon/mctest/"$folder"/sysonly" \
    --modelName="sysonly" \
    --histFile=$INPUTHIST \
    --responseMatrix=$RESPONSEMATRIX \
    --fitResult=$FITRESULT \
    --scaleRegularization=$REGSCALE \
    -f &
    sleep 1s
    
    nice -n 10 python run.py \
    --output="muon/mctest/"$folder"/statonly" \
    --modelName="statonly" \
    --histFile=$INPUTHIST \
    --responseMatrix=$RESPONSEMATRIX \
    --fitResult=$FITRESULT \
    --scaleRegularization=$REGSCALE \
    --noStatUncertainty \
    -f &
    sleep 1s
    
    nice -n 10 python run.py \
    --output="muon/mctest/"$folder"/mconly" \
    --modelName="mconly" \
    --histFile=$INPUTHIST \
    --responseMatrix=$RESPONSEMATRIX \
    --fitResult=$FITRESULT \
    --scaleRegularization=$REGSCALE \
    --noMCUncertainty \
    -f &
    sleep 25s
done


