#include <TString.h>
#include <TFile.h>
#include <TH1F.h>
#include <TH2F.h>
#include <TMath.h>
#include <iostream>

#include "utils.hpp"
#include "binnings.h"

using namespace std;

Double_t calc_asymmetry_syst(TString syst)
{
	TFile *f1 = new TFile("histos/unfolded_syst_"+syst+".root");
	TFile *f3 = new TFile("histos/efficiency.root");

	TH1F *hunf = (TH1F*)f1->Get("unfolded");
	TH1F *hgen_presel = (TH1F*)f3->Get("hgen_presel");
	//TH1F *hgen_presel_rebin = (TH1F*)f3->Get("hgen_presel_rebin");
	
	TH1F *hasy= (TH1F*)f1->Get("asymmetry");
	//TH1F *hStatErr = (TH1F*)f1->Get("staterr");
	
	// unfolded in bins of generated
	TH1F *hunf_rebin_width = new TH1F(var_y+"_unf",var_y+"_unf",bin_x,list_x);
	for(Int_t i = 1; i <= bin_x; i++) {
		hunf_rebin_width->SetBinContent(i,hunf->GetBinContent(i));
		hunf_rebin_width->SetBinError(i,hunf->GetBinError(i));
	}

	Double_t asy_gen = asymmetry(hgen_presel);
	Double_t asy_unf = hasy->GetMean();

	cout << endl << asy_gen << " " << asy_unf << endl;

	Double_t diff = asy_gen - asy_unf;
	//Double_t uncertainty = diff/asy_gen;
	Double_t uncertainty = diff;
	cout << uncertainty << endl;

	return uncertainty;
}

int main()
{	
	vector<TString> systematics;
	systematics.push_back("en__down");
	systematics.push_back("en__up");
	systematics.push_back("mass__down");
	systematics.push_back("mass__up");
	systematics.push_back("matching__down");
	systematics.push_back("matching__up");
	systematics.push_back("tchan_scale__down");
	systematics.push_back("tchan_scale__up");
	systematics.push_back("top_scale__down");
	systematics.push_back("top_scale__up");
	systematics.push_back("unclusen__down");
	systematics.push_back("unclusen__up");

	Double_t uncertainty = 0;

        for(vector<TString>::iterator it = systematics.begin(); it != systematics.end(); it++) {
		cout << (*it) << "\t\t";
		uncertainty += TMath::Power(calc_asymmetry_syst(*it),2);
	}
	cout << "========================" << endl;
	cout << "relative total uncertainty: " << TMath::Sqrt(uncertainty) << endl;

	return 0;
}
