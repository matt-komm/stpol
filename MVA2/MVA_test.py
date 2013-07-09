import ROOT
from plots.common import cross_sections
from plots.common import cuts

signals = [
	#~ "T_t", 
	"T_t_ToLeptons", 
	#~ "Tbar_t", 
	"Tbar_t_ToLeptons", 
]

backgrounds = [
	#~ "T_s", 
	#~ "Tbar_s", 
	"T_tW", 
	"Tbar_tW", 
	#~ "TTJets_MassiveBinDECAY", 
	"WJets_inclusive", 

	#FIXME: ttbar branching ratio
	#~ "TTJets_SemiLept", 
	#~ "TTJets_FullLept", 

	#exclusive sample branching ratios, same as PREP
	#~ "W1Jets_exclusive", 
	#~ "W2Jets_exclusive", 
	#~ "W3Jets_exclusive", 
	#~ "W4Jets_exclusive", 

	#http://cms.cern.ch/iCMS/prep/requestmanagement?dsn=*GJets_HT-*_8TeV-madgraph*
	#~ "GJets1", 
	#~ "GJets2", 

	#~ "DYJets", 
	#~ "WW", 
	#~ "WZ", 
	#~ "ZZ", 
	#~ "QCDMu", 

	#http://cms.cern.ch/iCMS/prep/requestmanagement?dsn=QCD_Pt_*_*_EMEnriched_TuneZ2star_8TeV_pythia6*
	#~ "QCD_Pt_20_30_EMEnriched", 
	#~ "QCD_Pt_30_80_EMEnriched", 
	#~ "QCD_Pt_80_170_EMEnriched", 
	#~ "QCD_Pt_170_250_EMEnriched", 
	#~ "QCD_Pt_250_350_EMEnriched", 
	#~ "QCD_Pt_350_EMEnriched", 

	#http://cms.cern.ch/iCMS/prep/requestmanagement?dsn=QCD_Pt_*_*_BCtoE_TuneZ2star_8TeV_pythia6*
	#~ "QCD_Pt_20_30_BCtoE", 
	#~ "QCD_Pt_30_80_BCtoE", 
	#~ "QCD_Pt_80_170_BCtoE", 
	#~ "QCD_Pt_170_250_BCtoE", 
	#~ "QCD_Pt_250_350_BCtoE", 
	#~ "QCD_Pt_350_BCtoE", 
]

variables = {
	#~ "SF_total" : "F",
	#~ "b_weight_nominal" : "F",
	#~ "b_weight_nominal_BCdown" : "F",
	#~ "b_weight_nominal_BCup" : "F",
	#~ "b_weight_nominal_Ldown" : "F",
	#~ "b_weight_nominal_Lup" : "F",
	#~ "bdiscr_bj" : "F",
	#~ "bdiscr_lj" : "F",
	#~ "cos_theta" : "F",
	#~ "deltaR_bj" : "F",
	#~ "deltaR_lj" : "F",
	#~ "el_mva" : "F",
	#~ "el_pt" : "F",
	#~ "el_reliso" : "F",
	#~ "electron_IDWeight" : "F",
	#~ "electron_IDWeight_down" : "F",
	#~ "electron_IDWeight_up" : "F",
	#~ "electron_triggerWeight" : "F",
	#~ "electron_triggerWeight_down" : "F",
	#~ "electron_triggerWeight_up" : "F",
	#~ "eta_bj" : "F",
	"eta_lj" : "F",
	#~ "gen_weight" : "F",
	#~ "met" : "F",
	#~ "mt_mu" : "F",
	#~ "mu_chi2" : "F",
	#~ "mu_db" : "F",
	#~ "mu_dz" : "F",
	#~ "mu_eta" : "F",
	#~ "mu_iso" : "F",
	#~ "mu_pt" : "F",
	#~ "muon_IDWeight" : "F",
	#~ "muon_IDWeight_down" : "F",
	#~ "muon_IDWeight_up" : "F",
	#~ "muon_IsoWeight" : "F",
	#~ "muon_IsoWeight_down" : "F",
	#~ "muon_IsoWeight_up" : "F",
	#~ "muon_TriggerWeight" : "F",
	#~ "muon_TriggerWeight_down" : "F",
	#~ "muon_TriggerWeight_up" : "F",
	#~ "pt_bj" : "F",
	#~ "pt_lj" : "F",
	#~ "pu_weight" : "F",
	#~ "rms_lj" : "F",
	"top_mass" : "F",
	#~ "true_cos_theta" : "F",
	#~ "HLT_Ele27_WP80_v10" : "I",
	#~ "HLT_Ele27_WP80_v11" : "I",
	#~ "HLT_Ele27_WP80_v8" : "I",
	#~ "HLT_Ele27_WP80_v9" : "I",
	#~ "HLT_IsoMu24_eta2p1_v11" : "I",
	#~ "HLT_IsoMu24_eta2p1_v12" : "I",
	#~ "HLT_IsoMu24_eta2p1_v13" : "I",
	#~ "HLT_IsoMu24_eta2p1_v14" : "I",
	#~ "HLT_IsoMu24_eta2p1_v15" : "I",
	#~ "HLT_IsoMu24_eta2p1_v16" : "I",
	#~ "HLT_IsoMu24_eta2p1_v17" : "I",
	#~ "el_charge" : "I",
	#~ "el_mother_id" : "I",
	#~ "mu_charge" : "I",
	#~ "mu_gtrack" : "I",
	#~ "mu_itrack" : "I",
	#~ "mu_layers" : "I",
	#~ "mu_mother_id" : "I",
	#~ "mu_stations" : "I",
	#~ "n_eles" : "I",
	#~ "n_jets" : "I",
	#~ "n_muons" : "I",
	#~ "n_tags" : "I",
	#~ "n_vertices" : "I",
	#~ "n_veto_ele" : "I",
	#~ "n_veto_mu" : "I",
	#~ "true_lepton_pdgId" : "I",
	#~ "wjets_classification" : "I",
	#~ "event_id" : "I",
	#~ "lumi_id" : "I",
	#~ "run_id" : "I"
}

cutstring = str(cuts.Cuts.rms_lj*cuts.Cuts.mt_mu*cuts.Cuts.n_jets(2)*cuts.Cuts.n_tags(1))
cuts = ROOT.TCut(cutstring)

files = {}
trees = {}
strees = {} #skimmed trees

facout = ROOT.TFile("facOut.root", "RECREATE")
factory = ROOT.TMVA.Factory("tpol", facout, "" )

for sg in signals:
	files[sg] = ROOT.TFile("step3_latest/mu/iso/nominal/" + sg + ".root")
	trees[sg] = files[sg].Get("trees/Events")
	strees[sg] = trees[sg].CopyTree(cutstring)
	count_uncut = files[sg].Get("trees/count_hist").GetBinContent(1)
	weight = cross_sections.xs[sg]*cross_sections.lumi_iso["mu"]/count_uncut
	factory.AddSignalTree(strees[sg], weight)

for bg in backgrounds:
	files[bg] = ROOT.TFile("step3_latest/mu/iso/nominal/" + bg + ".root")
	trees[bg] = files[bg].Get("trees/Events")
	strees[bg] = trees[bg].CopyTree(cutstring)
	count_uncut = files[bg].Get("trees/count_hist").GetBinContent(1)
	weight = cross_sections.xs[bg]*cross_sections.lumi_iso["mu"]/count_uncut
	factory.AddBackgroundTree(strees[bg], weight)

for var in variables:
	factory.AddVariable(var, variables[var])

factory.PrepareTrainingAndTestTree(ROOT.TCut(), "")
#~ factory.BookMethod(ROOT.TMVA.Types.kCuts, "Cuts")
factory.BookMethod(ROOT.TMVA.Types.kMLP, "MLP", "!H:!V:VarTransform=N:HiddenLayers=10:TrainingMethod=BFGS")


factory.TrainAllMethods()
factory.TestAllMethods()
factory.EvaluateAllMethods()

facout.Close()
