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

#include <boost/program_options.hpp>

using namespace std;

//Produces a binary classification to W+heavy or W+light, depending on whether there is a b or a c
WJetsClassification1 classify_1(WJetsClassification0 cls) {
    if (cls == Wbb || cls==Wcc || cls==WbX || cls==WcX || cls==Wbc) {
        return WJETS1_W_heavy;
    }
    else {
        return WJETS1_W_light;
    }
}

//Produces a ternary classification to 1) 2 x b/c-containing, 2) 1 x b/c-containing, 3) not containing a b/c 
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

//The random number generator used for weighting
TRandom* rng = 0;

//The W+light scale factor that is extracted from 2J0T (final selection), to match MC yield to data
static const float Wlight_sf = 1.0991871445834183;

//Produces the cos-theta dependent event weight and the corresponding up-down variations
// cls - The W+xy-type event classification (based on the two identified jets)
// hist - a pointer to the histogram with the look-up for the cos-theta dependent scale factor for the given classification
// w_flat(up/down) - the normalization scale factor applied on flavours irrespective of cos theta and the corresponding 1-sigma up/down variations
// w_shape(u/down) - the shape scale factor applied as depending on cos theta and the corresponding systematic variations
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
    //The scale factor is a random variable and in order to lessed the effect of the fluctuation, in low-statistics channels,
    //we randomly draw the per-event scale factor from the corresponding Gaussian distribution
    float w = rng->Gaus(hist->GetBinContent(bin), hist->GetBinError(bin));
    float e = fabs(w - 1.0);

    w_shape *= w;
    w_shape_up *= w + e;
    w_shape_down *= w - e;
}

//Returns the per-event classification based on the identified flavour of the two jets
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


    cout << "---------------" << endl;
    cout << argv[0] << endl;

    std::string infile;
    bool isWJets = true;

    namespace po = boost::program_options;
    po::options_description desc("Allowed options");
    desc.add_options()
        ("help", "produce help message")
        ("infile", po::value<string>(&infile)->required(), "the input file with a TTree trees/Events")
        ("isWJets", po::value<bool>(&isMC), "do you want to calculate the weights or set a dummy value to unity?")
    ;

    po::variables_map vm;

    try {
        po::store(po::parse_command_line(argc, argv, desc), vm);
        po::notify(vm);    
    } catch(po::error& e) {
        cout << "ERROR: " << e.what() << endl;
        exit(1);
    }

    if (vm.count("help")) {
        cout << desc << "\n";
        return 1;
    }



    rng = new TRandom();
    rng->SetSeed();

    TFile* fi = new TFile(infile.c_str(), "UPDATE");
    fi->cd("trees");
    TTree* events = (TTree*)fi->Get("trees/Events");
    TTree* weight_tree = new TTree("WJets_weights", "WJets_weights");

    TFile* hists_fi0 = new TFile("$STPOL_DIR/CMSSW_5_3_11/src/data/WJets_reweighting/hists__costheta_flavours_merged_scenario0.root", "UPDATE");

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
    vector<string> systematic_scenarios;
    systematic_scenarios.push_back("wjets_mg_flavour_nominal");
    systematic_scenarios.push_back("wjets_mg_flavour_up");
    systematic_scenarios.push_back("wjets_mg_flavour_down");

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
