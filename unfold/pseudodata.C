#include <TFile.h>
#include <TString.h>
#include <TH1F.h>

#include "utils.hpp"
#include "binnings.h"

void pseudodata()
{
	TFile *f = new TFile("histos/data.root");
	TFile *fo = new TFile("histos/pseudo_data.root","RECREATE");
	fo->cd();
	
	vector<TString> names;
	vector<Float_t> scales;
	vector<Float_t> uncs;
	vector<TH1F*> histos;

	read_fitres("nominal",names,scales,uncs);
	Int_t nbkgs = names.size()-1;
	
	TH1::SetDefaultSumw2(true);
	TH1F *hsignal = (TH1F*)f->Get(var_y+"__tchan");
	//hsignal->Scale(scales[0]);
	// Artificially enhance signal fraction
	// FIXME
	//hsignal->Scale(2);
	hsignal->Write();
	TH1F *added = (TH1F*)hsignal->Clone(var_y+"__DATA");
	
	// Read in background histograms
	for(int i = 0; i < nbkgs ; i++) {
		TString name = names.at(i+1);
		TH1F *histo = (TH1F*)f->Get(var_y+"__"+name);
				
		// Scale histos
		//histo->Scale(scales[i+1]);
		added->Add(histo);
		histo->Write();
	}

	//cout << added->Integral() << endl;
	fo->cd();
	added->Write();
	fo->Close();
}

int main()
{
	pseudodata();

	return 0;
}
