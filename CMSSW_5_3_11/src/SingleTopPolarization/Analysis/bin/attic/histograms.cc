#define CLANG

#include <TTree.h>
#include <TEventList.h>
#include <TFile.h>
#include <TSystem.h>
#include <TObject.h>
#include <TTreeFormula.h>
#include <iostream>
#include <sstream>
#include <TH1F.h>
#include <string>
#include <stdlib.h>
#include <vector>
#include <map>
#include <memory>

#ifdef CLANG
#include <tr1/tuple>
#else
#include <tuple>
#endif

#include <boost/any.hpp>
#include <boost/program_options.hpp>

#include "jet_flavour_classifications.h"

template <typename T>
void get_branch(const char *name, T *address, TTree *tree)
{
    tree->SetBranchStatus(name, 1);
    tree->SetBranchAddress(name, address);
    tree->AddBranchToCache(name);
}
using namespace std;

#ifdef CLANG
using namespace std::tr1;
#endif

typedef tuple <
int, int, int,
     //    string, string, string,
     string, string
     > hist_ident;
const std::string id_to_string(hist_ident tup)
{
    std::ostringstream ss;
    ss  << "N_jets__" << get<0>(tup)
        << "/N_tags__" << get<1>(tup)
        << "/jet_flavour__" << get<2>(tup)

        //        << "/mt_mu__" << get<3>(tup)
        //        << "/eta_lj__" << get<4>(tup)
        //        << "/top_mass__" << get<5>(tup)

        << "/weight__" << get<3>(tup)
        << "/var__" << get<4>(tup);
    return ss.str();
};

void ReplaceStringInPlace(std::string &subject, const std::string &search,
                          const std::string &replace)
{
    size_t pos = 0;
    while ((pos = subject.find(search, pos)) != std::string::npos)
    {
        subject.replace(pos, search.length(), replace);
        pos += replace.length();
    }
}

#define PLOT_PARS_COSTHETA 100, -1, 1
#define PLOT_PARS_ABS_ETA_LJ 100, 2.5, 5
#define PLOT_PARS_ETA_LJ 100, 0.0, 5.0

int main(int argc, char **argv)
{

    cout << "---------------" << endl;
    cout << argv[0] << endl;

    std::string infile;
    std::string outfile;
    bool doWJetsMadgraphWeights = false;
    bool doWJetsSherpaWeight = false;
    bool doSelect = false;
    bool isMC = true;
    std::string cut("n_muons==1 && n_eles==0 && n_veto_mu==0 && n_jets>0 && n_veto_ele==0 && rms_lj<0.025 && abs(eta_lj)>2.5 && top_mass<220 && top_mass>130 && mt_mu>50");
    std::string weight("1.0");

    namespace po = boost::program_options;
    po::options_description desc("Allowed options");
    desc.add_options()
    ("help", "produce help message")
    ("infile", po::value<string>(&infile)->required(), "the input file with a TTree trees/Events")
    ("outfile", po::value<string>(&outfile)->required(), "the output ROOT file with histograms")
    ("cut", po::value<string>(&cut), "The preselection cut string")
    ("weight", po::value<string>(&weight), "The weight to always apply")

    ("doWJetsMadgraphWeight", po::value<bool>(&doWJetsMadgraphWeights), "do weighted histograms with madgraph?")
    ("doWJetsSherpaWeight", po::value<bool>(&doWJetsSherpaWeight), "do weighted histograms with sherpa?")
    ("doSelect", po::value<bool>(&doSelect), "do the selection again?")

    ("isMC", po::value<bool>(&isMC), "do the selection again?")
    ;

    po::variables_map vm;

    try
    {
        po::store(po::parse_command_line(argc, argv, desc), vm);
        po::notify(vm);
    }
    catch (po::error &e)
    {
        cout << "ERROR: " << e.what() << endl;
        exit(1);
    }

    if (vm.count("help"))
    {
        cout << desc << "\n";
        return 1;
    }

    std::vector<int> N_jets;
    N_jets.push_back(2);
    N_jets.push_back(3);
    std::vector<int> N_tags;
    N_tags.push_back(0);
    N_tags.push_back(1);
    N_tags.push_back(2);

    const std::string fname = infile.substr(infile.rfind("/") + 1, infile.find(".root") - infile.rfind("/"));
    std::cout << "Input file is " << infile << std::endl;

    TFile *fi = new TFile(infile.c_str());
    TTree *events = (TTree *)fi->Get("trees/Events");
    if (doWJetsMadgraphWeights)
        events->AddFriend("trees/WJets_weights");
    events->SetCacheSize(10000000);

    vector<const char *> vars_to_enable;
    events->SetBranchStatus("*", 0);

    vars_to_enable.push_back("n_muons");
    vars_to_enable.push_back("n_eles");
    vars_to_enable.push_back("n_veto_mu");
    vars_to_enable.push_back("n_veto_ele");
    vars_to_enable.push_back("n_jets");
    vars_to_enable.push_back("top_mass");
    vars_to_enable.push_back("eta_lj");
    vars_to_enable.push_back("rms_lj");
    vars_to_enable.push_back("mt_mu");
    vars_to_enable.push_back("deltaR_bj");
    vars_to_enable.push_back("deltaR_lj");
    vars_to_enable.push_back("mu_iso");
    vars_to_enable.push_back("*weight*");
    vars_to_enable.push_back("*Weight*");

    for (auto & v : vars_to_enable)
    {
        events->SetBranchStatus(v, 1);
        events->AddBranchToCache(v);
    }

    TFile *ofi = new TFile(outfile.c_str(), "RECREATE");
    std::cout << "Output file is " << outfile << std::endl;
    ofi->cd();


    const std::string elist_name = std::string("elist__") + fname;

    //std::cout << "Looking for event list with name " << elist_name << std::endl;
    TObject *elist_ = ofi->Get(elist_name.c_str());
    //std::cout << "elist_=" << elist_ << std::endl;
    TEventList *elist = (TEventList *)elist_;

    //TTreeFormula* form = new TTreeFormula("weight", weight.c_str(), events);

    int Nentries = -1;
    if (elist == 0 || doSelect)
    {
        std::cout << "Performing preselection with str='" << cut << "'" << std::endl;

        Nentries = events->Draw((std::string(">>") + elist_name).c_str(), cut.c_str());
        elist = (TEventList *)ofi->Get(elist_name.c_str());
        std::cout << Nentries << " events selected with preselection" << std::endl;
        ofi->Flush();
    }
    else
    {
        Nentries = elist->GetN();
        std::cout << "Loaded preselection" << endl;

    }

    events->SetBranchStatus("*", 0);
    events->SetEventList(elist);

    int n_jets = -1;
    get_branch<int>("n_jets", &n_jets, events);
    int n_tags = -1;
    get_branch<int>("n_tags", &n_tags, events);

    float cos_theta = -1;
    get_branch<float>("cos_theta", &cos_theta, events);
    float eta_lj = -1;
    get_branch<float>("eta_lj", &eta_lj, events);

    int jet_flavour_classification = -1;

    vector<string> weights;

    vector<string> shape_weight_names;
    shape_weight_names.push_back("wjets_mg_flavour_shape_weight");
    shape_weight_names.push_back("wjets_mg_flavour_shape_weight_up");
    shape_weight_names.push_back("wjets_mg_flavour_shape_weight_down");

    vector<string> yield_weight_names;
    yield_weight_names.push_back("wjets_mg_flavour_flat_weight");
    yield_weight_names.push_back("wjets_mg_flavour_flat_weight_up");
    yield_weight_names.push_back("wjets_mg_flavour_flat_weight_down");

    weights.push_back("unweighted");

    map<string, float> wjets_weight_branches;
    auto getbranch = [&events, &wjets_weight_branches](const char * s)
    {
        wjets_weight_branches[s] = (float)1.0;
        events->SetBranchStatus(s, 1);
        events->SetBranchAddress(s, &wjets_weight_branches[s]);
        events->AddBranchToCache(s);
    };

    if (isMC)
    {
        getbranch("pu_weight");
        getbranch("b_weight_nominal");
        getbranch("muon_IsoWeight");
        getbranch("muon_IDWeight");
        getbranch("gen_weight");
    }


    if (doWJetsMadgraphWeights)
    {
        get_branch<int>("wjets_flavour_classification0", &jet_flavour_classification, events);

        for (auto & e : shape_weight_names)
            getbranch(e.c_str());
        for (auto & e : yield_weight_names)
            getbranch(e.c_str());

        weights.push_back("weighted_wjets_mg_flavour_nominal");
        weights.push_back("weighted_wjets_mg_flavour_up");
        weights.push_back("weighted_wjets_mg_flavour_down");
    }

    int min_flavour = -1;
    int max_flavour = -1;
    if (doWJetsMadgraphWeights)
    {
        min_flavour = 0;
        max_flavour = 7;
    }

    std::map<hist_ident, TH1 *> hists;
    TH1::AddDirectory(false);
    for (auto & weight : weights)
    {
        for (int i = min_flavour; i <= max_flavour; i++)
        {
            for (int n_jets = 2; n_jets <= 3; n_jets++)
            {
                for (int n_tags = 0; n_tags < 3; n_tags++)
                {
                    hists[make_tuple(n_jets, n_tags, i, weight.c_str(), "cos_theta")] = new TH1F("cos_theta", "cos_theta", PLOT_PARS_COSTHETA);
                    hists[make_tuple(n_jets, n_tags, i, weight.c_str(), "abs_eta_lj")] = new TH1F("abs_eta_lj", "abs_eta_lj", PLOT_PARS_ABS_ETA_LJ);
                    hists[make_tuple(n_jets, n_tags, i, weight.c_str(), "eta_lj")] = new TH1F("eta_lj", "eta_lj", PLOT_PARS_ETA_LJ);
                }
            }
        }
    }

    TH1::AddDirectory(true);

    for (auto & e : hists)
    {
        const std::string dirname(id_to_string(e.first));
        //ofi->rmdir(dirname.c_str());
        TDirectory *dir = (TDirectory *)ofi->Get(dirname.c_str());
        if (!dir)
        {
            dir = ofi->mkdir(dirname.c_str());
        }
        if (dir)
        {
            dir = (TDirectory *)ofi->Get(dirname.c_str());
        }
        else
        {
            cerr << "Couldn't make directory " << dirname << endl;
            throw 1;
        }
        e.second->SetDirectory(dir);
        e.second->Sumw2();
    }


    //cos_theta_hists[]
    long Nbytes = 0;
    cout << "Beginning event loop." << endl;

    map<string, float> sum_weights;
    for (auto & e : yield_weight_names)
        sum_weights[e] = 0.0;

    for (int n = 0; n < Nentries; n++)
    {
        long idx = elist->GetEntry(n);
        Nbytes += events->GetEntry(idx);

        //Calculate the sum of the shape weights for normalization
        for (auto & e : yield_weight_names)
            sum_weights[e] += wjets_weight_branches[e];


        if (n_jets == 2)
        {
            if (n_tags == 1 || n_tags == 0)
            {
                //int ndata = form->GetNdata();
                //for(int i=0;i<ndata; i++)
                //    form->EvalInstance(i);
                float w = 1.0;
                if (isMC)
                {
                    w = wjets_weight_branches["pu_weight"] * wjets_weight_branches["b_weight_nominal"] * wjets_weight_branches["muon_IsoWeight"] * wjets_weight_branches["muon_IDWeight"];
                    if (doWJetsSherpaWeight)
                        w *= wjets_weight_branches["gen_weight"];
                }
                //std::cout << w << endl;
                hists[make_tuple(n_jets, n_tags, jet_flavour_classification, weights[0], "cos_theta")]->Fill(cos_theta, w);
                hists[make_tuple(n_jets, n_tags, jet_flavour_classification, weights[0], "abs_eta_lj")]->Fill(fabs(eta_lj), w);
                hists[make_tuple(n_jets, n_tags, jet_flavour_classification, weights[0], "eta_lj")]->Fill(eta_lj, w);

                if (doWJetsMadgraphWeights)
                {
                    hists[make_tuple(n_jets, n_tags, jet_flavour_classification, weights[1], "cos_theta")]->Fill(
                        cos_theta,
                        w * wjets_weight_branches["wjets_mg_flavour_flat_weight"]*wjets_weight_branches["wjets_mg_flavour_shape_weight"]
                    );
                    hists[make_tuple(n_jets, n_tags, jet_flavour_classification, weights[1], "abs_eta_lj")]->Fill(
                        fabs(eta_lj),
                        w * wjets_weight_branches["wjets_mg_flavour_flat_weight"]*wjets_weight_branches["wjets_mg_flavour_shape_weight"]
                    );
                    hists[make_tuple(n_jets, n_tags, jet_flavour_classification, weights[1], "eta_lj")]->Fill(
                        eta_lj,
                        w * wjets_weight_branches["wjets_mg_flavour_flat_weight"]*wjets_weight_branches["wjets_mg_flavour_shape_weight"]
                    );


                    hists[make_tuple(n_jets, n_tags, jet_flavour_classification, weights[2], "cos_theta")]->Fill(
                        cos_theta,
                        w * wjets_weight_branches["wjets_mg_flavour_flat_weight_up"]*wjets_weight_branches["wjets_mg_flavour_shape_weight_up"]
                    );
                    hists[make_tuple(n_jets, n_tags, jet_flavour_classification, weights[2], "abs_eta_lj")]->Fill(
                        fabs(eta_lj),
                        w * wjets_weight_branches["wjets_mg_flavour_flat_weight_up"]*wjets_weight_branches["wjets_mg_flavour_flat_weight_up"]
                    );
                    hists[make_tuple(n_jets, n_tags, jet_flavour_classification, weights[2], "eta_lj")]->Fill(
                        eta_lj,
                        w * wjets_weight_branches["wjets_mg_flavour_flat_weight_up"]*wjets_weight_branches["wjets_mg_flavour_flat_weight_up"]
                    );


                    hists[make_tuple(n_jets, n_tags, jet_flavour_classification, weights[3], "cos_theta")]->Fill(
                        cos_theta,
                        w * wjets_weight_branches["wjets_mg_flavour_flat_weight_down"]*wjets_weight_branches["wjets_mg_flavour_shape_weight_down"]
                    );
                    hists[make_tuple(n_jets, n_tags, jet_flavour_classification, weights[3], "abs_eta_lj")]->Fill(
                        fabs(eta_lj),
                        w * wjets_weight_branches["wjets_mg_flavour_flat_weight_down"]*wjets_weight_branches["wjets_mg_flavour_shape_weight_down"]
                    );
                    hists[make_tuple(n_jets, n_tags, jet_flavour_classification, weights[3], "eta_lj")]->Fill(
                        eta_lj,
                        w * wjets_weight_branches["wjets_mg_flavour_flat_weight_down"]*wjets_weight_branches["wjets_mg_flavour_shape_weight_down"]
                    );


                }
            }
        }

    }
    std::cout << "Read " << Nbytes << " bytes" << std::endl;

    for (auto & e : sum_weights)
    {
        e.second = e.second / (float)Nentries;
        cout << "Mean weight " << e.first << " " << e.second << endl;
    }
    /*
        for (auto & e : hists)
        {
            if (get<3>(e.first) == weights[1])
            {
                e.second->Scale(sum_weights["wjets_mg_flavour_shape_weight"]);
            }
        }
    */
    events->SetCacheSize(0);

    TObject *count_hist = (fi->Get("trees/count_hist;1"));
    float ngen = 1.0;
    if (count_hist && isMC)
    {
        ngen = ((TH1I *)count_hist)->GetBinContent(1);
    }
    std::cout << "ngen=" << ngen << endl;
    for (auto & e : hists)
    {
        if (ngen > 0.0)
        {
            e.second->Scale(1.0 / ngen);
        }
    }

    fi->Close();
    delete fi;

    cout << "Writing file" << endl;
    ofi->Write();
    ofi->Close();
    delete ofi;

    return 0;
}
