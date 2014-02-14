#!/bin/bash

#INPUTHIST="/home/fynu/mkomm/mu__cos_theta__mva_0_06/data.root"
#RESPONSEMATRIX="/home/fynu/mkomm/mu__cos_theta__mva_0_06/matrix.root:matrix"
#FITRESULT="/home/fynu/mkomm/mu__cos_theta__mva_0_06/fitresult.txt"
folder="0.10000"
INPUTHIST="/home/fynu/mkomm/scanned_hists_feb10/hists/"$folder"/mu/cos_theta_lj.root"
RESPONSEMATRIX="/home/fynu/mkomm/scanned_hists_feb10/hists/"$folder"/tmatrix_nocharge.root:tm__pdgid_13__nominal"
FITRESULT="/home/fynu/mkomm/scanned_hists_feb10/fitResultMuon.txt"
python run.py \
--output="test" \
--modelName="test" \
--histFile=$INPUTHIST \
--responseMatrix=$RESPONSEMATRIX \
--fitResult=$FITRESULT \
--scaleRegularization=1.0 \
--prefix="2j1t" \
-f


