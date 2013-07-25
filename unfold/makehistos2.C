#include <TFile.h>
#include <TTree.h>
#include <TH1.h>

#include <iostream>

#include "xsec.h"
#include "binnings.h"

using namespace std;

void makehisto(TString varname, TString process, TString ofile, TString file, TString dir, TString syst)
{
	TFile *fo = new TFile("histos/input/"+ofile+"__"+syst+".root","RECREATE");
	TFile *f = new TFile("trees_8TeV/"+dir+"/"+file+".root");

	TTree *tree = (TTree*)f->Get("trees/Events");

	cout << "Filling histogram " << varname << "__" << process << "__" << syst << " with " << file << endl;

	fo->cd();

	Float_t lumi = 19739;

	// weights
	Float_t weight = 1.0;
	Float_t pu_weight = 1.0;
	Float_t btag_weight = 1.0;
	Float_t muonID_weight = 1.0;
	Float_t muonIso_weight = 1.0;
	Float_t muonTrigger_weight = 1.0;
	tree->SetBranchAddress("pu_weight", &pu_weight);
	tree->SetBranchAddress("b_weight_nominal", &btag_weight);
	tree->SetBranchAddress("muon_IDWeight", &muonID_weight);
	tree->SetBranchAddress("muon_IsoWeight", &muonIso_weight);
	tree->SetBranchAddress("muon_TriggerWeight", &muonTrigger_weight);
	// cut variables
	Float_t muonIso = 0;
	Float_t jetrms = 0;
	Float_t mtw = 0;
	tree->SetBranchAddress("mu_iso", &muonIso);
	tree->SetBranchAddress("rms_lj", &jetrms);
	tree->SetBranchAddress("mt_mu", &mtw);
	//
	Int_t wjets_class = -1;
	tree->SetBranchAddress("wjets_classification", &wjets_class);

	Float_t var = 0;
	tree->SetBranchAddress(varname, &var);
	
	TH1::SetDefaultSumw2(true);
	TH1I *hcount = (TH1I*)f->Get("trees/count_hist");
	Int_t count = hcount->GetBinContent(1); 
	cout << count << endl;

	//cout << "sample size: " << count << endl;
	Float_t xsec = get_xsec(file);
	cout << "xsec: " << xsec << endl;
	
	TH1F *histo = new TH1F(varname+"__"+process+"__"+syst,varname+"__"+process+"__"+syst,bin_y,list_y);
	histo->Sumw2();
	
	Long_t nentries = tree->GetEntries();
	for(Long_t i = 0; i < nentries; i++) {
		tree->GetEntry(i);

		// wjets
		if(process == "wjets_light") {
			if(wjets_class == 0 || wjets_class == 1) continue;
		} else if (process == "wjets_heavy") {
			if(wjets_class != 0 && wjets_class != 1) continue;
		}
		
		if(jetrms >= 0.025) continue;
		if(mtw <= 50) continue;
		if(process == "qcd") {
			if (muonIso < 0.3 || muonIso > 0.5) continue;
		}
		
		if(process != "DATA"  && process != "qcd") {
			weight = pu_weight*btag_weight*muonID_weight*muonIso_weight*muonTrigger_weight;
			weight *= lumi;
			weight *= xsec;
			weight /= (Float_t)count;
		}
		
		histo->Fill(var,weight);
	}
	if(process == "qcd") histo->Scale(xsec);


	cout << "integral: " << histo->Integral() << endl;
	// write histos
	histo->Write();
	fo->Close();
}

int main()
{

	map<TString, TString> systematics;

	systematics["ResUp"] = "res__up";
	systematics["ResDown"] = "res__down";
	systematics["EnUp"] = "en__up";
	systematics["EnDown"] = "en__down";
	systematics["UnclusteredEnUp"] = "unclusen__up";
	systematics["UnclusteredEnDown"] = "unclusen__down";

	for(map<TString, TString>::iterator it = systematics.begin(); it != systematics.end(); it++) {
		// varname histoname outfile inputfile dir syst
		makehisto("cos_theta","tchan","tchan_t","T_t_ToLeptons",it->first,it->second);
		makehisto("cos_theta","tchan","tchan_tbar","Tbar_t_ToLeptons",it->first,it->second);
		makehisto("cos_theta","top","schan_t","T_s",it->first,it->second);
		makehisto("cos_theta","top","schan_tbar","Tbar_s",it->first,it->second);
		makehisto("cos_theta","top","twchan_t","T_tW",it->first,it->second);
		makehisto("cos_theta","top","twchan_tbar","Tbar_tW",it->first,it->second);
		makehisto("cos_theta","top","ttbar_semilept","TTJets_SemiLept",it->first,it->second);
		makehisto("cos_theta","top","ttbar_fulllept","TTJets_FullLept",it->first,it->second);
		makehisto("cos_theta","wzjets","wjets1","W1Jets_exclusive",it->first,it->second);
		makehisto("cos_theta","wzjets","wjets2","W2Jets_exclusive",it->first,it->second);
		makehisto("cos_theta","wzjets","wjets3","W3Jets_exclusive",it->first,it->second);
		makehisto("cos_theta","wzjets","wjets4","W4Jets_exclusive",it->first,it->second);
		makehisto("cos_theta","wzjets","zjets","DYJets",it->first,it->second);
		makehisto("cos_theta","wzjets","ww","WW",it->first,it->second);
		makehisto("cos_theta","wzjets","wz","WZ",it->first,it->second);
		makehisto("cos_theta","wzjets","zz","ZZ",it->first,it->second);
	}
	
	/*
	for(map<TString, TString>::iterator it = systematics.begin(); it != systematics.end(); it++) {
		// varname histoname outfile inputfile dir syst
		makehisto("cos_theta","tchan","tchan_t","T_t_ToLeptons",it->first,it->second);
		makehisto("cos_theta","tchan","tchan_tbar","Tbar_t_ToLeptons",it->first,it->second);
		makehisto("cos_theta","schan","schan_t","T_s",it->first,it->second);
		makehisto("cos_theta","schan","schan_tbar","Tbar_s",it->first,it->second);
		makehisto("cos_theta","twchan","twchan_t","T_tW",it->first,it->second);
		makehisto("cos_theta","twchan","twchan_tbar","Tbar_tW",it->first,it->second);
		makehisto("cos_theta","ttbar","ttbar_semilept","TTJets_SemiLept",it->first,it->second);
		makehisto("cos_theta","ttbar","ttbar_fulllept","TTJets_FullLept",it->first,it->second);
		makehisto("cos_theta","wjets","wjets1","W1Jets_exclusive",it->first,it->second);
		makehisto("cos_theta","wjets","wjets2","W2Jets_exclusive",it->first,it->second);
		makehisto("cos_theta","wjets","wjets3","W3Jets_exclusive",it->first,it->second);
		makehisto("cos_theta","wjets","wjets4","W4Jets_exclusive",it->first,it->second);
		makehisto("cos_theta","zjets","zjets","DYJets",it->first,it->second);
		makehisto("cos_theta","diboson","ww","WW",it->first,it->second);
		makehisto("cos_theta","diboson","wz","WZ",it->first,it->second);
		makehisto("cos_theta","diboson","zz","ZZ",it->first,it->second);
	}
	*/

	
	// t-channel scale
	makehisto("cos_theta","tchan","tchan_t","TToLeptons_t-channel_scaleup","08_07_2013/mu/iso/SYST","tchan_scale__up");
	makehisto("cos_theta","tchan","tchan_t","TToLeptons_t-channel_scaledown","08_07_2013/mu/iso/SYST","tchan_scale__down");
	
	makehisto("cos_theta","tchan","tchan_tbar","Tbar_t_scaleup","08_07_2013/mu/iso/SYST","tchan_scale__up");
	makehisto("cos_theta","tchan","tchan_tbar","Tbar_t_scaledown","08_07_2013/mu/iso/SYST","tchan_scale__down");
	
	// t-channel mass
	makehisto("cos_theta","tchan","tchan_t","TToLeptons_t-channel_scaleup","08_07_2013/mu/iso/SYST","mass__up");
	makehisto("cos_theta","tchan","tchan_t","TToLeptons_t-channel_mass178_5","08_07_2013/mu/iso/SYST","mass__down");
	makehisto("cos_theta","tchan","tchan_tbar","Tbar_t_mass178_5","08_07_2013/mu/iso/SYST","mass__up");
	makehisto("cos_theta","tchan","tchan_tbar","Tbar_t_mass166_5","08_07_2013/mu/iso/SYST","mass__down");

	/*
	// ttbar scale
	makehisto("cos_theta","ttbar","ttbar","TTJets_scaleup","08_07_2013/mu/iso/SYST","scale__up");
	makehisto("cos_theta","ttbar","ttbar","TTJets_scaledown","08_07_2013/mu/iso/SYST","scale__down");
	
	// ttbar matching
	makehisto("cos_theta","ttbar","ttbar","TTJets_matchingup","08_07_2013/mu/iso/SYST","matching__up");
	makehisto("cos_theta","ttbar","ttbar","TTJets_matchingdown","08_07_2013/mu/iso/SYST","matching__down");

	// ttbar mass
	makehisto("cos_theta","ttbar","ttbar","TTJets_mass178_5","08_07_2013/mu/iso/SYST","mass__up");
	makehisto("cos_theta","ttbar","ttbar","TTJets_mass166_5","08_07_2013/mu/iso/SYST","mass__down");
	*/
	
	// ttbar scale
	makehisto("cos_theta","top","ttbar","TTJets_scaleup","08_07_2013/mu/iso/SYST","top_scale__up");
	makehisto("cos_theta","top","ttbar","TTJets_scaledown","08_07_2013/mu/iso/SYST","top_scale__down");
	
	// ttbar matching
	makehisto("cos_theta","top","ttbar","TTJets_matchingup","08_07_2013/mu/iso/SYST","matching__up");
	makehisto("cos_theta","top","ttbar","TTJets_matchingdown","08_07_2013/mu/iso/SYST","matching__down");

	// ttbar mass
	makehisto("cos_theta","top","ttbar","TTJets_mass178_5","08_07_2013/mu/iso/SYST","mass__up");
	makehisto("cos_theta","top","ttbar","TTJets_mass166_5","08_07_2013/mu/iso/SYST","mass__down");

}
