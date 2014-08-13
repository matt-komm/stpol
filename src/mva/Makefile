include ../analysis/Makefile.options

skim:
	./skim.sh

all: train

ARGS1="H:VerbosityLevel=Debug:NTrees=50:BoostType=Grad:Shrinkage=0.1:!UseBaggedGrad:nCuts=200:NNodesMax=5:UseNvars=4:PruneStrength=7:PruneMethod=CostComplexity:MaxDepth=2"
ARGS2="H:VerbosityLevel=Debug:NTrees=500:BoostType=Grad:Shrinkage=0.1:!UseBaggedGrad:nCuts=200:NNodesMax=5:UseNvars=4:PruneStrength=7:PruneMethod=CostComplexity:MaxDepth=2"
ARGS3="H:VerbosityLevel=Debug:NTrees=1000:BoostType=Grad:Shrinkage=0.1:!UseBaggedGrad:nCuts=200:NNodesMax=5:UseNvars=4:PruneStrength=7:PruneMethod=CostComplexity:MaxDepth=2"
ARGS4="H:VerbosityLevel=Debug:NTrees=2000:BoostType=Grad:Shrinkage=0.1:!UseBaggedGrad:nCuts=500:NNodesMax=5:UseNvars=4:PruneStrength=9:PruneMethod=CostComplexity:MaxDepth=1"
ARGSdef="H:VerbosityLevel=Debug:NTrees=2000:BoostType=Grad:Shrinkage=0.1:!UseBaggedGrad:nCuts=2000:nEventsMin=100:NNodesMax=5:UseNvars=4:PruneStrength=5:PruneMethod=CostComplexity:MaxDepth=6"

train: train_bdt_sig_bg_ARGS1 train_bdt_sig_bg_ARGS2 train_bdt_sig_bg train_bdt_sig_bg_mixed train_bdt_sig_bg_mixed_ARGS1 train_bdt_sig_bg_mixed_ARGS2

train_bdt_sig_bg_ARGS1:
	cp -R input/default input/bdt_sig_bg_ARGS1 
	python train.py input/bdt_sig_bg_ARGS1 stpol_bdt_sig_bg_ARGS1 $(ARGS1) &> input/bdt_sig_bg_ARGS1/log

train_bdt_sig_bg_ARGS2:
	cp -R input/default input/bdt_sig_bg_ARGS2 
	python train.py input/bdt_sig_bg_ARGS2 stpol_bdt_sig_bg_ARGS2 $(ARGS2) &> input/bdt_sig_bg_ARGS2/log

train_bdt_sig_bg_ARGS3:
	cp -R input/default input/bdt_sig_bg_ARGS3 
	python train.py input/bdt_sig_bg_ARGS3 stpol_bdt_sig_bg_ARGS3 $(ARGS3) &> input/bdt_sig_bg_ARGS3/log

train_bdt_sig_bg_ARGS4:
	cp -R input/default input/bdt_sig_bg_ARGS4 
	python train.py input/bdt_sig_bg_ARGS4 stpol_bdt_sig_bg_ARGS4 $(ARGS4) &> input/bdt_sig_bg_ARGS4/log

train_bdt_sig_bg:
	cp -R input/default input/bdt_sig_bg 
	python train.py input/bdt_sig_bg stpol_bdt_sig_bg $(ARGSdef) &> input/bdt_sig_bg/log

train_bdt_sig_bg_mixed:
	cp -R input/default input/bdt_sig_bg_mixed 
	python train_mixed.py input/bdt_sig_bg_mixed stpol_bdt_sig_bg_mixed $(ARGSdef) &> input/bdt_sig_bg_mixed/log

train_bdt_sig_bg_mixed_ARGS1:
	cp -R input/default input/bdt_sig_bg_mixed_ARGS1 
	python train_mixed.py input/bdt_sig_bg_mixed_ARGS1 stpol_bdt_sig_bg_mixed_ARGS1 $(ARGS1) &> input/bdt_sig_bg_mixed_ARGS1/log

train_bdt_sig_bg_mixed_ARGS2:
	cp -R input/default input/bdt_sig_bg_mixed_ARGS2
	python train_mixed.py input/bdt_sig_bg_mixed_ARGS2 stpol_bdt_sig_bg_mixed_ARGS2 $(ARGS2) &> input/bdt_sig_bg_mixed_ARGS2/log

train_bdt_sig_bg_mixed_ARGS3:
	cp -R input/default input/bdt_sig_bg_mixed_ARGS3
	python train_mixed.py input/bdt_sig_bg_mixed_ARGS3 stpol_bdt_sig_bg_mixed_ARGS3 $(ARGS3) &> input/bdt_sig_bg_mixed_ARGS3/log

train_bdt_sig_bg_mixed_ARGS4:
	cp -R input/default input/bdt_sig_bg_mixed_ARGS4
	python train_mixed.py input/bdt_sig_bg_mixed_ARGS4 stpol_bdt_sig_bg_mixed_ARGS4 $(ARGS4) &> input/bdt_sig_bg_mixed_ARGS4/log

evaluate:
	find ~/singletop/ntuples/nominal/ -name "*.root" | ~/parallel python adder.py bdt_sig_bg weights/stpol_bdt_sig_bg_lepton_flavour.weights.xml {}
	find ~/singletop/ntuples/nominal/ -name "*.root" | ~/parallel python adder.py bdt_sig_bg_A3 weights/stpol_bdt_sig_bg_ARGS3_lepton_flavour.weights.xml {}
	find ~/singletop/ntuples/nominal/ -name "*.root" | ~/parallel python adder.py bdt_sig_bg_mixed_A3 weights/stpol_bdt_sig_bg_mixed_ARGS3_lepton_flavour.weights.xml {}
