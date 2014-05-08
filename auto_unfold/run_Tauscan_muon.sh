#!/bin/bash


INPUTFOLDERS=""

TAUSCALE="0.001 0.005 0.1 0.5 1.0 2.0 5.0 10.0 50.0 100.0"

FITRESULT="/home/fynu/mkomm/stpol/auto_unfold/fitResultMuon.txt"
REGSCALE=1.0

for tau in $TAUSCALE
do
    INPUTHIST="/nfs/user/mkomm/scanned_hists_apr18/0.80000/mu/cos_theta_lj.root"
    RESPONSEMATRIX="/home/fynu/mkomm/stpol/auto_unfold/mergedTM.root:tm__nominal"
    #rm -rf "muon/tauscan/"$tau
    #mkdir "muon/tauscan/"$tau
    echo "running: "$tau

    nice -n 10 python run.py \
    --includeSys="" \
    --output="muon/tauscan/"$tau"" \
    --modelName="tau" \
    --histFile=$INPUTHIST \
    --responseMatrix=$RESPONSEMATRIX \
    --fitResult=$FITRESULT \
    --scaleRegularization=$tau \
    -f &> "muon/tauscan/"$tau"_run.log" &
    sleep 20s

done


