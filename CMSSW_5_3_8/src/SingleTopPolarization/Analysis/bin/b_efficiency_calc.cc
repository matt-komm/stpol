#include "b_efficiency_calc.h"
#include <limits>
#include <cmath>

const float eps = std::numeric_limits<float>::epsilon();
bool AreSame(float a, float b) {
        return std::fabs(a - b) < eps;
}

static const unsigned int n_eta_bins = 4;
const Double_t eta_bins_low[n_eta_bins] = {
    (Double_t)0.0,
    (Double_t)0.8,
    (Double_t)1.6,
    (Double_t)2.4
};

static const unsigned int n_pt_bins = 18;
const Double_t pt_bins_low[n_pt_bins] = {
    0,
    20,
    30,
    40,
    50,
    60,
    70,
    80,
    100,
    120,
    160,
    210,
    260,
    320,
    400,
    500,
    600,
    800
};
const static std::vector<float> empty_vec;
void BEffCalcs::initialize_branches() {
}

BEffCalcs::BEffCalcs(const edm::ParameterSet& pars, BranchVars& _branch_vars, TFileDirectory& dir)
: CutsBase(_branch_vars)
, jet_pt_src(pars.getParameter<edm::InputTag>("jetPtSrc"))
, jet_eta_src(pars.getParameter<edm::InputTag>("jetEtaSrc"))
, jet_bdisc_src(pars.getParameter<edm::InputTag>("jetBDiscriminatorSrc"))
, jet_flavour_src(pars.getParameter<edm::InputTag>("jetFlavourSrc"))
, doBEffCalcs (pars.getParameter<bool>("doBEffCalcs"))
, b_discriminator_wp(3.41)
{
    const Double_t* p_pt_bins_low = (const Double_t*)&pt_bins_low;
    const Double_t* p_eta_bins_low = (const Double_t*)&eta_bins_low;
    Int_t _n_pt_bins = (Int_t)n_pt_bins-1;
    Int_t _n_eta_bins = (Int_t)n_eta_bins-1;

    true_b_distribution = dir.make<TH2D>("true_b", "True b", _n_pt_bins, p_pt_bins_low, _n_eta_bins, p_eta_bins_low);
    true_b_tagged_distribution = dir.make<TH2D>("true_b_tagged", "True b tagged", _n_pt_bins, p_pt_bins_low, _n_eta_bins, p_eta_bins_low); 
    
    true_c_distribution = dir.make<TH2D>("true_c", "True c",  _n_pt_bins, p_pt_bins_low, _n_eta_bins, p_eta_bins_low);
    true_c_tagged_distribution = dir.make<TH2D>("true_c_tagged", "True c tagged", _n_pt_bins, p_pt_bins_low, _n_eta_bins, p_eta_bins_low); 
    
    true_l_distribution = dir.make<TH2D>("true_l", "True l",  _n_pt_bins, p_pt_bins_low, _n_eta_bins, p_eta_bins_low);
    true_l_tagged_distribution = dir.make<TH2D>("true_l_tagged", "True l tagged", _n_pt_bins, p_pt_bins_low, _n_eta_bins, p_eta_bins_low); 
}

bool BEffCalcs::process(const edm::EventBase& event) {
    pre_process();

    std::vector<float> jet_pts = get_collection<std::vector<float>>(event, jet_pt_src, empty_vec);
    std::vector<float> jet_etas = get_collection<std::vector<float>>(event, jet_eta_src, empty_vec);
    std::vector<float> jet_bdiscs = get_collection<std::vector<float>>(event, jet_bdisc_src, empty_vec);
    std::vector<float> jet_flavours = get_collection<std::vector<float>>(event, jet_flavour_src, empty_vec);
    const unsigned int size = jet_pts.size();
    if(jet_etas.size() != size || jet_bdiscs.size() != size || jet_flavours.size() != size) {
        throw;
    }

    for (unsigned int i=0; i<size; i++) {
        float pt = jet_pts[i]; 
        float eta = jet_etas[i]; 
        float bdisc = jet_bdiscs[i]; 
        float flavour = jet_flavours[i];

        TH2D* true_distr = 0;
        TH2D* true_tagged_distr = 0;

        //b
        if(AreSame(std::fabs(flavour), 5.0)) {
            true_distr = true_b_distribution; 
            true_tagged_distr = true_b_tagged_distribution; 
        }
        //c
        else if(AreSame(std::fabs(flavour), 4.0)) {
            true_distr = true_c_distribution; 
            true_tagged_distr = true_c_tagged_distribution; 
        }
        //l
        else {
            true_distr = true_l_distribution; 
            true_tagged_distr = true_l_tagged_distribution; 
        }

        true_distr->Fill(pt, std::fabs(eta)); 
        if (bdisc >= b_discriminator_wp) {
            true_tagged_distr->Fill(pt, std::fabs(eta));
        }
    }
    post_process();
    return true;
}
