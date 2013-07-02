#include <TFile.h>

#include "binnings.h"
#include "histo.hpp"
#include "xsec.h"
#include "info.h"

#include <iostream>

void efficiency()
{
	TChain *chain = new TChain("trees/Events");
	TChain *chain2 = new TChain("trees/Events");

	chain->Add(file_t_presel);
	chain2->Add(file_tbar_presel);
	
	TFile *fo = new TFile("histos/efficiency.root","RECREATE");

	// Enable correct errors
	TH1::SetDefaultSumw2(true);

	fo->cd();
	TH1F *hgen_presel_t = new TH1F("hgen_presel_t","hgen_presel_t",100, var_min, var_max);
	TH1F *hgen_presel_tbar = new TH1F("hgen_presel_tbar","hgen_presel_tbar",100, var_min, var_max);
	TH1F *hgen_presel_t_rebin = new TH1F("hgen_presel_t_rebin","hgen_presel_t_rebin",bin_x,list_x);
	TH1F *hgen_presel_tbar_rebin = new TH1F("hgen_presel_tbar_rebin","hgen_presel_tbar_rebin",bin_x,list_x);
	// FIXME lepton id only for muons
	chain->Draw(var_x+">>hgen_presel_t","true_lepton_pdgId==-13");
	chain2->Draw(var_x+">>hgen_presel_tbar","true_lepton_pdgId==13");
	chain->Draw(var_x+">>hgen_presel_t_rebin","true_lepton_pdgId==-13");
	chain2->Draw(var_x+">>hgen_presel_tbar_rebin","true_lepton_pdgId==13");
	
	/*
	chain->Draw(var_x+">>hgen_presel_t","true_lepton_pdgId!=0");
	chain2->Draw(var_x+">>hgen_presel_tbar","true_lepton_pdgId!=0");
	chain->Draw(var_x+">>hgen_presel_t_rebin","true_lepton_pdgId!=0");
	chain2->Draw(var_x+">>hgen_presel_tbar_rebin","true_lepton_pdgId!=0");
	*/
	
	Float_t xsec_t = get_xsec("T_t_ToLeptons");
	Float_t xsec_tbar = get_xsec("Tbar_t_ToLeptons");
	// divdide # events and mult. xsec, BR
	// FIXME scale hgen_presel_rebin
	//hgen_presel_rebin->Scale(xsec*0.108/hgen_presel_rebin->Integral());
	
	hgen_presel_t->Scale(xsec_t);
	hgen_presel_tbar->Scale(xsec_tbar);

	TH1F *hgen_presel = (TH1F*)hgen_presel_t->Clone("hgen_presel");
	hgen_presel->Add(hgen_presel_tbar);
	
	hgen_presel_t_rebin->Scale(xsec_t/hgen_presel_t_rebin->Integral());
	hgen_presel_tbar_rebin->Scale(xsec_tbar/hgen_presel_tbar_rebin->Integral());

	TH1F *hgen_presel_rebin = (TH1F*)hgen_presel_t_rebin->Clone("hgen_presel_rebin");
	hgen_presel_rebin->Add(hgen_presel_tbar_rebin);
	hgen_presel_rebin->Scale((xsec_t+xsec_tbar)*lumi/hgen_presel_rebin->Integral());
	std::cout << hgen_presel_rebin->Integral() << std::endl;
	
	TH1F *hgen = new TH1F("hgen","hgen",100, var_min, var_max);
	TH1F *hgen_rebin = new TH1F("hgen_rebin","hgen_rebin",bin_x,list_x);
	TH1F *hrec = new TH1F("hrec","hrec",100, var_min, var_max);
	fillhisto(var_x,hgen);
	fillhisto(var_x,hgen_rebin);
	fillhisto(var_y,hrec);

	TH1F *heff = (TH1F*)hgen_rebin->Clone("efficiency");
	heff->SetTitle("efficiency");
	std::cout << heff->Integral() << std::endl;
	heff->Divide(hgen_presel_rebin);
	std::cout << heff->Integral() << std::endl;

	fo->cd();
	hgen_presel->Write();
	hgen_presel_rebin->Write();
	hgen->Write();
	hgen_rebin->Write();
	hrec->Write();
	heff->Write();

	fo->Close();
}

int main()
{
	efficiency();
}
