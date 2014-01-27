#!/bin/bash

INPUTFOLDERS="
mu__cos_theta__mva_0_0
mu__cos_theta__mva_0_05
mu__cos_theta__mva_0_1
mu__cos_theta__mva_0_15
mu__cos_theta__mva_0_2
mu__cos_theta__mva_0_25
mu__cos_theta__mva_0_3
mu__cos_theta__mva_0_35
mu__cos_theta__mva_0_4
mu__cos_theta__mva_0_45
mu__cos_theta__mva_0_5
"
FITRESULT="/home/fynu/mkomm/histos_bins_6_12/fitresult.txt"
REGSCALE=3.0


for folder in $INPUTFOLDERS
do
    INPUTHIST="/home/fynu/mkomm/histos_bins_6_12/"$folder"/data.root"
    RESPONSEMATRIX="/home/fynu/mkomm/histos_bins_6_12/"$folder"/rebinned.root:matrixEff"
    rm -rf "muon/scansignal/"$folder
    mkdir "muon/scansignal/"$folder
    
    nice -n 10 python run.py \
    --output="muon/scansignal/"$folder"/total" \
    --modelName="total" \
    --histFile=$INPUTHIST \
    --responseMatrix=$RESPONSEMATRIX \
    --fitResult=$FITRESULT \
    --scaleRegularization=$REGSCALE \
    --noBackground \
    -f &
    sleep 1s
    
    nice -n 10 python run.py \
    --includeSys="" \
    --output="muon/scansignal/"$folder"/sysonly" \
    --modelName="sysonly" \
    --histFile=$INPUTHIST \
    --responseMatrix=$RESPONSEMATRIX \
    --fitResult=$FITRESULT \
    --scaleRegularization=$REGSCALE \
    --noBackground \
    -f &
    sleep 1s
    
    nice -n 10 python run.py \
    --output="muon/scansignal/"$folder"/statonly" \
    --modelName="statonly" \
    --histFile=$INPUTHIST \
    --responseMatrix=$RESPONSEMATRIX \
    --fitResult=$FITRESULT \
    --scaleRegularization=$REGSCALE \
    --noStatUncertainty \
    --noBackground \
    -f &
    sleep 1s
    
    nice -n 10 python run.py \
    --output="muon/scansignal/"$folder"/mconly" \
    --modelName="mconly" \
    --histFile=$INPUTHIST \
    --responseMatrix=$RESPONSEMATRIX \
    --fitResult=$FITRESULT \
    --scaleRegularization=$REGSCALE \
    --noMCUncertainty \
    --noBackground \
    -f &
    sleep 25s
done


