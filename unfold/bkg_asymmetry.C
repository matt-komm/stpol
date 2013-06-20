#include <TString.h>
#include <TFile.h>
#include <TH1F.h>
#include <TH2D.h>
#include <TMath.h>
#include <iostream>

#include "utils.hpp"
#include "binnings.h"

using namespace std;

void calc_asymmetry()
{
	TFile *f = new TFile("histos/data.root");

	vector<TString> names;
	vector<Float_t> scales;
	vector<Float_t> uncs;

	read_fitres(names,scales,uncs);
	TH1F *hsignal = (TH1F*)f->Get(var_y+"__tchan");
	hsignal->Scale(scales[0]);
	cout << "Signal:" << endl;
	cout << asymmetry(hsignal) << endl;
	int nbkgs = names.size()-1;
	for(int i = 0; i < nbkgs ; i++) {
		TString name = names.at(i+1);
		TH1F *histo = (TH1F*)f->Get(var_y+"__"+name);
			
		// Scale histos
		histo->Scale(scales[i+1]);

		cout << name << endl;
		cout << asymmetry(histo) << endl;
	}

	TH1F *hdata = (TH1F*)f->Get(var_y+"__DATA");
	cout << "DATA" << endl;
	cout << asymmetry(hdata) << endl;
}

int main()
{
	calc_asymmetry();

	return 0;
}
