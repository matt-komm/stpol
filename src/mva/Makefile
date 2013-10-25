
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

addvars: add_csvm

add_csvm:
	find skims/ -name "*.root" | ~/parallel -j5 echo python adder.py {.}_mva_csvm.csv weights/stpol_csvm_lepton_flavour.weights.xml {} 
