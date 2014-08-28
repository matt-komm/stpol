include ../analysis/Makefile.options

skim:
	./skim.sh

all: train


ARGSdef="H:VerbosityLevel=Debug:NTrees=2000:BoostType=Grad:Shrinkage=0.1:!UseBaggedGrad:nCuts=2000:nEventsMin=100:NNodesMax=5:UseNvars=4:PruneStrength=5:PruneMethod=CostComplexity:MaxDepth=6"
ARGSmixed="H:VerbosityLevel=Debug:NTrees=200:BoostType=Grad:Shrinkage=0.1:nCuts=50:UseNvars=2:MaxDepth=2"

train_bdt_sig_bg:
	cp -R input/default input/bdt_sig_bg 
	python train.py input/bdt_sig_bg stpol_bdt_sig_bg $(ARGSdef) &> input/bdt_sig_bg/log

train_bdt_sig_bg_exclusive_only:
	cp -R input/exclusive_only input/bdt_sig_bg_exclusive_only 
	python train.py input/bdt_sig_bg_exclusive_only stpol_bdt_sig_bg_exclusive_only $(ARGSdef) &> input/bdt_sig_bg_exclusive_only/log

train_bdt_sig_bg_mixed:
	cp -R input/default input/bdt_sig_bg_mixed 
	python train_mixed.py input/bdt_sig_bg_mixed stpol_bdt_sig_bg_mixed $(ARGSmixed) &> input/bdt_sig_bg_mixed/log

evaluate:
	find ~/singletop/ntuples/nominal/ -name "*.root" | ~/parallel python adder.py bdt_sig_bg weights/stpol_bdt_sig_bg_lepton_flavour.weights.xml {}
	find ~/singletop/ntuples/nominal/ -name "*.root" | ~/parallel python adder.py bdt_sig_bg_A3 weights/stpol_bdt_sig_bg_ARGS3_lepton_flavour.weights.xml {}
	find ~/singletop/ntuples/nominal/ -name "*.root" | ~/parallel python adder.py bdt_sig_bg_mixed_A3 weights/stpol_bdt_sig_bg_mixed_ARGS3_lepton_flavour.weights.xml {}

print_statistics:
	echo "TTJets_SemiLept"
	cat input/default/bg.txt | grep "TTJets_SemiLept" | python list_entries.py
	echo "TTJets_FullLept"
	cat input/default/bg.txt | grep "TTJets_FullLept" | python list_entries.py
	echo "TTJets_MassiveBinDECAY"
	cat input/default/bg.txt | grep "TTJets_MassiveBinDECAY" | python list_entries.py
