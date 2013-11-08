
all: train

train: train_bdt_sig_wjets train_bdt_sig_ttjets train_bdt_wjets_ttjets 

#train_csvm_wjets_only train_csvt_wjets_only

train_bdt_sig_wjets:
	python train.py input/bdt_sig_bg1 stpol_bdt_sig_wjets &> input/bdt_sig_bg1/log

train_bdt_sig_ttjets:
	python train.py input/bdt_sig_bg2 stpol_bdt_sig_ttjets &> input/bdt_sig_bg2/log

train_bdt_wjets_ttjets:
	python train.py input/bdt_bg1_bg2 stpol_bdt_wjets_ttjets &> input/bdt_bg1_bg2/log

addvars: add_tchpt add_csvt

add_csvm:
	find skims/csvm* -name "*.root" | sort -R | ~/parallel -j10 -n5 python adder.py csvm weights/stpol_csvm_lepton_flavour.weights.xml {} 

add_csvm_no_bdisc:
	find skims/csvm* -name "*.root" | sort -R | ~/parallel -j10 -n5 python adder.py csvm_no_bdisc weights/stpol_csvm_no_bdisc_lepton_flavour.weights.xml {} 

add_csvt:
	find skims/csvt* -name "*.root" | sort -R | ~/parallel -j10 -n5 python adder.py csvt weights/stpol_csvt_lepton_flavour.weights.xml {} 

add_bdt_wjets:
	find skims/csvt* -name "*.root" | sort | ~/parallel -j4 -n5 python adder.py bdt_wjets weights/stpol_bdt_wjets_lepton_flavour.weights.xml {} 

add_bdt_ttjets:
	find skims/csvt* -name "*.root" | sort | ~/parallel -j4 -n5 python adder.py bdt_ttjets weights/stpol_bdt_ttjets_lepton_flavour.weights.xml {} 

add_tchpt:
	find skims/tchpt* -name "*.root" | sort | ~/parallel -j10 -n5 python adder.py tchpt weights/stpol_tchpt_lepton_flavour.weights.xml {} 

effcurves: eff_csvm eff_csvt

eff_csvm:
	julia roc.jl skims/csvm mva_csvm input/csvm/effs.csv

eff_csvt:
	julia roc.jl skims/csvt mva_csvt input/csvt/effs.csv
