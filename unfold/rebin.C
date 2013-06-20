#include <TChain.h>

#include "binnings.h"
#include "info.h"
#include "xsec.h"
#include "helpers.hpp"

void rebin()
{
	TFile *fo = new TFile("histos/rebinned.root","RECREATE");

	TChain *chain = new TChain("trees/Events");

	chain->Add(file_t);
	Long_t nentries_t = chain->GetEntries();
	chain->Add(file_tbar);
	
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
