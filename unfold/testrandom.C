#include "binnings.h"

#define NPSEUDO 1000

void testrandom()
{
	//TH1::SetDefaultSumw2(true);
	TFile *f = new TFile("histos/rebinned.root");
	TH1D *hrec = (TH1D*)f->Get(var_y+"_rebin");
	
	Int_t expected = 6142.5; // Events expected in data: approx at 20/fb
	hrec->Scale(expected/hrec->Integral());
	
	TFile *fo = new TFile("histos/testrandom.root","RECREATE");
	fo->cd();
	
	TH1D *hPull[bin_x];
	TH1D *hBin[bin_x];

	TString pull_name = "pull_";
	TString bin_name = "reldiff_";
	for(Int_t i=1; i <= bin_x; i++) {
		TString pname = pull_name;
		pname += i;
		TString bname = bin_name;
		bname += i;
		hPull[i-1] = new TH1D(pname,pname,100,-5.0,5.0);
		hBin[i-1] = new TH1D(bname,bname,200,-1.0,1.0);
	}

	for(Int_t p=1; p<=NPSEUDO; p++) {
		TH1D *hpseudo = new TH1D("pseudo","pseudo", bin_y, list_y);
		hpseudo->Reset();
		// FIXME Wrong, use poisson instead
		hpseudo->FillRandom(hrec,expected);
		//for(Int_t j=0; j<expected; j++) hpseudo->Fill(hrec->GetRandom());

	
		for(Int_t k=1; k<=bin_x; k++) {
			Double_t diff = (hrec->GetBinContent(k) - hpseudo->GetBinContent(k));
			
			hPull[k-1]->Fill(diff/hpseudo->GetBinError(k));
			hBin[k-1]->Fill(diff/hrec->GetBinContent(k));
		}

	}
	
	for(Int_t i=0; i < bin_x; i++) {
		hBin[i]->Write();
		hPull[i]->Write();
	}

	//fo->Close();

}
