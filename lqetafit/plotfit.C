#include "TString.h"
#include "TFile.h"
#include "TCanvas.h"
#include "TH1F.h"
#include "THStack.h"
#include "TLegend.h"

#include <vector>

#include <iostream>
#include <fstream>

using namespace std;

void plotfit()
{
	vector<TString> names;
	vector<Float_t> scales;
	vector<Float_t> uncs;
	vector<TH1F*> histos;
	TH1F *hsignal;

	TString var_y = "eta_lj";
	TString name;
	Float_t scale, unc;

	ifstream ifs;
	ifs.open("results.txt");
	while (ifs >> name >> scale >> unc) {
		if(name == "beta_signal") name = "tchan";
		//cout << name << endl;
		names.push_back(name);
		scales.push_back(scale);
		uncs.push_back(unc);
	} 
	ifs.close();
	
	for(unsigned int i = 0; i < names.size(); i++)
		cout << names.at(i) << " " << scales.at(i) << " " << uncs.at(i) << endl;
	
	TCanvas *c = new TCanvas("c","canvas",1024,768);
	THStack *hstack = new THStack("hstack","stack plot");
	TFile *f = new TFile("histos/lqeta.root");
	hsignal = (TH1F*)f->Get(var_y+"__tchan");
	hsignal->Scale(scales[0]);
	hsignal->SetLineColor(kBlack);
	hsignal->SetFillColor(kRed);
	hstack->Add(hsignal);
	TH1F *hadd = (TH1F*)hsignal->Clone();
	
	TLegend *leg = new TLegend(0.7,0.6,0.9,0.9);
        leg->SetTextSize(0.04);
        leg->SetFillColor(0);
        leg->AddEntry(hsignal,"t-channel","f");

	Int_t nbkgs = names.size()-1;
	for(int i = 0; i < nbkgs ; i++) {
		TString name = names.at(i+1);
		TH1F *histo = (TH1F*)f->Get(var_y+"__"+name);
	
		// Scale histos
		histo->Scale(scales[i+1]);

		histo->SetLineColor(kBlack);
		histo->SetFillColor((i+1)*10);

        	leg->AddEntry(histo,name,"f");
		hstack->Add(histo);
		hadd->Add(histo);
	}
	
	TH1F *hdata = (TH1F*)f->Get(var_y+"__DATA");
	hdata->SetLineColor(kBlack);
	hdata->SetMarkerStyle(20);
	hdata->SetStats(0);
	hdata->SetTitle("");
	hdata->GetXaxis()->SetTitle("#eta_{lj}");
	hdata->GetYaxis()->SetTitle("Events");
	hdata->SetMaximum(hdata->GetMaximum()*1.2);
	hdata->Draw();
	
	hstack->Draw("HIST SAME");
	hdata->Draw("SAME");

	leg->Draw();

	cout << "KS: " << hdata->KolmogorovTest(hadd) << endl;

	gPad->RedrawAxis();


	c->Print("stack.png");
	c->Print("stack.pdf");
}

int main()
{
	plotfit();
}
