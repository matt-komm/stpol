import MVA2.common
import ROOT

#~ train_WJets = MVA2.common.MVA_trainer('prepared_WJets.root', ofName = 'trained_WJets.root', jobname='BDT_WJets')
#~ train_WJets_ttbar = MVA2.common.MVA_trainer('prepared_WJets_ttbar.root', ofName = 'trained_WJets_ttbar.root', jobname='BDT_WJets_ttbar')
train_all_mu = MVA2.common.MVA_trainer('prepared_all_mu.root', ofName = 'trained_all_mu.root', jobname='BDT_all_mu')
#~ train_all_el = MVA2.common.MVA_trainer('prepared_all_el.root', ofName = 'trained_all_el.root', jobname='BDT_all_el')
#~ for train in [train_WJets, train_WJets_ttbar]:
	#~ train.add_variable("mt_mu")
	#~ train.add_variable("top_mass")
	#~ train.add_variable("eta_lj")
	#~ train.add_variable("bdiscr_bj")
	#~ train.add_variable("bdiscr_lj")
	#~ train.add_variable("eta_bj")
	#~ train.add_variable("eta_lj")
	#~ train.add_variable("met")
	#~ train.add_variable("mu_iso")
	#~ train.add_variable("rms_lj")


#~ train_all_el.add_variable("pt_bj")
#~ train_all_el.add_variable("el_pt")
#~ train_all_el.add_variable("bdiscr_lj")
#~ train_all_el.add_variable("bdiscr_bj")
#~ train_all_el.add_variable("mass_lj")
#~ train_all_el.add_variable("mass_bj")
#~ train_all_el.add_variable("mt_el")
#~ train_all_el.add_variable("met")
#~ train_all_el.add_variable("C")
#~ train_all_el.add_variable("eta_lj")
#~ train_all_el.add_variable("top_mass")
train_all_mu.add_variable("pt_bj")
train_all_mu.add_variable("mu_pt")
train_all_mu.add_variable("bdiscr_lj")
train_all_mu.add_variable("bdiscr_bj")
train_all_mu.add_variable("mass_lj")
train_all_mu.add_variable("mass_bj")
train_all_mu.add_variable("mt_mu")
train_all_mu.add_variable("met")
train_all_mu.add_variable("C")
train_all_mu.add_variable("eta_lj")
train_all_mu.add_variable("top_mass")


#~ train_WJets.book_method(ROOT.TMVA.Types.kBDT, "BDT_WJets", "!H:!V:NTrees=100")
#~ train_WJets.book_method(ROOT.TMVA.Types.kBDT, "BDT_WJets_Mario", "!H:!V:NTrees=2000:BoostType=Grad:Shrinkage=0.1:!UseBaggedGrad:nCuts=2000:nEventsMin=100:NNodesMax=5:UseNvars=4:PruneStrength=5:PruneMethod=CostComplexity:MaxDepth=6")
#~ train_WJets_ttbar.book_method(ROOT.TMVA.Types.kBDT, "BDT_WJets_ttbar", "!H:!V:NTrees=100")
#~ train_WJets_ttbar.book_method(ROOT.TMVA.Types.kBDT, "BDT_WJets_ttbar_Mario", "!H:!V:NTrees=2000:BoostType=Grad:Shrinkage=0.1:!UseBaggedGrad:nCuts=2000:nEventsMin=100:NNodesMax=5:UseNvars=4:PruneStrength=5:PruneMethod=CostComplexity:MaxDepth=6")
train_all_mu.book_method(ROOT.TMVA.Types.kBDT, "BDT_all_mu_Mario", "!H:!V:NTrees=2000:BoostType=Grad:Shrinkage=0.1:!UseBaggedGrad:nCuts=2000:nEventsMin=100:NNodesMax=5:UseNvars=4:PruneStrength=5:PruneMethod=CostComplexity:MaxDepth=6")
#~ train_all_el.book_method(ROOT.TMVA.Types.kBDT, "BDT_all_el_Mario", "!H:!V:NTrees=2000:BoostType=Grad:Shrinkage=0.1:!UseBaggedGrad:nCuts=2000:nEventsMin=100:NNodesMax=5:UseNvars=4:PruneStrength=5:PruneMethod=CostComplexity:MaxDepth=6")

for train in [train_all_mu]:
#~ for train in [train_WJets, train_WJets_ttbar]:
	train.get_factory().TrainAllMethods()
	train.evaluate()
	train.pack()
