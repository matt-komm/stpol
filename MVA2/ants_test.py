#! /usr/bin/env python
import ROOT
from plots.common import cross_sections

ROOT.gROOT.Reset()

files = {}
hists = {}
trees = {}
hstack = ROOT.THStack()
legend = ROOT.TLegend(0.7, 0.05, 0.95, 0.95)

clridx=0

backgrounds = ["T_t_ToLeptons", "Tbar_t_ToLeptons", "T_s", "Tbar_s", "T_tW", "Tbar_tW", "TTJets_MassiveBinDECAY", "WJets_inclusive", "TTJets_SemiLept", "TTJets_FullLept", "GJets1", "GJets2", "DYJets", "WW", "WZ", "ZZ", "QCDMu", "QCD_Pt_20_30_EMEnriched", "QCD_Pt_30_80_EMEnriched", "QCD_Pt_80_170_EMEnriched", "QCD_Pt_170_250_EMEnriched", "QCD_Pt_250_350_EMEnriched", "QCD_Pt_350_EMEnriched", "QCD_Pt_20_30_BCtoE", "QCD_Pt_30_80_BCtoE", "QCD_Pt_80_170_BCtoE", "QCD_Pt_170_250_BCtoE", "QCD_Pt_250_350_BCtoE", "QCD_Pt_350_BCtoE"]


for back in backgrounds:
	files[back] = ROOT.TFile("../../out_step3_test4/mu/iso/nominal/"+back+".root")
	trees[back] = files[back].Get("trees/Events")
	count_uncut = files[back].Get("trees/count_hist").GetBinContent(1)
	count_cut = trees[back].GetEntries()
	hists[back] = ROOT.TH1F(back, back, 100, -1, 1.8)
	hists[back].SetFillStyle(1001)
	hists[back].SetFillColor(clridx)
	clridx += 1
	hists[back].SetLineWidth(0)
	hists[back].SetLineStyle(0)
	weight = cross_sections.lumi_iso["mu"]*cross_sections.xs[back]/count_uncut
	#weight = cross_sections.lumi_iso["mu"]*cs *count_cut/count_uncut   /count_cut
	trees[back].Draw("cos_theta >> " + back, str(weight))
	hstack.Add(hists[back])
	legend.AddEntry(hists[back],back)

files["SingleMu"] = ROOT.TFile("../../out_step3_test4/mu/iso/nominal/"+"SingleMu"+".root")
trees["SingleMu"] = files["SingleMu"].Get("trees/Events")
hists["SingleMu"] = ROOT.TH1F("SingleMu", "SingleMu", 100, -1, 1.8)
trees["SingleMu"].Draw("cos_theta >> SingleMu", "1")
legend.AddEntry(hists["SingleMu"],"SingleMu")

hstack.Draw()
hists["SingleMu"].Draw("E1 SAME")
legend.Draw()


