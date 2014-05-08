#!/bin/bash
python TMmerger.py ~/scanned_hists_apr17/csvt__qcd_mva__real/0.40000/mu/tmatrix_nocharge__gen_mu.root ~/scanned_hists_apr17/csvt__qcd_mva__real/0.40000/mu/tmatrix_nocharge__gen_tau.root tm_out_real.root
python createAnomHists.py \
--input=tm_out_real.root \
--addinput=~/scanned_hists_apr17/csvt__qcd_mva__real/0.40000/mu/cos_theta_lj.root \
--output=out_real.root \
-n 21 \
--inputHistSMCuts=tm__comphep_nominal__proj_y \
--inputHistUnPhysCuts=tm__comphep_anom_unphys__proj_y \
--inputHistBSMCuts=tm__comphep_anom_0100__proj_y \
--inputHistSM=tm__comphep_nominal__proj_x \
--inputHistUnPhys=tm__comphep_anom_unphys__proj_x \
--inputHistBSM=tm__comphep_anom_0100__proj_x \
--inputTMSM=tm__comphep_nominal \
--inputTMUnPhys=tm__comphep_anom_unphys \
--inputTMBSM=tm__comphep_anom_0100 

python TMmerger.py ~/scanned_hists_apr17/csvt__qcd_mva__cplx/0.40000/mu/tmatrix_nocharge__gen_mu.root ~/scanned_hists_apr17/csvt__qcd_mva__cplx/0.40000/mu/tmatrix_nocharge__gen_tau.root tm_out_cplx.root
python createAnomHists.py \
--input=tm_out_cplx.root \
--addinput=~/scanned_hists_apr17/csvt__qcd_mva__cplx/0.40000/mu/cos_theta_lj.root \
--output=out_cplx.root \
-n 21 \
--inputHistSMCuts=tm__comphep_nominal__proj_y \
--inputHistUnPhysCuts=tm__comphep_anom_unphys__proj_y \
--inputHistBSMCuts=tm__comphep_anom_0100__proj_y \
--inputHistSM=tm__comphep_nominal__proj_x \
--inputHistUnPhys=tm__comphep_anom_unphys__proj_x \
--inputHistBSM=tm__comphep_anom_0100__proj_x \
--inputTMSM=tm__comphep_nominal \
--inputTMUnPhys=tm__comphep_anom_unphys \
--inputTMBSM=tm__comphep_anom_0100 
