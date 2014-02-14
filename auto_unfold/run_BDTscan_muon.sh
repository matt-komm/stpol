#!/bin/bash


INPUTFOLDERS="
-0.00000  -0.07000  -0.14000  0.01000  0.08000  0.16000  0.23000  0.30000  0.37000  0.44000
-0.01000  -0.08000  -0.15000  0.02000  0.09000  0.17000  0.24000  0.31000  0.38000  0.45000
-0.02000  -0.09000  -0.16000  0.03000  0.10000  0.18000  0.25000  0.32000  0.39000  0.46000
-0.03000  -0.10000  -0.17000  0.04000  0.11000  0.19000  0.26000  0.33000  0.40000  0.47000
-0.04000  -0.11000  -0.18000  0.05000  0.13000  0.20000  0.27000  0.34000  0.41000  0.48000
-0.05000  -0.12000  -0.19000  0.06000  0.14000  0.21000  0.28000  0.35000  0.42000  0.49000
-0.06000  -0.13000  -0.20000  0.07000  0.15000  0.22000  0.29000  0.36000  0.43000  0.50000
"

INPUTFOLDERS="
-0.20000
-0.15000
-0.10000
-0.05000
-0.00000
0.05000
0.10000
0.15000
0.20000
0.25000
0.30000
0.35000
0.40000
0.45000
0.50000
"
FITRESULT="/home/fynu/mkomm/scanned_hists_feb10/fitResultMuon.txt"
REGSCALE=1.0

for folder in $INPUTFOLDERS
do
    INPUTHIST="/home/fynu/mkomm/scanned_hists_feb10/hists/"$folder"/mu/cos_theta_lj.root"
    RESPONSEMATRIX="/home/fynu/mkomm/scanned_hists_feb10/hists/"$folder"/tmatrix_nocharge.root:tm__pdgid_13__nominal"
    rm -rf "muon/scan/"$folder
    mkdir "muon/scan/"$folder
    
    nice -n 10 python run.py \
    --output="muon/scan/"$folder"/total" \
    --modelName="total" \
    --histFile=$INPUTHIST \
    --responseMatrix=$RESPONSEMATRIX \
    --fitResult=$FITRESULT \
    --scaleRegularization=$REGSCALE \
    --noMCUncertainty \
    -f &
    sleep 5s
    
    nice -n 10 python run.py \
    --includeSys="" \
    --output="muon/scan/"$folder"/sysexcl" \
    --modelName="sysexcl" \
    --histFile=$INPUTHIST \
    --responseMatrix=$RESPONSEMATRIX \
    --fitResult=$FITRESULT \
    --scaleRegularization=$REGSCALE \
    --noMCUncertainty \
    -f &
    sleep 5s
    
    nice -n 10 python run.py \
    --output="muon/scan/"$folder"/statexcl" \
    --modelName="statexcl" \
    --histFile=$INPUTHIST \
    --responseMatrix=$RESPONSEMATRIX \
    --fitResult=$FITRESULT \
    --scaleRegularization=$REGSCALE \
    --noStatUncertainty \
    --noMCUncertainty \
    -f &
    sleep 5s
    
    nice -n 10 python run.py \
    --output="muon/scan/"$folder"/mcexcl" \
    --modelName="mcexcl" \
    --histFile=$INPUTHIST \
    --responseMatrix=$RESPONSEMATRIX \
    --fitResult=$FITRESULT \
    --scaleRegularization=$REGSCALE \
    --noMCUncertainty \
    -f &
    sleep 5s
    
    nice -n 10 python run.py \
    --output="muon/scan/"$folder"/nosys" \
    --modelName="nosys" \
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


