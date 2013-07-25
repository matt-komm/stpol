#ifndef HISTO_HPP
#define HISTO_HPP

#include <TH1F.h>
#include <TChain.h>
#include <TFile.h>

#include "xsec.h"
#include "binnings.h"
#include "info.h"

void fillhisto(TString variable, TH1F *histo)
{	
	TChain *chain = new TChain("trees/Events");

	chain->Add(file_t);
	Long_t nentries_t = chain->GetEntries();
	chain->Add(file_tbar);
	
	Float_t weight = 1.0;
	Float_t pu_weight = 1.0;
	Float_t btag_weight = 1.0;
	Float_t muonID_weight = 1.0;
	Float_t muonIso_weight = 1.0;
	Float_t muonTrigger_weight = 1.0;

	chain->SetBranchAddress("pu_weight", &pu_weight);
	chain->SetBranchAddress("b_weight_nominal", &btag_weight);
	chain->SetBranchAddress("muon_IDWeight", &muonID_weight);
	chain->SetBranchAddress("muon_IsoWeight", &muonIso_weight);
	chain->SetBranchAddress("muon_TriggerWeight", &muonTrigger_weight);

	// cut variables
	Float_t eta_lj = 0;
	Float_t muonIso = 0;
	Float_t jetrms = 0;
	Float_t mtw = 0;
	chain->SetBranchAddress("mu_iso", &muonIso);
	chain->SetBranchAddress("rms_lj", &jetrms);
	chain->SetBranchAddress("mt_mu", &mtw);
	chain->SetBranchAddress("eta_lj", &eta_lj);


	Int_t HLT_v11 = 0;
        Int_t HLT_v12 = 0;
        Int_t HLT_v13 = 0;
        Int_t HLT_v14 = 0;
        Int_t HLT_v15 = 0;
        Int_t HLT_v16 = 0;
        Int_t HLT_v17 = 0;
	
	chain->SetBranchAddress("HLT_IsoMu24_eta2p1_v11", &HLT_v11);
        chain->SetBranchAddress("HLT_IsoMu24_eta2p1_v12", &HLT_v12);
        chain->SetBranchAddress("HLT_IsoMu24_eta2p1_v13", &HLT_v13);
        chain->SetBranchAddress("HLT_IsoMu24_eta2p1_v14", &HLT_v14);
        chain->SetBranchAddress("HLT_IsoMu24_eta2p1_v15", &HLT_v15);
        chain->SetBranchAddress("HLT_IsoMu24_eta2p1_v16", &HLT_v16);
        chain->SetBranchAddress("HLT_IsoMu24_eta2p1_v17", &HLT_v17);

        Int_t n_jets = 0;
        Int_t n_tags = 0;
        Int_t n_veto_ele = -1;
        Int_t n_veto_mu = -1;
        Float_t pt_lj = 0;
        Float_t pt_bj = 0;
        Float_t top_mass = 0;
        chain->SetBranchAddress("n_jets", &n_jets);
        chain->SetBranchAddress("n_tags", &n_tags);
        chain->SetBranchAddress("n_veto_ele", &n_veto_ele);
        chain->SetBranchAddress("n_veto_mu", &n_veto_mu);
        chain->SetBranchAddress("pt_lj", &pt_lj);
        chain->SetBranchAddress("pt_bj", &pt_bj);
        chain->SetBranchAddress("top_mass", &top_mass);


	Float_t var = 0;
	chain->SetBranchAddress(variable, &var);
	
	TH1::SetDefaultSumw2(true);
	
	//TFile *f_t = new TFile(file_t);
	//TFile *f_tbar = new TFile(file_tbar);
	TFile *f_t = new TFile(file_t);
	TFile *f_tbar = new TFile(file_tbar);
	
	TH1I *hcount_t = (TH1I*)f_t->Get("trees/count_hist");
	TH1I *hcount_tbar = (TH1I*)f_tbar->Get("trees/count_hist");
	Int_t count_t = hcount_t->GetBinContent(1); 
	Int_t count_tbar = hcount_tbar->GetBinContent(1); 
	f_t->Close();
	f_tbar->Close();

	Float_t xsec_t = get_xsec("T_t_ToLeptons");
	Float_t xsec_tbar = get_xsec("Tbar_t_ToLeptons");
	
	Long_t nentries = chain->GetEntries();
	for(Long_t i = 0; i < nentries; i++) {
		chain->GetEntry(i);
		 		
		if(TMath::Abs(eta_lj) < 2.5) continue;
		if(jetrms >= 0.025) continue;
		if(mtw <= 50) continue;
                if(!(HLT_v11 == 1 || HLT_v12 == 1 || HLT_v13 == 1 || HLT_v14 == 1 || HLT_v15 == 1 || HLT_v16 == 1 || HLT_v17)) continue;
                if(n_jets != 2) continue;
                if(n_tags != 1) continue;
                if(n_veto_ele != 0) continue;
                if(n_veto_mu != 0) continue;
                if(pt_lj <= 40) continue;
                if(pt_bj <= 40) continue;
                if(top_mass <= 130 || top_mass >= 220) continue;

		// weight depending on sample 
		weight = pu_weight*btag_weight*muonID_weight*muonIso_weight*muonTrigger_weight;
		weight *= lumi;
		if(i <= nentries_t) {
			weight *= xsec_t;
			weight /= (Float_t)count_t;
		} else {
			weight *= xsec_tbar;
			weight /= (Float_t)count_tbar;
		}
		
		if(var > var_max) continue;
		if(var < var_min) continue;

		histo->Fill(var,weight);
	}

}

#endif
