#include <TTree.h>
#include <TFile.h>
#include <TSystem.h>
#include <TObject.h>
#include <iostream>
#include <stdlib.h>
#include <map>

enum WJetsClassification {
   // Wbb,
    Wgg,
    Wcc,
    WbX,
    WgX,
    WcX,
    WXX,
};


WJetsClassification classify(int flavour_a, int flavour_b) {
    int a = abs(flavour_a);
    int b = abs(flavour_b);
    //if (a==5 && b==5) {
    //    return Wbb;
    //}
    if (a==21 && b==21) {
        return Wgg;
    }
    else if (a==4 && b==4) {
        return Wcc;
    }
    else if (a==5 || b==5) {
        return WbX;
    }
    else if (a==21 || b==21) {
        return WgX;
    }
    else if (a==4 || b==4) {
        return WcX;
    }
    else {
        return WXX;
    }
}

int main() {
    std::map<int, float> weights;
    weights[Wgg] = 1.422222; //error=0.101451
    weights[Wcc] = 0.165217; //error=0.063260
    weights[WbX] = 0.063391; //error=0.014114
    weights[WgX] = 1.289320; //error=0.044974
    weights[WcX] = 0.574324; //error=0.045911
    weights[WXX] = 1.040555; //error=0.025275

    TFile* fi = new TFile("out.root", "UPDATE");
    TTree* events = (TTree*)fi->Get("trees/Events");

    int gen_flavour_bj = -1;
    int gen_flavour_lj = -1;
    
    events->SetBranchStatus("*", 0);
    events->SetBranchStatus("gen_flavour_bj", 1);
    events->SetBranchStatus("gen_flavour_lj", 1);
    events->SetBranchAddress("gen_flavour_bj", &gen_flavour_bj);
    events->SetBranchAddress("gen_flavour_lj", &gen_flavour_lj);
    
    float wjets_flavour_weight = 1.0;
    int cls = -1;
    
    TBranch* weight_branch = events->Branch("wjets_flavour_weight", &wjets_flavour_weight, "wjets_flavour_weight/F"); 
    events->SetBranchStatus("wjets_flavour_weight", 1);
    
    TBranch* cls_branch = events->Branch("wjets_flavour_classification", &cls, "wjets_flavour_classification/I"); 
    events->SetBranchStatus("wjets_flavour_classification", 1);
    
    int Nbytes = 0;
    for (int n=0; n<events->GetEntries(); n++) {
        events->GetEntry(n);
        cls = classify(gen_flavour_bj, gen_flavour_lj);
        wjets_flavour_weight = weights[cls];
        int nbytes = weight_branch->Fill();
        nbytes += cls_branch->Fill();
        if (nbytes<0) {
            std::cerr << "Write error!" << std::endl;
            exit(1);
        }
        Nbytes += nbytes;
    }
    events->SetBranchStatus("*", 1);
    fi->cd("trees");
    events->Write("", TObject::kOverwrite);
    fi->Close();
    std::cout << "Wrote " << Nbytes << " bytes" << std::endl;
    return 0;
}
