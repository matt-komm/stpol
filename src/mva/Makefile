
all: train

train: train_csvm train_csvt train_csvm_wjets_only train_csvt_wjets_only

train_csvm:
	python train.py input/csvm stpol_csvm &> input/csvm/log

train_csvt:
	python train.py input/csvt stpol_csvt &> input/csvt/log

train_csvm_wjets_only:
	python train.py input/csvm_wjets_only stpol_csvm_wjets_only &> input/csvm_wjets_only/log

train_csvt_wjets_only:
	python train.py input/csvt_wjets_only stpol_csvt_wjets_only &> input/csvt_wjets_only/log

addvars: add_csvm add_csvt

add_csvm:
	find skims/ -name "*.root" | ~/parallel -j10 python adder.py {.}_mva_csvm.csv weights/stpol_csvm_lepton_flavour.weights.xml {} 

add_csvt:
	find skims/ -name "*.root" | ~/parallel -j10 python adder.py {.}_mva_csvt.csv weights/stpol_csvt_lepton_flavour.weights.xml {} 

effcurves: eff_csvm eff_csvt

eff_csvm:
	julia roc.jl skims/csvm mva_csvm input/csvm/effs.csv

eff_csvt:
	julia roc.jl skims/csvt mva_csvt input/csvt/effs.csv
