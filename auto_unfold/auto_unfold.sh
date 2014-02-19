#!/bin/bash

folder="0.10000"
INPUTHIST="/home/fynu/mkomm/scanned_hists_feb19/hists/"$folder"/mu/cos_theta_lj.root"
RESPONSEMATRIX="/home/fynu/mkomm/scanned_hists_feb19/hists/"$folder"/mu/tmatrix_nocharge.root:tm__pdgid_13__nominal"
FITRESULT="/home/fynu/mkomm/scanned_hists_feb19/fitResultMuon.txt"
REGSCALE="1.0"
nice -n 10 python run.py \
--output="test" \
--modelName="total" \
--histFile=$INPUTHIST \
--responseMatrix=$RESPONSEMATRIX \
--fitResult=$FITRESULT \
--scaleRegularization=$REGSCALE \
-f


