#include <TTree.h>
#include <TEventList.h>
#include <TFile.h>
#include <TSystem.h>
#include <TObject.h>
#include <iostream>
#include <TH1F.h>
#include <string>
#include <stdlib.h>
#include <map>

template <typename T>
void get_branch(const char* name, T* address, TTree* tree) {
    tree->SetBranchStatus(name, 1);
    tree->SetBranchAddress(name, address);
    tree->AddBranchToCache(name);
}

std::vector<int> N_jets;
N_jets.push_back(2);
N_jets.push_back(3);
std::vector<int> N_tags;
N_tags.push_back(0);
N_tags.push_back(1);
N_tags.push_back(2);
std::string hist_name(int n_jets, int n_tags) {
    std::istringstream ss;
    ss << "__NJets_" << n_jets;
    ss << "__NTags_" << n_tags;
    return ss.string();
}
int main(int argc, char* argv[]) {

    if(argc!=2) {
        std::cout << "Usage: " << argv[0] << " /path/to/input/file.root" << std::endl;
        exit(1);
    }
    const std::string infile(argv[1]);
    std::cout << "Input file is " << infile << std::endl;

    TFile* fi = new TFile(infile.c_str());
    TTree* events = (TTree*)fi->Get("trees/Events");
    events->SetCacheSize(10000000);
    
    int Nbytes = 0;
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

    int Nentries = events->Draw(">>elist", "n_muons==1 && n_eles==0 && n_veto_mu==0 && n_jets>0 && n_veto_ele==0 && rms_lj<0.025 && abs(eta_lj)>2.5 && top_mass<220 && top_mass>130 && mt_mu>50");
    TEventList* elist = (TEventList*)fi->Get("elist");
    std::cout << Nentries << " events selected with preselection" << std::endl;

    events->SetBranchStatus("*", 0);
    events->SetEventList(elist);

    int n_jets = -1;
    get_branch<int>("n_jets", &n_jets, events);
    int n_tags = -1;
    get_branch<int>("n_tags", &n_tags, events); 
    int wjets_flavour_classification = -1;
    get_branch<int>("wjets_flavour_classification", &wjets_flavour_classification, events); 
    float cos_theta = -1;
    get_branch<float>("cos_theta", &cos_theta, events);

    std::map<std::string, std::map<std::string, TH1F*>> hists;
    std::string sample_name("WJets");

    for (int& n : N_jets) {
        for (int& m : N_tags) {
            std::string hname(hist_name(n, m));
            hists[hname][sample_name] = new TH1F(sample_name.c_str(), sample_name.c_str(), 20, -1, 1);
        }
    }

    //cos_theta_hists[]
    for (int n=0; n<Nentries; n++) {
        long idx = elist->GetEntry(n);
        events->GetEntry(idx);

        for (int& n : N_jets) {
            for (int& m : N_tags) {
                if (n_jets==n && n_tags == m) {

                }
            }
        }

    }
    
    fi->Close();
    
    //std::cout << "Wrote " << Nbytes << " bytes" << std::endl;
    return 0;
}
