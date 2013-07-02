#include "binnings.h"
#include "utils.hpp"

TH1D* subtracted()
{
	TFile *f1 = new TFile("histos/pseudo_data.root");

	TH1D *hdata = (TH1D*)f1->Get(var_y+"__DATA");

	vector<TString> names;
	vector<Double_t> scales;
	vector<Double_t> uncs;

	Double_t sf_ttbar = 1.0;
	Double_t sf_wjets= 1.0;
	Double_t sf_zjets= 1.0;

	cout << "Reading fit results: " << endl;
	read_fitres(names,scales,uncs);
	for(int i = 0; i < names.size(); i++)
	{
		cout << names.at(i) << " " << scales.at(i) << " " << uncs.at(i) << endl;
		if (names.at(i) == "ttbar") sf_ttbar = scales.at(i);
		if (names.at(i) == "wjets") sf_wjets = scales.at(i);
		if (names.at(i) == "zjets") sf_zjets = scales.at(i);
	}

	// read backgrounds
	TH1D *httbar = (TH1D*)f1->Get(var_y+"__ttbar");
	TH1D *hwjets = (TH1D*)f1->Get(var_y+"__wjets");
	TH1D *hzjets = (TH1D*)f1->Get(var_y+"__zjets");
	
	// FIXME hardcoded for now
	httbar->Scale(sf_ttbar);
	hwjets->Scale(sf_wjets);
	hzjets->Scale(sf_zjets);

	cout << "data events: " << hdata->Integral() << endl;
	cout << "ttbar events: " << httbar->Integral() << endl;
	cout << "wjets events: " << hwjets->Integral() << endl;
	cout << "zjets events: " << hzjets->Integral() << endl;


	// subtract
	hdata->Add(httbar, -1);
	hdata->Add(hwjets, -1);
	hdata->Add(hzjets, -1);
	
	cout << "subtracted data events: " << hdata->Integral() << endl;

	return hdata;
}

void subtractpdata()
{
	TFile *fo = new TFile("histos/subtracted_pdata.root","RECREATE");
	fo->cd();

	TH1D *hsignal = subtracted();

	hsignal->Draw();
	fo->cd();
	hsignal->Write();
}
