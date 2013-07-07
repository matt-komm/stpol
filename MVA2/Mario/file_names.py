from plots.common import cross_sections

dataFiles_ele = ["../MVA2/step3_final/ele/iso/nominal/SingleMu.root.root","../MVA2/step3_final/ele/iso/nominal/SingleEle.root"]

dataFiles_mu = ["../MVA2/step3_final/mu/iso/nominal/SingleMu.root.root","../MVA2/step3_final/mu/iso/nominal/SingleEle.root"]

mcFiles = {
	"T_t" : "iso/nominal/T_t.root",
	"T_t_ToLeptons" : "iso/nominal/T_t_ToLeptons.root",
	"Tbar_t" : "iso/nominal/Tbar_t.root",
	"Tbar_t_ToLeptons" : "iso/nominal/Tbar_t_ToLeptons.root",
	"T_s" : "iso/nominal/T_s.root",
	"Tbar_s" : "iso/nominal/Tbar_s.root",
	"T_tW" : "iso/nominal/T_tW.root",
	"Tbar_tW" : "iso/nominal/Tbar_tW.root",
	"TTJets_MassiveBinDECAY" : "iso/nominal/TTJets_MassiveBinDECAY.root",
	"WJets_inclusive" : "iso/nominal/WJets_inclusive.root",
	"TTJets_SemiLept" : "iso/nominal/TTJets_SemiLept.root",
	"TTJets_FullLept" : "iso/nominal/TTJets_FullLept.root",
	"W1Jets_exclusive" : "iso/nominal/W1Jets_exclusive.root",
	"W2Jets_exclusive" : "iso/nominal/W2Jets_exclusive.root",
	"W3Jets_exclusive" : "iso/nominal/W3Jets_exclusive.root",
	"W4Jets_exclusive" : "iso/nominal/W4Jets_exclusive.root",
	"GJets1" : "iso/nominal/GJets1.root",
	"GJets2" : "iso/nominal/GJets2.root",
	"DYJets" : "iso/nominal/DYJets.root",
	"WW" : "iso/nominal/WW.root",
	"WZ" : "iso/nominal/WZ.root",
	"ZZ" : "iso/nominal/ZZ.root",
	"QCDMu" : "iso/nominal/QCDMu.root",
	"QCD_Pt_20_30_EMEnriched" : "iso/nominal/QCD_Pt_20_30_EMEnriched.root",
	"QCD_Pt_30_80_EMEnriched" : "iso/nominal/QCD_Pt_30_80_EMEnriched.root",
	"QCD_Pt_80_170_EMEnriched" : "iso/nominal/QCD_Pt_80_170_EMEnriched.root",
	"QCD_Pt_170_250_EMEnriched" : "iso/nominal/QCD_Pt_170_250_EMEnriched.root",
	"QCD_Pt_250_350_EMEnriched" : "iso/nominal/QCD_Pt_250_350_EMEnriched.root",
	"QCD_Pt_350_EMEnriched" : "iso/nominal/QCD_Pt_350_EMEnriched.root",
	"QCD_Pt_20_30_BCtoE" : "iso/nominal/QCD_Pt_20_30_BCtoE.root",
	"QCD_Pt_30_80_BCtoE" : "iso/nominal/QCD_Pt_30_80_BCtoE.root",
	"QCD_Pt_80_170_BCtoE" : "iso/nominal/QCD_Pt_80_170_BCtoE.root",
	"QCD_Pt_170_250_BCtoE" : "iso/nominal/QCD_Pt_170_250_BCtoE.root",
	"QCD_Pt_250_350_BCtoE" : "iso/nominal/QCD_Pt_250_350_BCtoE.root",
	"QCD_Pt_350_BCtoE" : "iso/nominal/QCD_Pt_350_BCtoE.root",
}

dataLumi_ele = {"Ele" : cross_sections.lumi_iso["ele"]}

dataLumi_mu = {"Mu" : cross_sections.lumi_iso["mu"]}
