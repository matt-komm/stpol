#include <TFile.h>
#include <TString.h>
#include <TH1F.h>

#include <cstdlib>
#include <iostream>
#include <fstream>

using namespace std;

void read_fitres(vector<TString> &names, vector<Float_t> &scales, vector<Float_t> &uncs)
{
        TString name;
        Float_t scale, unc;
        
        ifstream ifs;
        ifs.open("results.txt");
        if(!ifs.good()) {
                cout << "Could not open fit results file!" << endl;
                exit(1);
        }
        while (ifs >> name >> scale >> unc) {
                names.push_back(name);
                scales.push_back(scale);
                uncs.push_back(unc);
        } 
        ifs.close();
        
}

void pseudodata()
{
	TString var_y = "eta_lj";
	TFile *f = new TFile("histos/lqeta.root");
	TFile *fo = new TFile("histos/pseudo_data.root","RECREATE");
	fo->cd();
	
	vector<TString> names;
	vector<Float_t> scales;
	vector<Float_t> uncs;
	vector<TH1F*> histos;

	read_fitres(names,scales,uncs);
	Int_t nbkgs = names.size()-1;
	
	TH1::SetDefaultSumw2(true);
	TH1F *hsignal = (TH1F*)f->Get(var_y+"__tchan");
	hsignal->Scale(scales[0]);
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
		histo->Scale(scales[i+1]);
		added->Add(histo);
		histo->Write();
	}

	cout << added->Integral() << endl;
	fo->cd();
	added->Write();
	fo->Close();
}

int main()
{
	pseudodata();

	return 0;
}
