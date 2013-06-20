#include "helpers.hpp"
#include "binnings.h"
#include "info.h"
#include "xsec.h"

#include <TChain.h>
#include <TString.h>
#include <TH1F.h>

//Int_t MAXBIN = 100000;
//Int_t MAXBIN = 10000;

#define MAXBIN 10000

TH1F* gethisto(TString variable)
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

	Float_t var = 0;
	chain->SetBranchAddress(variable, &var);
	
	TH1::SetDefaultSumw2(true);
	TH1F *histo = new TH1F(variable, variable, MAXBIN, var_min, var_max);
	
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
		
		if(var > var_max) continue;
		if(var < var_min) continue;

		histo->Fill(var,weight);
	}

	return (TH1F*)histo;
}

void getbinning(const TH1F* histo, const Int_t bins)
{
	Float_t totint = histo->Integral(0, MAXBIN);
	Float_t evbin = totint/bins;

	cout << "Events: " << totint << endl;
	cout << "Events per bin: " << evbin << endl;

	Float_t edges[bins+1];
	
	cout << "{" << var_min << ", ";
	edges[0] = var_min;
	Int_t iedge = 1;

	Int_t prevbin = 0;
	for(Long_t k=1; k<=MAXBIN; k++)
	{
		// FIXME: Somewhat slow
		Float_t integral = histo->Integral(prevbin+1, k);
		if(integral>=evbin)
		{
        		Float_t newedge = histo->GetXaxis()->GetBinUpEdge(k);
			
			// Set bin edge to 0 in order to calculate the asymmetry
        		if(TMath::Abs(newedge)<0.01) newedge = 0;
        
			edges[iedge++] = newedge;
			cout << newedge << ", ";
        		
			prevbin = k;
		}
	}
	//cout << integral << " ";

	Float_t lastedge = histo->GetXaxis()->GetBinUpEdge(MAXBIN);
	edges[bins] = lastedge;
	cout << lastedge << "};" << endl;
}

void findbinning()
{

	// generated 8
	// reconstructed 16

	TH1F *histo_gen = gethisto(var_x);
	TH1F *histo_rec = gethisto(var_y);

	// generated
	//getbinning(histo_gen, 5);
	// reconstructed
	//getbinning(histo_rec, 10);
	
	// generated
//	getbinning(histo_gen, 7);
	// reconstructed
//	getbinning(histo_rec, 14);
	
	// generated
	getbinning(histo_gen, 3);
	// reconstructed
	getbinning(histo_rec, 6);

}

int main()
{
	findbinning();

	return 0;
}
