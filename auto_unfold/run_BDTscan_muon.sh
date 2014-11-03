#!/bin/bash


INPUTFOLDERS="
0.01000  -0.12000  0.02000  0.13000  0.24000  0.35000  0.46000  0.57000  0.68000  0.79000  0.90000
-0.02000  -0.13000  0.03000  0.14000  0.25000  0.36000  0.47000  0.58000  0.69000  0.80000  0.91000
-0.03000  -0.14000  0.04000  0.15000  0.26000  0.37000  0.48000  0.59000  0.70000  0.81000  0.92000
-0.04000  -0.15000  0.05000  0.16000  0.27000  0.38000  0.49000  0.60000  0.71000  0.82000  0.93000
-0.05000  -0.16000  0.06000  0.17000  0.28000  0.39000  0.50000  0.61000  0.72000  0.83000  0.94000
-0.06000  -0.17000  0.07000  0.18000  0.29000  0.40000  0.51000  0.62000  0.73000  0.84000  
-0.07000  -0.18000  0.08000  0.19000  0.30000  0.41000  0.52000  0.63000  0.74000  0.85000
-0.08000  -0.19000  0.09000  0.20000  0.31000  0.42000  0.53000  0.64000  0.75000  0.86000
-0.09000  -0.20000  0.10000  0.21000  0.32000  0.43000  0.54000  0.65000  0.76000  0.87000
-0.10000  0.00000   0.11000  0.22000  0.33000  0.44000  0.55000  0.66000  0.77000  0.88000
-0.11000  0.01000   0.12000  0.23000  0.34000  0.45000  0.56000  0.67000  0.78000  0.89000
"

INPUTFOLDERS="-0.20000 -0.15000 -0.10000 -0.05000 0.00000 0.05000 0.10000 0.15000 0.20000 0.25000 0.30000 0.35000 0.40000 0.45000 0.50000 0.55000 0.60000 0.65000 0.70000 0.75000 0.80000 0.85000 0.90000"

#INPUTFOLDERS="0.55000"

FITRESULT="/home/fynu/mkomm/scanned_hists_feb19/fitResultMuon.txt"
REGSCALE=1.0

for folder in $INPUTFOLDERS
do
    INPUTHIST="/home/fynu/mkomm/scanned_hists_feb19/hists/"$folder"/mu/cos_theta_lj.root"
    RESPONSEMATRIX="/home/fynu/mkomm/scanned_hists_feb19/hists/"$folder"/mu/tmatrix_nocharge.root:tm__pdgid_13__nominal"
    rm -rf "muon/scan/"$folder
    mkdir "muon/scan/"$folder
    echo "running: "$folder
    nice -n 10 python run.py \
    --output="muon/scan/"$folder"/total" \
    --modelName="total" \
    --histFile=$INPUTHIST \
    --responseMatrix=$RESPONSEMATRIX \
    --fitResult=$FITRESULT \
    --scaleRegularization=$REGSCALE \
    -f &> "muon/scan/"$folder"_total_run.log" &
    sleep 5s
    
    nice -n 10 python run.py \
    --excludeSys="scale" \
    --output="muon/scan/"$folder"/scaleexcl" \
    --modelName="scaleexcl" \
    --histFile=$INPUTHIST \
    --responseMatrix=$RESPONSEMATRIX \
    --fitResult=$FITRESULT \
    --scaleRegularization=$REGSCALE \
    -f &> "muon/scan/"$folder"_scaleexcl_run.log" &
    sleep 5s
    
    nice -n 10 python run.py \
    --excludeSys="jes" \
    --output="muon/scan/"$folder"/jesexcl" \
    --modelName="jesxcl" \
    --histFile=$INPUTHIST \
    --responseMatrix=$RESPONSEMATRIX \
    --fitResult=$FITRESULT \
    --scaleRegularization=$REGSCALE \
    -f &> "muon/scan/"$folder"_jesexcl_run.log" &
    sleep 5s 
       
    nice -n 10 python run.py \
    --includeSys="" \
    --output="muon/scan/"$folder"/sysexcl" \
    --modelName="sysexcl" \
    --histFile=$INPUTHIST \
    --responseMatrix=$RESPONSEMATRIX \
    --fitResult=$FITRESULT \
    --scaleRegularization=$REGSCALE \
    -f &> "muon/scan/"$folder"_sysexcl_run.log" &
    sleep 5s
        
    nice -n 10 python run.py \
    --output="muon/scan/"$folder"/statexcl" \
    --modelName="statexcl" \
    --histFile=$INPUTHIST \
    --responseMatrix=$RESPONSEMATRIX \
    --fitResult=$FITRESULT \
    --scaleRegularization=$REGSCALE \
    --noStatUncertainty \
    -f &> "muon/scan/"$folder"_statexcl_run.log" &
    sleep 5s
    
    nice -n 10 python run.py \
    --output="muon/scan/"$folder"/mcexcl" \
    --modelName="mcexcl" \
    --histFile=$INPUTHIST \
    --responseMatrix=$RESPONSEMATRIX \
    --fitResult=$FITRESULT \
    --scaleRegularization=$REGSCALE \
    --noMCUncertainty \
    -f &> "muon/scan/"$folder"_mcexcl_run.log" &
    sleep 5s
    
    nice -n 10 python run.py \
    --output="muon/scan/"$folder"/nosys" \
    --modelName="nosys" \
    --includeSys="" \
    --histFile=$INPUTHIST \
    --responseMatrix=$RESPONSEMATRIX \
    --fitResult=$FITRESULT \
    --scaleRegularization=$REGSCALE \
    --noStatUncertainty \
    -f &> "muon/scan/"$folder"_nosys_run.log" &
    
    sleep 15s
done

