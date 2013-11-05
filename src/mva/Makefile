
all: train

train: train_csvt train_tchpt

#train_csvm_wjets_only train_csvt_wjets_only

train_csvm:
	python train.py input/csvm stpol_csvm &> input/csvm/log

train_tchpt:
	python train.py input/tchpt stpol_tchpt &> input/tchpt/log

train_csvm_no_bdisc:
	python train.py input/csvm_no_bdisc stpol_csvm_no_bdisc &> input/csvm_no_bdisc/log

train_csvt:
	python train.py input/csvt stpol_csvt &> input/csvt/log

train_wjets:
	python train.py input/bdt_wjets stpol_bdt_wjets &> input/bdt_wjets/log

train_ttjets:
	python train.py input/bdt_ttjets stpol_bdt_ttjets &> input/bdt_ttjets/log

train_csvt_dphi:
	python train.py input/csvt_dphi stpol_csvt_dphi &> input/csvt_dphi/log

train_csvm_wjets_only:
	python train.py input/csvm_wjets_only stpol_csvm_wjets_only &> input/csvm_wjets_only/log

train_csvt_wjets_only:
	python train.py input/csvt_wjets_only stpol_csvt_wjets_only &> input/csvt_wjets_only/log

addvars: add_tchpt add_csvt

add_csvm:
	find skims/csvm* -name "*.root" | sort -R | ~/parallel -j10 -n5 python adder.py csvm weights/stpol_csvm_lepton_flavour.weights.xml {} 

add_csvm_no_bdisc:
	find skims/csvm* -name "*.root" | sort -R | ~/parallel -j10 -n5 python adder.py csvm_no_bdisc weights/stpol_csvm_no_bdisc_lepton_flavour.weights.xml {} 

add_csvt:
	find skims/csvt* -name "*.root" | sort -R | ~/parallel -j10 -n5 python adder.py csvt weights/stpol_csvt_lepton_flavour.weights.xml {} 

add_tchpt:
	find skims/tchpt* -name "*.root" | sort -R | ~/parallel -j10 -n5 python adder.py tchpt weights/stpol_tchpt_lepton_flavour.weights.xml {} 

effcurves: eff_csvm eff_csvt

eff_csvm:
	julia roc.jl skims/csvm mva_csvm input/csvm/effs.csv

eff_csvt:
	julia roc.jl skims/csvt mva_csvt input/csvt/effs.csv
