#include <TString.h>
#include <TFile.h>
#include <TH1F.h>
#include <TH2F.h>
#include <TMath.h>
#include <iostream>

#include "utils.hpp"
#include "binnings.h"

using namespace std;

void calc_asymmetry()
{
	TFile *f1 = new TFile("histos/unfolded.root");
	// FIXME
	TFile *f4 = new TFile("histos/pseudo_data.root");
	//TFile *f5 = new TFile("histos/subtracted_pdata.root");
	TFile *f5 = new TFile("histos/data.root");
	TFile *f3 = new TFile("histos/efficiency.root");
	//TFile *f3 = new TFile("histos/efficiency_comphep.root");

	TH1F *hunf = (TH1F*)f1->Get("unfolded");
	TH2F *herr = (TH2F*)f1->Get("error");
	TH1F *hgen_presel = (TH1F*)f3->Get("hgen_presel");
	TH1F *hgen_presel_rebin = (TH1F*)f3->Get("hgen_presel_rebin");
	TH1F *hgen = (TH1F*)f3->Get("hgen");
	TH1F *hrec = (TH1F*)f3->Get("hrec");
	
	TH1F *hStatErr = (TH1F*)f1->Get("staterr");
	
	TH1F *hpdata = (TH1F*)f4->Get(var_y+"__DATA");
	//TH1F *hsdata = (TH1F*)f5->Get(var_y+"__DATA");
	TH1F *hdata = (TH1F*)f5->Get(var_y+"__DATA");
	
	// unfolded in bins of generated
	TH1F *hunf_rebin_width = new TH1F(var_y+"_unf",var_y+"_unf",bin_x,list_x);
	for(Int_t i = 1; i <= bin_x; i++) {
		hunf_rebin_width->SetBinContent(i,hunf->GetBinContent(i));
		hunf_rebin_width->SetBinError(i,hunf->GetBinError(i));
	}

	cout << "generated (before selection)" << endl;
	cout << asymmetry(hgen_presel) << endl;
	cout << "generated (before selection, rebinned)" << endl;
	cout << asymmetry(hgen_presel_rebin) << endl;
	cout << "generated (after selection)" << endl;
	cout << asymmetry(hgen) << endl;
	cout << "reconstruced" << endl;
	cout << asymmetry(hrec) << endl;
	cout << "unfolded" << endl;
	cout << asymmetry(hunf_rebin_width) << endl;
	cout << "mean stat. error: " << hStatErr->GetMean() << " +- " << hStatErr->GetMeanError() << endl;
	cout << "stat. error: " << error_unfold(herr,hunf_rebin_width) << endl;
	cout << "pseudo DATA" << endl;
	cout << asymmetry(hpdata) << endl;
	//cout << "subtracted pseudo DATA" << endl;
	//cout << asymmetry(hsdata) << endl;
	cout << "DATA" << endl;
	cout << asymmetry(hdata) << endl;
}

int main()
{
	calc_asymmetry();

	return 0;
}
