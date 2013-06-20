#include <TFile.h>
#include <TTree.h>
#include <TH1.h>

#include <iostream>

#include "info.h"
#include "xsec.h"
#include "binnings.h"

using namespace std;

void makehisto(TString varname, TString process, TString ofile, TString file)
{
	TFile *fo = new TFile("histos/input/"+ofile+".root","RECREATE");
	TFile *f = new TFile("trees_8TeV/Nominal/"+file+".root");

	TTree *tree = (TTree*)f->Get("trees/Events");

	cout << "Filling histogram " << varname << "__" << process << endl;

	fo->cd();

	Float_t weight = 1.0;
	Float_t pu_weight = 1.0;
	Float_t btag_weight = 1.0;
	Float_t muonID_weight = 1.0;
	Float_t muonIso_weight = 1.0;
	Float_t muonTrigger_weight = 1.0;

	tree->SetBranchAddress("pu_weight", &pu_weight);
	tree->SetBranchAddress("b_weight_nominal", &btag_weight);
	tree->SetBranchAddress("muon_IDWeight", &muonID_weight);
	tree->SetBranchAddress("muon_IsoWeight", &muonIso_weight);
	tree->SetBranchAddress("muon_TriggerWeight", &muonTrigger_weight);

	// cut variables
	Float_t eta_lj = 0;
	Float_t muonIso = 0;
	Float_t jetrms = 0;
	Float_t mtw = 0;
	tree->SetBranchAddress("mu_iso", &muonIso);
	tree->SetBranchAddress("rms_lj", &jetrms);
	tree->SetBranchAddress("mt_mu", &mtw);
	tree->SetBranchAddress("eta_lj", &eta_lj);

	Float_t var = 0;
	tree->SetBranchAddress(varname, &var);
	
	TH1::SetDefaultSumw2(true);
	TH1I *hcount = (TH1I*)f->Get("trees/count_hist");
	Int_t count = hcount->GetBinContent(1); 

	//cout << "sample size: " << count << endl;
	Float_t xsec = get_xsec(file);
	cout << "xsec: " << xsec << endl;
	
	TH1F *histo = new TH1F(varname+"__"+process,varname+"__"+process,bin_y,list_y);
	histo->Sumw2();
	
	Long_t nentries = tree->GetEntries();
	for(Long_t i = 0; i < nentries; i++) {
		tree->GetEntry(i);

		if(TMath::Abs(eta_lj) < 2.5) continue;

		if(jetrms >= 0.025) continue;
		if(mtw <= 50) continue;
		if(process == "qcd") {
			if (muonIso < 0.3 || muonIso > 0.5) continue;
		} 
		
		if(process != "DATA"  && process != "qcd") {
			weight = pu_weight*btag_weight*muonID_weight*muonIso_weight*muonTrigger_weight;
			weight *= lumi;
			weight *= xsec;
			weight /= (Float_t)count;
		}
		
		histo->Fill(var,weight);
	}
	cout << "integral: " << histo->Integral() << endl;

	// write histos
	histo->Write();
	fo->Close();
}

int main()
{
	// varname histoname outfile inputfile
	/*
	//makehisto("cos_theta","tchan","tchan_t","T_t");
	//makehisto("cos_theta","tchan","tchan_tbar","Tbar_t");
	makehisto("cos_theta","tchan","tchan_t","T_t_ToLeptons");
	makehisto("cos_theta","tchan","tchan_tbar","Tbar_t_ToLeptons");
	makehisto("cos_theta","schan","schan_t","T_s");
	makehisto("cos_theta","schan","schan_tbar","Tbar_s");
	makehisto("cos_theta","twchan","twchan_t","T_tW");
	makehisto("cos_theta","twchan","twchan_tbar","Tbar_tW");
	makehisto("cos_theta","ttbar","ttbar_semilept","TTJets_SemiLept");
	makehisto("cos_theta","wjets","wjets1","W1Jets_exclusive");
	makehisto("cos_theta","wjets","wjets2","W2Jets_exclusive");
	makehisto("cos_theta","wjets","wjets3","W3Jets_exclusive");
	makehisto("cos_theta","wjets","wjets4","W4Jets_exclusive");
	makehisto("cos_theta","zjets","zjets","DYJets");
	makehisto("cos_theta","diboson","ww","WW");
	makehisto("cos_theta","diboson","wz","WZ");
	makehisto("cos_theta","diboson","zz","ZZ");
	//makehisto("cos_theta","qcd","qcd","QCDMu");
	makehisto("cos_theta","qcd","qcd","QCDShape");
	makehisto("cos_theta","DATA","DATA_SingleMu","SingleMu");
	//makehisto("cos_theta","DATA","DATA_SingleMuAB","SingleMuAB");
	//makehisto("cos_theta","DATA","DATA_SingleMuC","SingleMuC");
	//makehisto("cos_theta","DATA","DATA_SingleMuD","SingleMuD");
	*/
	makehisto("cos_theta","tchan","tchan_t","T_t_ToLeptons");
	makehisto("cos_theta","tchan","tchan_tbar","Tbar_t_ToLeptons");
	makehisto("cos_theta","top","schan_t","T_s");
	makehisto("cos_theta","top","schan_tbar","Tbar_s");
	makehisto("cos_theta","top","twchan_t","T_tW");
	makehisto("cos_theta","top","twchan_tbar","Tbar_tW");
	makehisto("cos_theta","top","ttbar_semilept","TTJets_SemiLept");
	makehisto("cos_theta","top","ttbar_fulllept","TTJets_FullLept");
	makehisto("cos_theta","wzjets","wjets1","W1Jets_exclusive");
	makehisto("cos_theta","wzjets","wjets2","W2Jets_exclusive");
	makehisto("cos_theta","wzjets","wjets3","W3Jets_exclusive");
	makehisto("cos_theta","wzjets","wjets4","W4Jets_exclusive");
	makehisto("cos_theta","wzjets","zjets","DYJets");
	makehisto("cos_theta","wzjets","ww","WW");
	makehisto("cos_theta","wzjets","wz","WZ");
	makehisto("cos_theta","wzjets","zz","ZZ");
	makehisto("cos_theta","qcd","qcd","QCDShape");
	makehisto("cos_theta","DATA","DATA_SingleMu","SingleMu");
}
