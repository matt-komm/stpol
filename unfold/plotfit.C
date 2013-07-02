#include <TString.h>
#include <TCanvas.h>
#include <THStack.h>
#include <TFile.h>
#include <TH1F.h>

#include "binnings.h"
#include "utils.hpp"

void plotfit()
{
	vector<TString> names;
	vector<Float_t> scales;
	vector<Float_t> uncs;
	vector<TH1F*> histos;
	TH1F *hsignal;

	read_fitres(names,scales,uncs);
	Int_t nbkgs = names.size()-1;

	TCanvas *c = new TCanvas("c","canvas",1024,768);
	//c->SetLogy();
	THStack *hstack = new THStack("hstack","stack plot");

	// FIXME
//	TFile *f = new TFile("histos/data.root");
	TFile *f = new TFile("histos/pseudo_data.root");

	TH1F *hdata = (TH1F*)f->Get(var_y+"__DATA");

	hsignal = (TH1F*)f->Get(var_y+"__tchan");
//	hsignal->Scale(scales[0]);
	hsignal->SetLineColor(kBlack);
	hsignal->SetFillColor(kRed);
	hstack->Add(hsignal);

	// Read in background histograms
	for(int i = 0; i < nbkgs ; i++) {
		TString name = names.at(i+1);
		TH1F *histo = (TH1F*)f->Get(var_y+"__"+name);
				
		// Scale histos
//		histo->Scale(scales[i+1]);
		histo->SetLineColor(kBlack);
		histo->SetFillColor((i+1)*10);
		histos.push_back(histo);
		hstack->Add(histo);
	}

	hdata->SetLineColor(kBlack);
	hdata->SetMarkerStyle(20);
	hdata->SetStats(0);
	hdata->SetTitle("");
	hdata->GetXaxis()->SetTitle(varname);
	hdata->GetYaxis()->SetTitle("Events");
	hdata->SetMinimum(0);
	hdata->Draw();

	hstack->Draw("HIST SAME");
	hdata->Draw("SAME");

	gPad->RedrawAxis();

	c->Print("plots/stack.png");
	c->Print("plots/stack.pdf");
}

int main()
{
	plotfit();

	return 0;
}
