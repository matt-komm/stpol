#include <TFile.h>
#include <TTree.h>
#include <TH1.h>

#include <iostream>

#include "info.h"
#include "xsec.h"
#include "binnings.h"

using namespace std;

void makehisto(TString varname, TString process, TString ofile, TString file, TString datapath="")
{
	TFile *fo = new TFile("histos/input/"+ofile+".root","RECREATE");
	//TFile *f = new TFile("trees_8TeV/Nominal/"+file+".root");
	TFile *f = new TFile("trees_8TeV/mu/mc/iso/nominal/Jul15/"+file+".root");

	// FIXME
	TTree *tree = (TTree*)f->Get("trees/Events");
	//TTree *tree = (TTree*)f->Get("trees/Events_selected");

	cout << "Filling histogram " << varname << "__" << process << endl;

	fo->cd();

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
	Float_t eta_lj = 0;
	Float_t muonIso = 0;
	Float_t jetrms = 0;
	Float_t mtw = 0;
	tree->SetBranchAddress("mu_iso", &muonIso);
	tree->SetBranchAddress("rms_lj", &jetrms);
	tree->SetBranchAddress("mt_mu", &mtw);
	tree->SetBranchAddress("eta_lj", &eta_lj);


        Int_t HLT_v11 = 0;
        Int_t HLT_v12 = 0;
        Int_t HLT_v13 = 0;
        Int_t HLT_v14 = 0;
        Int_t HLT_v15 = 0;
        Int_t HLT_v16 = 0;
        Int_t HLT_v17 = 0;

        tree->SetBranchAddress("HLT_IsoMu24_eta2p1_v11", &HLT_v11);
        tree->SetBranchAddress("HLT_IsoMu24_eta2p1_v12", &HLT_v12);
        tree->SetBranchAddress("HLT_IsoMu24_eta2p1_v13", &HLT_v13);
        tree->SetBranchAddress("HLT_IsoMu24_eta2p1_v14", &HLT_v14);
        tree->SetBranchAddress("HLT_IsoMu24_eta2p1_v15", &HLT_v15);
        tree->SetBranchAddress("HLT_IsoMu24_eta2p1_v16", &HLT_v16);
        tree->SetBranchAddress("HLT_IsoMu24_eta2p1_v17", &HLT_v17);

        Int_t n_jets = 0;
        Int_t n_tags = 0;
        Int_t n_veto_ele = -1;
        Int_t n_veto_mu = -1;
        Float_t pt_lj = 0;
        Float_t pt_bj = 0;
        Float_t top_mass = 0;
        tree->SetBranchAddress("n_jets", &n_jets);
        tree->SetBranchAddress("n_tags", &n_tags);
        tree->SetBranchAddress("n_veto_ele", &n_veto_ele);
        tree->SetBranchAddress("n_veto_mu", &n_veto_mu);
        tree->SetBranchAddress("pt_lj", &pt_lj);
        tree->SetBranchAddress("pt_bj", &pt_bj);
        tree->SetBranchAddress("top_mass", &top_mass);


	Float_t var = 0;
	tree->SetBranchAddress(varname, &var);

	Float_t var_gen = 0;
	// FIXME
	if(process == "tchan") {
		tree->SetBranchAddress(var_x, &var_gen);
	}
	
	TH1::SetDefaultSumw2(true);
	TH1I *hcount = (TH1I*)f->Get("trees/count_hist");
	Int_t count = hcount->GetBinContent(1); 

	//cout << "sample size: " << count << endl;
	Float_t xsec = get_xsec(file);
	cout << "xsec: " << xsec << endl;
	
	TH1F *histo = new TH1F(varname+"__"+process,varname+"__"+process,bin_y,list_y);
	histo->Sumw2();
	
	Long_t nentries = tree->GetEntries();
	for(Long_t i = 0; i < nentries; i++) {
		tree->GetEntry(i);

		if(TMath::Abs(eta_lj) < 2.5) continue;

		if(jetrms >= 0.025) continue;
		if(mtw <= 50) continue;

                if(!(HLT_v11 == 1 || HLT_v12 == 1 || HLT_v13 == 1 || HLT_v14 == 1 || HLT_v15 == 1 || HLT_v16 == 1 || HLT_v17==1)) continue;
                if(n_jets != 2) continue;
                if(n_tags != 1) continue;
                if(n_veto_ele != 0) continue;
                if(n_veto_mu != 0) continue;
                if(pt_lj <= 40) continue;
                if(pt_bj <= 40) continue;
                if(top_mass <= 130 || top_mass >= 220) continue;

		if(process == "qcd") {
			if (muonIso < 0.3 || muonIso > 0.5) continue;
		} 
		
		if(process != "DATA"  && process != "qcd") {
			weight = pu_weight*btag_weight*muonID_weight*muonIso_weight*muonTrigger_weight;
			weight *= lumi;
			weight *= xsec;
			weight /= (Float_t)count;
		}

		// FIXME reweight costheta
		/*
		if(process == "tchan") {
			weight *= (0.25*var_gen+0.5)/(0.440209*var_gen+0.5);
		}
		*/
		
		histo->Fill(var,weight);
	}
	cout << "integral: " << histo->Integral() << endl;

	// write histos
	histo->Write();
	fo->Close();
}

int main()
{
	// varname histoname outfile inputfile
	//makehisto("cos_theta","tchan","tchan_t","T_t");
	//makehisto("cos_theta","tchan","tchan_tbar","Tbar_t");
	/*
	makehisto("cos_theta","tchan","tchan_t","T_t_ToLeptons");
	makehisto("cos_theta","tchan","tchan_tbar","Tbar_t_ToLeptons");
	makehisto("cos_theta","schan","schan_t","T_s");
	makehisto("cos_theta","schan","schan_tbar","Tbar_s");
	makehisto("cos_theta","twchan","twchan_t","T_tW");
	makehisto("cos_theta","twchan","twchan_tbar","Tbar_tW");
	makehisto("cos_theta","ttbar","ttbar_semilept","TTJets_SemiLept");
	makehisto("cos_theta","ttbar","ttbar_fulllept","TTJets_FullLept");
	makehisto("cos_theta","wjets","wjets1","W1Jets_exclusive");
	makehisto("cos_theta","wjets","wjets2","W2Jets_exclusive");
	makehisto("cos_theta","wjets","wjets3","W3Jets_exclusive");
	makehisto("cos_theta","wjets","wjets4","W4Jets_exclusive");
	makehisto("cos_theta","zjets","zjets","DYJets");
	makehisto("cos_theta","diboson","ww","WW");
	makehisto("cos_theta","diboson","wz","WZ");
	makehisto("cos_theta","diboson","zz","ZZ");
	//makehisto("cos_theta","qcd","qcd","QCDMu");
	makehisto("cos_theta","qcd","qcd","QCDShape");
	makehisto("cos_theta","DATA","DATA_SingleMu","SingleMu");
	*/
	
//	makehisto("cos_theta","tchan","tchan_comphep","../08_07_2013/mu/iso/SYST/TToBMuNu_comphep_t-channel");
//	makehisto("cos_theta","tchan","tchan_comphep_anom","../08_07_2013/mu/iso/SYST/TToBMuNu_anomWtb-0100_t-channel");
//	makehisto("cos_theta","tchan","tchan_comphep_unphys","../08_07_2013/mu/iso/SYST/TToBMuNu_anomWtb-unphys_t-channel");

	// merged processes
	makehisto("cos_theta","tchan","tchan_t","T_t_ToLeptons");
	makehisto("cos_theta","tchan","tchan_tbar","Tbar_t_ToLeptons");
	makehisto("cos_theta","top","schan_t","T_s");
	makehisto("cos_theta","top","schan_tbar","Tbar_s");
	makehisto("cos_theta","top","twchan_t","T_tW");
	makehisto("cos_theta","top","twchan_tbar","Tbar_tW");
	makehisto("cos_theta","top","ttbar_semilept","TTJets_SemiLept");
	makehisto("cos_theta","top","ttbar_fulllept","TTJets_FullLept");
	makehisto("cos_theta","wzjets","wjets1","W1Jets_exclusive");
	makehisto("cos_theta","wzjets","wjets2","W2Jets_exclusive");
	makehisto("cos_theta","wzjets","wjets3","W3Jets_exclusive");
	makehisto("cos_theta","wzjets","wjets4","W4Jets_exclusive");
	makehisto("cos_theta","wzjets","zjets","DYJets");
	makehisto("cos_theta","wzjets","ww","WW");
	makehisto("cos_theta","wzjets","wz","WZ");
	makehisto("cos_theta","wzjets","zz","ZZ");
	makehisto("cos_theta","qcd","qcd","QCDShape");
	makehisto("cos_theta","DATA","DATA_SingleMu","SingleMu");
}
