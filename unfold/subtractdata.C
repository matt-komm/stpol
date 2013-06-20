#include "binnings.h"
#include "utils.hpp"

TH1D* subtracted()
{
	TH1D *hdata = rebin("DATA");

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

	TH1D *httbar = rebin("MC_ttbar");
	TH1D *hwjets = rebin("MC_wjets");
	TH1D *hzjets = rebin("MC_zjets");

	// FIXME
	Double_t lumi = 1231;
	httbar->Scale(lumi);
	hwjets->Scale(lumi);
	hzjets->Scale(lumi);

	// FIXME hardcoded for now
	httbar->Scale(sf_ttbar);
	hwjets->Scale(sf_wjets);
	hzjets->Scale(sf_zjets);

	cout << "data events: " << hdata->Integral() << endl;
	cout << "ttbar events: " << httbar->Integral() << endl;
	cout << "wjets events: " << hwjets->Integral() << endl;
	cout << "zjets events: " << hzjets->Integral() << endl;



	hdata->Add(httbar, -1);
	hdata->Add(hwjets, -1);
	hdata->Add(hzjets, -1);
	
	cout << "subtracted data events: " << hdata->Integral() << endl;

	return hdata;
}

void subtractdata()
{
	// FIXME pseudo data
	TFile *fo = new TFile("histos/subtracted_data.root","RECREATE");
	fo->cd();

	TH1D *hsignal = subtracted();

	hsignal->Draw();
	hsignal->Write();
}
