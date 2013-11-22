include ../analysis/Makefile.options

skim:
	./skim.sh

all: train

train: train_bdt_sig_wjets train_bdt_sig_ttjets train_bdt_wjets_ttjets train_bdt_sig_bg 

#train_csvm_wjets_only train_csvt_wjets_only

inputs:
	find skims/$1/tchan -name "*.root" > input/$2/sig.txt
	find skims/$1/ttjets -name "*.root" > input/$2/bg.txt
	find skims/$1/wjets -name "*.root" >> input/$2/bg.txt

train_bdt_sig_wjets:
	$(ROOTWRAP) && python train.py input/bdt_sig_bg1 stpol_bdt_sig_wjets &> input/bdt_sig_bg1/log

train_bdt_sig_bg:
	$(ROOTWRAP) && python train.py input/bdt_sig_bg stpol_bdt_sig_bg &> input/bdt_sig_bg/log

train_bdt_sig_ttjets:
	$(ROOTWRAP) && python train.py input/bdt_sig_bg2 stpol_bdt_sig_ttjets &> input/bdt_sig_bg2/log

train_bdt_wjets_ttjets:
	$(ROOTWRAP) && python train.py input/bdt_bg1_bg2 stpol_bdt_wjets_ttjets &> input/bdt_bg1_bg2/log

addvars: add_bdt_sig_bg1 add_bdt_sig_bg2 add_bdt_bg1_bg2 add_bdt_sig_bg

add_bdt_sig_bg1:
	find skims/csvt* -name "*.root" | sort | ~/parallel -t --verbose --resume --joblog=`mktemp` -j1 -n5 python adder.py bdt_sig_bg1 weights/stpol_bdt_sig_wjets_lepton_flavour.weights.xml {} 
 
add_bdt_sig_bg:
	find skims/csvt* -name "*.root" | sort | ~/parallel -t --verbose --resume --joblog=`mktemp` -j1 -n5 python adder.py bdt_sig_bg weights/stpol_bdt_sig_bg_lepton_flavour.weights.xml {} 

add_bdt_sig_bg2:
	find skims/csvt* -name "*.root" | sort | ~/parallel -t --verbose --resume --joblog=`mktemp` -j1 -n5 python adder.py bdt_sig_bg2 weights/stpol_bdt_sig_ttjets_lepton_flavour.weights.xml {}

add_bdt_bg1_bg2:
	find skims/csvt* -name "*.root" | sort | ~/parallel -t --verbose --resume --joblog=`mktemp` -j1 -n5 python adder.py bdt_bg1_bg2 weights/stpol_bdt_wjets_ttjets_lepton_flavour.weights.xml {} 
 
hadd:
	find -L skims -name "*.root" > files.txt
	../skim/hadd.jl files.txt skims.csv

effcurves: eff_csvm eff_csvt

eff_csvm:
	julia roc.jl skims/csvm mva_csvm input/csvm/effs.csv

eff_csvt:
	julia roc.jl skims/csvt mva_csvt input/csvt/effs.csv
