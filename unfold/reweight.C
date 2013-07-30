#include <TFile.h>
#include <TChain.h>

#include "binnings.h"
#include "xsec.h"
#include "info.h"
#include "utils.hpp"

#include <iostream>

void reweight()
{
	TChain *chain = new TChain("trees/Events");

	chain->Add(file_t_presel);
	
	TFile *fo = new TFile("histos/efficiency_test2.root","RECREATE");

	// Enable correct errors
	TH1::SetDefaultSumw2(true);

	fo->cd();
	TH1F *hgen_presel = new TH1F("hgen_presel","hgen_presel",100, var_min, var_max);
	TH1F *hgen_presel_rebin = new TH1F("hgen_presel_rebin","hgen_presel_rebin",bin_x,list_x);

	Float_t true_costheta = 0.0;
	Int_t true_leptonid = 0.0;

        chain->SetBranchAddress("true_cos_theta", &true_costheta);
        chain->SetBranchAddress("true_lepton_pdgId", &true_leptonid); 


	Long_t nentries = chain->GetEntries();
        for(Long_t i = 0; i < nentries; i++) {
                chain->GetEntry(i);

		if(true_leptonid != -13) continue;

		//cout << true_costheta << endl;

		Float_t weight = 1.0;

		weight = (0.25*true_costheta+0.5)/(0.440209*true_costheta+0.5);
		//cout << weight << endl;

		hgen_presel->Fill(true_costheta,weight);
		hgen_presel_rebin->Fill(true_costheta,weight);
	}

	
	Float_t xsec_t = get_xsec("T_t_ToLeptons");
	Float_t xsec_tbar = get_xsec("Tbar_t_ToLeptons");
	
	hgen_presel->Scale(xsec_t);

	cout << asymmetry(hgen_presel) << endl;
/*	
	TH1F *hgen = new TH1F("hgen","hgen",100, var_min, var_max);
	TH1F *hgen_rebin = new TH1F("hgen_rebin","hgen_rebin",bin_x,list_x);
	TH1F *hrec = new TH1F("hrec","hrec",100, var_min, var_max);
	
	TChain *chain2 = new TChain("trees/Events");

	chain2->Add(file_t);
	Long_t nentries_t = chain2->GetEntries();
	//chain2->Add(file_tbar);
	
	Float_t weight = 1.0;
	Float_t pu_weight = 1.0;
	Float_t btag_weight = 1.0;
	Float_t muonID_weight = 1.0;
	Float_t muonIso_weight = 1.0;
	Float_t muonTrigger_weight = 1.0;

	chain2->SetBranchAddress("pu_weight", &pu_weight);
	chain2->SetBranchAddress("b_weight_nominal", &btag_weight);
	chain2->SetBranchAddress("muon_IDWeight", &muonID_weight);
	chain2->SetBranchAddress("muon_IsoWeight", &muonIso_weight);
	chain2->SetBranchAddress("muon_TriggerWeight", &muonTrigger_weight);

	// cut variables
	Float_t eta_lj = 0;
	Float_t muonIso = 0;
	Float_t jetrms = 0;
	Float_t mtw = 0;
	chain2->SetBranchAddress("mu_iso", &muonIso);
	chain2->SetBranchAddress("rms_lj", &jetrms);
	chain2->SetBranchAddress("mt_mu", &mtw);
	chain2->SetBranchAddress("eta_lj", &eta_lj);

	Float_t variable_x = 0;
	Float_t variable_y = 0;
	chain2->SetBranchAddress(var_x, &variable_x);
	chain2->SetBranchAddress(var_y, &variable_y);
	
	TH1::SetDefaultSumw2(true);
	
	TFile *f_t = new TFile(file_t);
	TFile *f_tbar = new TFile(file_tbar);
	TH1I *hcount_t = (TH1I*)f_t->Get("trees/count_hist");
	TH1I *hcount_tbar = (TH1I*)f_tbar->Get("trees/count_hist");
	Int_t count_t = hcount_t->GetBinContent(1); 
	Int_t count_tbar = hcount_tbar->GetBinContent(1); 
	f_t->Close();
	f_tbar->Close();

	Long_t nentries2 = chain2->GetEntries();
	for(Long_t i = 0; i < nentries2; i++) {
		chain2->GetEntry(i);
		 		
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
		// FIXME reweight costheta
		weight *= 0.215*(1+true_costheta)+0.5/0.440209;
		
		if(variable_y > var_max) continue;
		if(variable_y < var_min) continue;

		hgen->Fill(variable_x,weight);
		hgen_rebin->Fill(variable_x,weight);
		hrec->Fill(variable_y,weight);
	}


	TH1F *heff = (TH1F*)hgen_rebin->Clone("efficiency");
	heff->SetTitle("efficiency");
	std::cout << heff->Integral() << std::endl;
	heff->Divide(hgen_presel_rebin);
	std::cout << heff->Integral() << std::endl;

	fo->cd();
	hgen_presel->Write();
	hgen_presel_rebin->Write();

	hgen->Write();
	hgen_rebin->Write();
	heff->Write();

	//fo->Close();
	*/
	fo->cd();
	hgen_presel->Write();
	hgen_presel_rebin->Write();
}

int main()
{
	reweight();
}
