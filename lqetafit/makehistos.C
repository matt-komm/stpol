#include <TFile.h>
#include <TTree.h>
#include <TH1.h>

#include <iostream>

#include "xsec.h"

using namespace std;

void makehisto(TString varname, TString process, TString ofile, TString file)
{
	TFile *fo = new TFile("histos/"+ofile+".root","RECREATE");
	TFile *f = new TFile("trees_8TeV/Nominal/"+file+".root");

	TTree *tree = (TTree*)f->Get("trees/Events");

	cout << "Filling histogram " << varname << "__" << process << " with " << file << endl;

	fo->cd();

	Float_t lumi = 19739;

	// weights
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
	Float_t muonIso = 0;
	Float_t jetrms = 0;
	Float_t mtw = 0;
	tree->SetBranchAddress("mu_iso", &muonIso);
	tree->SetBranchAddress("rms_lj", &jetrms);
	tree->SetBranchAddress("mt_mu", &mtw);
	//
	Int_t wjets_class = -1;
	tree->SetBranchAddress("wjets_classification", &wjets_class);

	Float_t var = 0;
	tree->SetBranchAddress(varname, &var);
	
	TH1::SetDefaultSumw2(true);
	TH1I *hcount = (TH1I*)f->Get("trees/count_hist");
	Int_t count = hcount->GetBinContent(1); 

	//cout << "sample size: " << count << endl;
	Float_t xsec = get_xsec(file);
	cout << "xsec: " << xsec << endl;
	
	// FIXME adapt range for each variable histogram
	//TH1D *histo = new TH1D(varname+"__"+process,varname+"__"+process,30,-4.5,4.5);
	//TH1D *histo = new TH1D(varname+"__"+process,varname+"__"+process,15,-4.5,4.5);
	//TH1D *histo = new TH1D(varname+"__"+process,varname+"__"+process,20,-4.5,4.5);
	// FIXME
	TH1D *histo = new TH1D(varname+"__"+process,varname+"__"+process,15,0,4.5);
	//TH1D *histo = new TH1D(varname+"__"+process,varname+"__"+process,20,0,4.5); // too much
	histo->Sumw2();
	
	Long_t nentries = tree->GetEntries();
	for(Long_t i = 0; i < nentries; i++) {
		tree->GetEntry(i);

		// wjets
		if(process == "wjets_light") {
			if(wjets_class == 0 || wjets_class == 1) continue;
		} else if (process == "wjets_heavy") {
			if(wjets_class != 0 && wjets_class != 1) continue;
		}
		
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
		
		// FIXME
		//histo->Fill(var,weight);
		histo->Fill(TMath::Abs(var),weight);
	}
	if(process == "qcd") histo->Scale(xsec);


	cout << "integral: " << histo->Integral() << endl;
	// write histos
	histo->Write();
	fo->Close();
}

int main()
{
	// varname histoname outfile inputfile
	/*
	//makehisto("eta_lj","tchan","tchan_t","T_t");
	//makehisto("eta_lj","tchan","tchan_tbar","Tbar_t");
	makehisto("eta_lj","tchan","tchan_t","T_t_ToLeptons");
	makehisto("eta_lj","tchan","tchan_tbar","Tbar_t_ToLeptons");
	makehisto("eta_lj","schan","schan_t","T_s");
	makehisto("eta_lj","schan","schan_tbar","Tbar_s");
	makehisto("eta_lj","twchan","twchan_t","T_tW");
	makehisto("eta_lj","twchan","twchan_tbar","Tbar_tW");
	makehisto("eta_lj","ttbar","ttbar_semilept","TTJets_SemiLept");
	makehisto("eta_lj","wjets","wjets1","W1Jets_exclusive");
	makehisto("eta_lj","wjets","wjets2","W2Jets_exclusive");
	makehisto("eta_lj","wjets","wjets3","W3Jets_exclusive");
	makehisto("eta_lj","wjets","wjets4","W4Jets_exclusive");
	makehisto("eta_lj","zjets","zjets","DYJets");
	makehisto("eta_lj","diboson","ww","WW");
	makehisto("eta_lj","diboson","wz","WZ");
	makehisto("eta_lj","diboson","zz","ZZ");
	//makehisto("eta_lj","qcd","qcd","QCDMu");
	makehisto("eta_lj","qcd","qcd","QCDShape");
	makehisto("eta_lj","DATA","DATA_SingleMu","SingleMu");
	*/

	makehisto("eta_lj","tchan","tchan_t","T_t_ToLeptons");
	makehisto("eta_lj","tchan","tchan_tbar","Tbar_t_ToLeptons");
	makehisto("eta_lj","top","schan_t","T_s");
	makehisto("eta_lj","top","schan_tbar","Tbar_s");
	makehisto("eta_lj","top","twchan_t","T_tW");
	makehisto("eta_lj","top","twchan_tbar","Tbar_tW");
	makehisto("eta_lj","top","ttbar_semilept","TTJets_SemiLept");
	makehisto("eta_lj","top","ttbar_fulllept","TTJets_FullLept");
	makehisto("eta_lj","wzjets","wjets1","W1Jets_exclusive");
	makehisto("eta_lj","wzjets","wjets2","W2Jets_exclusive");
	makehisto("eta_lj","wzjets","wjets3","W3Jets_exclusive");
	makehisto("eta_lj","wzjets","wjets4","W4Jets_exclusive");
	makehisto("eta_lj","wzjets","zjets","DYJets");
	makehisto("eta_lj","wzjets","ww","WW");
	makehisto("eta_lj","wzjets","wz","WZ");
	makehisto("eta_lj","wzjets","zz","ZZ");
	//makehisto("eta_lj","qcd","qcd","QCDMu");
	makehisto("eta_lj","qcd","qcd","QCDShape");
	makehisto("eta_lj","DATA","DATA_SingleMu","SingleMu");

	/*
	// split wjets flavor
	makehisto("eta_lj","wjets_light","wjets1_light","W1Jets_exclusive");
	makehisto("eta_lj","wjets_light","wjets2_light","W2Jets_exclusive");
	makehisto("eta_lj","wjets_light","wjets3_light","W3Jets_exclusive");
	makehisto("eta_lj","wjets_light","wjets4_light","W4Jets_exclusive");
	
	//
	makehisto("eta_lj","wjets_heavy","wjets1_heavy","W1Jets_exclusive");
	makehisto("eta_lj","wjets_heavy","wjets2_heavy","W2Jets_exclusive");
	makehisto("eta_lj","wjets_heavy","wjets3_heavy","W3Jets_exclusive");
	makehisto("eta_lj","wjets_heavy","wjets4_heavy","W4Jets_exclusive");
	
	makehisto("eta_lj","tchan","tchan_t","T_t_ToLeptons");
	makehisto("eta_lj","tchan","tchan_tbar","Tbar_t_ToLeptons");
	makehisto("eta_lj","top","schan_t","T_s");
	makehisto("eta_lj","top","schan_tbar","Tbar_s");
	makehisto("eta_lj","top","twchan_t","T_tW");
	makehisto("eta_lj","top","twchan_tbar","Tbar_tW");
	makehisto("eta_lj","top","ttbar_semilept","TTJets_SemiLept");
	makehisto("eta_lj","top","ttbar_fulllept","TTJets_FullLept");
	makehisto("eta_lj","zjets","zjets","DYJets");
	makehisto("eta_lj","zjets","ww","WW");
	makehisto("eta_lj","zjets","wz","WZ");
	makehisto("eta_lj","zjets","zz","ZZ");
	//makehisto("eta_lj","qcd","qcd","QCDMu");
	makehisto("eta_lj","qcd","qcd","QCDShape");
	makehisto("eta_lj","DATA","DATA_SingleMu","SingleMu");
	*/

}
