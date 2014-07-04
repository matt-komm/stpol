#!/bin/bash


REGSCALE=1.0
RESPONSEMATRIX="/home/fynu/mkomm/stpol/auto_unfold/out.root:tm__nominal"
INPUTHIST="/home/fynu/mkomm/stpol/auto_unfold/out.root"

echo "runnning: "$sample
echo "----------------------"
TARGET=/home/fynu/mkomm/stpol/auto_unfold/test
CFG=$TARGET/"test.cfg"
echo "set, signal, beta_signal, 2j1t_cos_theta_lj__tchan" > $CFG
echo "set, background, qcd, 2j1t_cos_theta_lj__qcd" >> $CFG
echo "set, background, ttjets, 2j1t_cos_theta_lj__ttjets, 2j1t_cos_theta_lj__twchan, 2j1t_cos_theta_lj__schan" >> $CFG
echo "set, background, wzjets, 2j1t_cos_theta_lj__wjets, 2j1t_cos_theta_lj__dyjets, 2j1t_cos_theta_lj__diboson" >> $CFG
echo "rate, beta_signal, 1.0,  1.0e-6" >> $CFG
echo "rate, ttjets, 1.0,  1.0e-6" >> $CFG
echo "rate, qcd, 1.0, 1.0e-6" >> $CFG
echo "rate, wzjets, 1.0,  1.0e-6" >> $CFG
echo $CFG
cat $CFG

nice -n 10 python run.py \
--output=$TARGET"/test" \
--modelName="test" \
--includeSys="" \
--histFile=$INPUTHIST \
--responseMatrix=$RESPONSEMATRIX \
--fitResult=$CFG \
--scaleRegularization=$REGSCALE \
--noMCUncertainty \
--only-2bins \
-f






