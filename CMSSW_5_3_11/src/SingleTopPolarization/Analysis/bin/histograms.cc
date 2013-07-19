#include <TTree.h>
#include <TEventList.h>
#include <TFile.h>
#include <TSystem.h>
#include <TObject.h>
#include <iostream>
#include <sstream>
#include <TH1F.h>
#include <string>
#include <stdlib.h>
#include <vector>
#include <map>
#include <memory>
#include <tr1/tuple> 

template <typename T>
void get_branch(const char* name, T* address, TTree* tree) {
    tree->SetBranchStatus(name, 1);
    tree->SetBranchAddress(name, address);
    tree->AddBranchToCache(name);
}

static const std::string sep("__");
std::string hist_name(int n_jets, int n_tags) {
    std::ostringstream ss;
    ss << sep << "NJets_" << n_jets;
    ss << sep << "NTags_" << n_tags;
    return ss.str();
}

int main(int argc, char* argv[]) {

    if(argc!=2) {
        std::cout << "Usage: " << argv[0] << " /path/to/input/file.root" << std::endl;
        exit(1);
    }

    std::vector<int> N_jets;
    N_jets.push_back(2);
    N_jets.push_back(3);
    std::vector<int> N_tags;
    N_tags.push_back(0);
    N_tags.push_back(1);
    N_tags.push_back(2);

    const std::string infile(argv[1]);
    const std::string fname = infile.substr(infile.rfind("/")+1, infile.find(".root") - infile.rfind("/"));
    std::cout << "Input file is " << infile << std::endl;

    TFile* fi = new TFile(infile.c_str());
    TTree* events = (TTree*)fi->Get("trees/Events");
    events->SetCacheSize(10000000);
    
    events->SetBranchStatus("*", 0);
    events->SetBranchStatus("n_muons", 1);
    events->SetBranchStatus("n_eles", 1);
    events->SetBranchStatus("n_veto_mu", 1);
    events->SetBranchStatus("n_veto_ele", 1);
    events->SetBranchStatus("n_jets", 1);
    events->SetBranchStatus("top_mass", 1);
    events->SetBranchStatus("eta_lj", 1);
    events->SetBranchStatus("rms_lj", 1);
    events->SetBranchStatus("mt_mu", 1);

    events->AddBranchToCache("n_muons");
    events->AddBranchToCache("n_eles");
    events->AddBranchToCache("n_veto_mu");
    events->AddBranchToCache("n_veto_ele");
    events->AddBranchToCache("n_jets");
    events->AddBranchToCache("top_mass");
    events->AddBranchToCache("eta_lj");
    events->AddBranchToCache("rms_lj");
    events->AddBranchToCache("mt_mu");

    TFile* ofi = new TFile("out.root", "UPDATE");
    ofi->cd();

    std::cout << "Performing preselection" << std::endl;

    const std::string elist_name = std::string("elist__") + fname;

    std::cout << "Looking for event list with name " << elist_name << std::endl;
    TObject* elist_ = ofi->Get(elist_name.c_str());
    std::cout << "elist_=" << elist_ << std::endl;
    TEventList* elist = (TEventList*)elist_;
    
    int Nentries = -1;
    if (elist==0) {
        Nentries = events->Draw((std::string(">>") + elist_name).c_str(), "n_muons==1 && n_eles==0 && n_veto_mu==0 && n_jets>0 && n_veto_ele==0 && rms_lj<0.025 && abs(eta_lj)>2.5 && top_mass<220 && top_mass>130 && mt_mu>50");
        elist = (TEventList*)ofi->Get(elist_name.c_str());
        std::cout << Nentries << " events selected with preselection" << std::endl;
        elist->Write();
    }
    Nentries = elist->GetN();

    events->SetBranchStatus("*", 0);
    events->SetEventList(elist);

    int n_jets = -1;
    get_branch<int>("n_jets", &n_jets, events);
    int n_tags = -1;
    get_branch<int>("n_tags", &n_tags, events); 
    //int wjets_flavour_classification = -1;
    //get_branch<int>("wjets_flavour_classification", &wjets_flavour_classification, events); 
    float cos_theta = -1;
    get_branch<float>("cos_theta", &cos_theta, events);

    typedef std::tr1::tuple<int, int, const char*> hist_ident;
    std::map<hist_ident, TH1*> hists;
    hists[std::tr1::make_tuple(2, 1, "cos_theta")] = new TH1F("cos_theta_2_1", "cos_theta", 20, -1, 1);
    hists[std::tr1::make_tuple(2, 0, "cos_theta")] = new TH1F("cos_theta_2_0", "cos_theta", 20, -1, 1);

    //cos_theta_hists[]
    long Nbytes = 0;
    for (int n=0; n<Nentries; n++) {
        long idx = elist->GetEntry(n);
        Nbytes += events->GetEntry(idx);
        if (n_jets==2 && n_tags==1)
            hists[std::tr1::make_tuple(2,1, "cos_theta")]->Fill(cos_theta);
        if (n_jets==2 && n_tags==0)
            hists[std::tr1::make_tuple(2,0, "cos_theta")]->Fill(cos_theta);

    }
    std::cout << "Read " << Nbytes << " bytes" << std::endl;

    for (auto& e : hists) {
        e.second->Print("ALL");
        //ofi->Delete((std::string(e.second->GetName()) + std::string(";")).c_str());

        e.second->Write("", TObject::kOverwrite);
    }
    
    fi->Close();
    ofi->Close();
    
    //std::cout << "Wrote " << Nbytes << " bytes" << std::endl;
    return 0;
}
