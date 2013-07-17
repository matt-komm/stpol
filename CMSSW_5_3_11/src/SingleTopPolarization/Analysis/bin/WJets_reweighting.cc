#include <TTree.h>
#include <TFile.h>
#include <TSystem.h>
#include <TObject.h>
#include <iostream>
#include <stdlib.h>
#include <TH1F.h>
#include <TH1.h>
#include <map>

//TFile global("global.root", "RECREATE");

enum WJetsClassification {
    //W+heavy
    Wbb,
    Wcc,
    WbX,
    WcX,

    //W+light
    WgX,
    Wgg,
    WXX,
};

enum WJetsClassification1 {
    WJETS1_W_heavy,
    WJETS1_W_light,
};

int classify_1(int cls) {
    if (cls == Wbb || cls==Wcc || cls==WbX || cls==WcX) {
        return WJETS1_W_heavy;
    }
    else {
        return WJETS1_W_light;
    }
}

std::string classify_1_str(int cls) {
    if(cls==WJETS1_W_heavy)
        return std::string("W_heavy");
    else if(WJETS1_W_light)
        return std::string("W_light");
    else
        throw 1;
}

static const float Wlight_sf = 1.07267761;
void weight_1(int cls, float cos_theta, std::map<int, TH1F*>& hists, float& w, float& w_up, float& w_down) {
    w = 1.0;
    w_up = 1.0;
    w_down = 1.0;
    int cls_simple = classify_1(cls);

    TH1F* h = hists[cls_simple];
    int bin = h->FindBin(cos_theta);
    
    std::cout << "cos_theta=" << cos_theta << " Bin=" << bin << " cls=" << cls << " cls_1=" << cls_simple << " w=" << h->GetBinContent(bin) << std::endl;
    if (cls_simple==WJETS1_W_heavy) { //W+heavy
        w *= 1.0;
        w_up *= 2.0;
        w_down *= 0.5;
    }
    else if (cls_simple == WJETS1_W_light) { //W+light

        //madgraph W+light, measured in 2J data/madgraph
        w *= Wlight_sf;
        w_up *= Wlight_sf+(Wlight_sf-1.0);
        w_down *= Wlight_sf-(Wlight_sf-1.0);
    }
    else 
        throw 1;

    //Measured shape differences sherpa vs madgraph
    w *= h->GetBinContent(bin);
    w_up *= (h->GetBinContent(bin) + h->GetBinError(bin));
    w_down *= (h->GetBinContent(bin) - h->GetBinError(bin));
    std::cout << "w=" << w << std::endl;

}

WJetsClassification classify(int flavour_a, int flavour_b) {
    int a = abs(flavour_a);
    int b = abs(flavour_b);
    if (a==5 && b==5) {
       return Wbb;
    }
    else if (a==21 && b==21) {
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

TH1F* get_ratio_hist_1(TFile* fi, int cls) {


    const std::string mg("WJets/madgraph/");
    const std::string sh("WJets/sherpa/");
    const std::string flavour(classify_1_str(cls));

    TH1F* h_mg = (TH1F*)fi->Get((mg+flavour).c_str());
    TH1F* h_sh = (TH1F*)fi->Get((sh+flavour).c_str());
    //global.cd();
    std::string ratio_name(std::string("ratio__") + flavour);
    fi->Delete((ratio_name + std::string(";*")).c_str());
    TH1F* ratio = (TH1F*)h_sh->Clone(ratio_name.c_str());
    ratio->Divide(h_mg);
    ratio->Write();
    //fi->Close();
    return ratio;

}

int main(int argc, char* argv[]) {

    if(argc!=2) {
        std::cout << "Usage: " << argv[0] << " /path/to/input/file.root" << std::endl;
        exit(1);
    }
    const std::string infile(argv[1]);
    std::cout << "Input file is " << infile << std::endl;

    std::map<int, float> weights;
    weights[Wgg] = 1.422222; //error=0.101451

    weights[Wcc] = 0.165217; //error=0.063260
    weights[WbX] = 0.063391; //error=0.014114
    weights[WgX] = 1.289320; //error=0.044974
    weights[WcX] = 0.574324; //error=0.045911
    weights[WXX] = 1.040555; //error=0.025275

    weights[Wcc] *= 2;
    weights[WbX] *= 2;
    weights[WcX] *= 2;

    TFile* fi = new TFile(infile.c_str(), "UPDATE");
    fi->cd("trees");
    TTree* events = (TTree*)fi->Get("trees/Events");
    TTree* weight_tree = new TTree("WJets_weights", "WJets_weights");

    TFile* hists_fi = new TFile("$STPOL_DIR/CMSSW_5_3_11/src/data/WJets_reweighting/hists__costheta_flavours_merged.root", "UPDATE");
    std::map<int, TH1F*> ratio_hists;
    ratio_hists[WJETS1_W_heavy] = get_ratio_hist_1(hists_fi, WJETS1_W_heavy);
    ratio_hists[WJETS1_W_light] = get_ratio_hist_1(hists_fi, WJETS1_W_light);

    ratio_hists[WJETS1_W_heavy]->Print("ALL");
    ratio_hists[WJETS1_W_light]->Print("ALL");

    int gen_flavour_bj = -1;
    int gen_flavour_lj = -1;
    float cos_theta = 0.0;
    
    events->SetBranchStatus("*", 0);
    events->SetBranchStatus("gen_flavour_bj", 1);
    events->SetBranchStatus("gen_flavour_lj", 1);
    events->SetBranchStatus("cos_theta", 1);
    events->SetBranchAddress("gen_flavour_bj", &gen_flavour_bj);
    events->SetBranchAddress("gen_flavour_lj", &gen_flavour_lj);
    events->SetBranchAddress("cos_theta", &cos_theta);
    
    //float wjets_flavour_weight = 1.0;
    int cls = -1;

    float weight=1.0, weight_up=1.0, weight_down = 1.0;
    TBranch* weight_branch = weight_tree->Branch("wjets_mg_flavour_weight", &weight, "wjets_mg_flavour_weight/F"); 
    //events->SetBranchStatus("wjets_mg_flavour_weight", 1);
    TBranch* weight_branch_up = weight_tree->Branch("wjets_mg_flavour_weight_up", &weight_up, "wjets_mg_flavour_weight_up/F"); 
    //events->SetBranchStatus("wjets_mg_flavour_weight_up", 1);
    TBranch* weight_branch_down = weight_tree->Branch("wjets_mg_flavour_weight_down", &weight_down, "wjets_mg_flavour_weight_down/F"); 
    //events->SetBranchStatus("wjets_mg_flavour_weight_down", 1);
    
    TBranch* cls_branch = weight_tree->Branch("wjets_flavour_classification", &cls, "wjets_flavour_classification/I"); 
    //events->SetBranchStatus("wjets_flavour_classification", 1);
    
    int Nbytes = 0;

    std::cout << "Beginning event loop over " << events->GetEntries() << " events." << std::endl;
     for (int n=0; n<events->GetEntries(); n++) {
        events->GetEntry(n);
        weight=1.0;
        weight_up=1.0;
        weight_down = 1.0;
        cls = classify(gen_flavour_bj, gen_flavour_lj);
        //wjets_flavour_weight = weights[cls];
        weight_1(cls, cos_theta, ratio_hists, weight, weight_up, weight_down);
        int nbytes = weight_tree->Fill();
        if (nbytes<0) {
            std::cerr << "Write error!" << std::endl;
            exit(1);
        }
        Nbytes += nbytes;
    }
    events->SetBranchStatus("*", 1);
    fi->cd("trees");

    /*TList* list = events->GetListOfFriends();
    for(int i=0;i<list->GetEntries(); i++) {
        events->RemoveFriend((TTree*)list->At(i));
    }*/

    weight_tree->Write("", TObject::kOverwrite);
    events->Write("", TObject::kOverwrite);
    fi->Close();
    std::cout << "Wrote " << Nbytes << " bytes" << std::endl;

    hists_fi->Close();
    //global.Close();
    return 0;
}
