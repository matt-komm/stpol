#include <TChain.h>
#include <TFile.h>

#include "binnings.h"
#include "info.h"
#include "xsec.h"
#include "utils.hpp"

void rebin()
{
	//TFile *fo = new TFile("histos/rebinned_comphep.root","RECREATE");
	TFile *fo = new TFile("histos/rebinned.root","RECREATE");

	TChain *chain = new TChain("trees/Events");

	// Poweg
	chain->Add(file_t);
	Long_t nentries_t = chain->GetEntries();
	chain->Add(file_tbar);
	
	// Comphep
	//chain->Add("trees_8TeV/08_07_2013//mu/presel/TToBMuNu_comphep_t-channel.root");

	fo->cd();
	
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



	Float_t var_gen = 0;
	Float_t var_rec = 0;
	
	chain->SetBranchAddress(var_y, &var_rec);
	chain->SetBranchAddress(var_x, &var_gen);
	
	TH1::SetDefaultSumw2(true);
	
	// histograms
	TH1F *hgen_rebin = new TH1F(var_x+"_rebin",var_x+" rebinned",bin_x,list_x);
	TH1F *hrec_rebin = new TH1F(var_y+"_rebin",var_y+" rebinned",bin_y,list_y);
	
	TH2F *hgenrec_rebin = new TH2F("matrix","matrix",bin_x,list_x,bin_y,list_y);

	hrec_rebin->Sumw2();
	hgen_rebin->Sumw2();
	hgenrec_rebin->Sumw2();
	
	/*
	TFile *f = new TFile("trees_8TeV/08_07_2013//mu/presel/TToBMuNu_comphep_t-channel.root");
	TH1I *hcount = (TH1I*)f->Get("trees/count_hist");
	Int_t count = hcount->GetBinContent(1); 
	f->Close();
	*/
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

		//weight *= xsec_t+xsec_tbar;
		//weight /= (Float_t)count;
		
		if(i <= nentries_t) {
			weight *= xsec_t;
			weight /= (Float_t)count_t;
		} else {
			weight *= xsec_tbar;
			weight /= (Float_t)count_tbar;
		}

		if(var_gen > var_max) continue;
		fill_nooverflow_1d(hgen_rebin,var_gen,weight);
		fill_nooverflow_1d(hrec_rebin,var_rec,weight);
		fill_nooverflow_2d(hgenrec_rebin,var_gen,var_rec,weight);
	}

	fo->cd();
	// write histos
	hrec_rebin->Write();
	hgen_rebin->Write();
	hgenrec_rebin->Write();
	fo->Close();
}

int main()
{
	rebin();

	return 0;
}
