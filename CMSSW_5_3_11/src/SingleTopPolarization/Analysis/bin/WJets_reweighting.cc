#include <TTree.h>
#include <TFile.h>
#include <TSystem.h>
#include <TObject.h>
#include <iostream>
#include <stdlib.h>
#include <TH1F.h>
#include <TH1.h>
#include <TRandom.h>

#include <map>
#include <cmath>

#include "jet_flavour_classifications.h"

#define QUADSUM(x,y) sqrt(pow(x,2)+pow(y,2))

using namespace std;

WJetsClassification1 classify_1(WJetsClassification0 cls) {
    if (cls == Wbb || cls==Wcc || cls==WbX || cls==WcX || cls==Wbc) {
        return WJETS1_W_heavy;
    }
    else {
        return WJETS1_W_light;
    }
}

WJetsClassification2 classify_2(WJetsClassification0 cls) {
    if (cls == Wbb || cls==Wcc || cls==Wbc) {
        return WJETS2_W_QQ;
    }
    else if(cls == WcX || cls==WbX) {
        return WJETS2_W_Qq;
    } else {
        return WJETS2_W_qq;
    }
}

TRandom* rng = 0;

static const float Wlight_sf = 1.0991871445834183;
void weight(
    WJetsClassification0 cls, float cos_theta, TH1F* hist,
    float& w_flat, float& w_flat_up, float& w_flat_down,
    float& w_shape, float& w_shape_up, float& w_shape_down) {
    w_flat = 1.0;
    w_flat_up = 1.0;
    w_flat_down = 1.0;

    w_shape = 1.0;
    w_shape_up = 1.0;
    w_shape_down = 1.0;

    WJetsClassification1 cls_simple = classify_1(cls);

    int bin = hist->FindBin(cos_theta);
    
    if (cls_simple==WJETS1_W_heavy) { //W+heavy
        w_flat *= 1.0;
        w_flat_up *= 2.0;
        w_flat_down *= 0.5;
    }
    else if (cls_simple == WJETS1_W_light) { //W+light

        //madgraph W+light, measured in 2J data/madgraph
        w_flat *= Wlight_sf;
        w_flat_up *= Wlight_sf + fabs(Wlight_sf-1.0);
        w_flat_down *= Wlight_sf - fabs(Wlight_sf-1.0);
    }
    else 
        throw 1;

    //Measured shape differences sherpa vs madgraph
    float w = rng->Gaus(hist->GetBinContent(bin), hist->GetBinError(bin));
    //cout << hist->GetBinContent(bin) << ":" << hist->GetBinError(bin) << ":" << w << endl;
    float e = fabs(w - 1.0);//QUADSUM(fabs(w - 1.0), hist->GetBinError(bin));
    w_shape *= w;
    w_shape_up *= w + e;
    w_shape_down *= w - e;
    //std::cout << "w=" << w << std::endl;

}

WJetsClassification0 classify(int flavour_a, int flavour_b) {
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
    else if ((a==5 && b==4) || (a==4 && b==5)) {
        return Wbc;
    }
    else if (a==5 || b==5) {
        return WbX;
    }
    else if (a==4 || b==4) {
        return WcX;
    }
    else if (a==21 || b==21) {
        return WgX;
    }
    else {
        return WXX;
    }
}

int main(int argc, char* argv[]) {

    if(argc!=2) {
        std::cout << "Usage: " << argv[0] << " /path/to/input/file.root" << std::endl;
        exit(1);
    }
    const std::string infile(argv[1]);
    std::cout << "Input file is " << infile << std::endl;

    rng = new TRandom();
    rng->SetSeed();


/* For reweighting sherpa fractions to madgraph
    std::map<WJetsClassification0, float> weights;
    //weights[WJETS2_W_QQ] = 0.163661; //error=0.009857 [1]
    //weights[WJETS2_W_Qq] = 0.498646; //error=0.007892 [2]
    //weights[WJETS2_W_qq] = 1.244096; //error=0.012993 [3]

    weights[Wbb] = 0.309315; //error=0.044416 [1]
    weights[Wcc] = 0.225933; //error=0.017562 [2]
    weights[Wbc] = 0.047298; //error=0.006804 [3]
    weights[WbX] = 0.111583; //error=0.005099 [4]
    weights[WcX] = 0.645442; //error=0.011115 [5]
    weights[WgX] = 1.385702; //error=0.020337 [6]
    weights[Wgg] = 1.443654; //error=0.044480 [7]
    weights[WXX] = 1.011214; //error=0.017198 [8]

*/

    TFile* fi = new TFile(infile.c_str(), "UPDATE");
    fi->cd("trees");
    TTree* events = (TTree*)fi->Get("trees/Events");
    TTree* weight_tree = new TTree("WJets_weights", "WJets_weights");

    TFile* hists_fi0 = new TFile("$STPOL_DIR/CMSSW_5_3_11/src/data/WJets_reweighting/hists__costheta_flavours_merged_scenario0.root", "UPDATE");
    TFile* hists_fi2 = new TFile("$STPOL_DIR/CMSSW_5_3_11/src/data/WJets_reweighting/hists__costheta_flavours_merged_scenario2.root", "UPDATE");    

    std::map<WJetsClassification2, TH1F*> ratio_hists2;
    ratio_hists2[WJETS2_W_QQ] = (TH1F*)hists_fi2->Get("ratio__W_QQ");
    ratio_hists2[WJETS2_W_Qq] = (TH1F*)hists_fi2->Get("ratio__W_Qq");
    ratio_hists2[WJETS2_W_qq] = (TH1F*)hists_fi2->Get("ratio__W_qq");

    std::map<WJetsClassification0, TH1F*> ratio_hists0;
    ratio_hists0[Wbb] = (TH1F*)hists_fi0->Get("ratio__Wbb");
    ratio_hists0[Wcc] = (TH1F*)hists_fi0->Get("ratio__Wcc");
    ratio_hists0[Wbc] = (TH1F*)hists_fi0->Get("ratio__Wbc");
    ratio_hists0[WbX] = (TH1F*)hists_fi0->Get("ratio__WbX");
    ratio_hists0[WcX] = (TH1F*)hists_fi0->Get("ratio__WcX");
    ratio_hists0[WgX] = (TH1F*)hists_fi0->Get("ratio__WgX");
    ratio_hists0[Wgg] = (TH1F*)hists_fi0->Get("ratio__Wgg");
    ratio_hists0[WXX] = (TH1F*)hists_fi0->Get("ratio__WXX");

    int gen_flavour_bj = -1;
    int gen_flavour_lj = -1;
    int n_tags = -1;
    float cos_theta = 0.0;
    
    events->SetBranchStatus("*", 0);
    events->SetBranchStatus("gen_flavour_bj", 1);
    events->SetBranchStatus("gen_flavour_lj", 1);
    events->SetBranchStatus("cos_theta", 1);
    events->SetBranchAddress("gen_flavour_bj", &gen_flavour_bj);
    events->SetBranchAddress("gen_flavour_lj", &gen_flavour_lj);
    events->SetBranchAddress("cos_theta", &cos_theta);
    events->SetBranchAddress("n_tags", &n_tags);
    
    //float wjets_flavour_weight = 1.0;
    WJetsClassification0 cls0;
    WJetsClassification1 cls1;
    WJetsClassification2 cls2;

    std::map<const std::string, float> weights_flat;
    std::map<const std::string, float> weights_shape;
    
    weights_flat["nominal"] = 1.0;
    weights_flat["up"] = 1.0;
    weights_flat["down"] = 1.0;

    weights_shape["nominal"] = 1.0;
    weights_shape["up"] = 1.0;
    weights_shape["down"] = 1.0;

    std::map<const std::string, float> weights_mg_combined;
    weights_mg_combined["nominal"] = 1.0;
    weights_mg_combined["up"] = 1.0;
    weights_mg_combined["down"] = 1.0;

    std::map<const std::string, float> weight_sherpa;
    weight_sherpa["nominal"] = 1.0;
    weight_sherpa["up"] = 1.0;
    weight_sherpa["down"] = 1.0;

/*
    weight_tree->Branch("wjets_sh_flavour_flat_weight", &weight_sherpa["nominal"], "wjets_sh_flavour_flat_weight/F"); 
    weight_tree->Branch("wjets_sh_flavour_flat_weight_up", &weight_sherpa["up"], "wjets_sh_flavour_flat_weight/F"); 
    weight_tree->Branch("wjets_sh_flavour_flat_weight_down", &weight_sherpa["down"], "wjets_sh_flavour_flat_weight/F"); 
*/    
    weight_tree->Branch("wjets_mg_flavour_flat_weight", &weights_flat["nominal"], "wjets_mg_flavour_flat_weight/F"); 
    weight_tree->Branch("wjets_mg_flavour_flat_weight_up", &weights_flat["up"], "wjets_mg_flavour_flat_weight_up/F"); 
    weight_tree->Branch("wjets_mg_flavour_flat_weight_down", &weights_flat["down"], "wjets_mg_flavour_flat_weight_down/F"); 
    
    weight_tree->Branch("wjets_mg_flavour_shape_weight", & weights_shape["nominal"], "wjets_mg_flavour_shape_weight/F"); 
    weight_tree->Branch("wjets_mg_flavour_shape_weight_up", &weights_shape["up"], "wjets_mg_flavour_shape_weight_up/F"); 
    weight_tree->Branch("wjets_mg_flavour_shape_weight_down", &weights_shape["down"], "wjets_mg_flavour_shape_weight_down/F"); 
/*
    weight_tree->Branch("wjets_mg_flavour_weight_comb", &weights_mg_combined["nominal"], "wjets_mg_flavour_weight_comb/F"); 
    weight_tree->Branch("wjets_mg_flavour_weight_comb_up", &weights_mg_combined["up"], "wjets_mg_flavour_weight_comb_up/F"); 
    weight_tree->Branch("wjets_mg_flavour_weight_comb_down", &weights_mg_combined["down"], "wjets_mg_flavour_weight_comb_down/F"); 
*/

    weight_tree->Branch("wjets_flavour_classification0", &cls0, "wjets_flavour_classification0/I"); 
    weight_tree->Branch("wjets_flavour_classification1", &cls1, "wjets_flavour_classification1/I"); 
    weight_tree->Branch("wjets_flavour_classification2", &cls2, "wjets_flavour_classification2/I"); 
    
    int Nbytes = 0;

    vector <string> systematics;
    systematics.push_back("nominal");
    systematics.push_back("up");
    systematics.push_back("down");

    std::cout << "Beginning event loop over " << events->GetEntries() << " events." << std::endl;
     for (int n=0; n<events->GetEntries(); n++) {
        events->GetEntry(n);
        cls0 = classify(gen_flavour_bj, gen_flavour_lj);
        cls1 = classify_1(cls0);
        cls2 = classify_2(cls0);

        //weight_sherpa["nominal"] = weights[cls0];

        weight(cls0, cos_theta, ratio_hists0[cls0],
            weights_flat["nominal"], weights_flat["up"], weights_flat["down"],
            weights_shape["nominal"], weights_shape["up"], weights_shape["down"]
        );

/*
        for (auto& s : systematics)
            weights_mg_combined[s] = weights_flat[s] * weights_shape[s];
*/
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

    hists_fi0->Close();
    hists_fi2->Close();
    //global.Close();
    return 0;
}
