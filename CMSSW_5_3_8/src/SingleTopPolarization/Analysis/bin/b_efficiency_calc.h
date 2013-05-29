#include "cuts_base.h"
#include "TFile.h"
#include "PhysicsTools/FWLite/interface/TFileService.h"
#include "TH2D.h"
#ifndef B_EFF_CALC_H
#define B_EFF_CALC_H


class BEffCalcs : public CutsBase {
public:
    edm::InputTag jet_pt_src;
    edm::InputTag jet_eta_src;
    edm::InputTag jet_bdisc_src;
    edm::InputTag jet_flavour_src;
    void initialize_branches();

    TH2D* true_b_distribution;
    TH2D* true_b_tagged_distribution;
    TH2D* true_c_distribution;
    TH2D* true_c_tagged_distribution;
    TH2D* true_l_distribution;
    TH2D* true_l_tagged_distribution;

    BEffCalcs(const edm::ParameterSet& pars, BranchVars& _branch_vars, TFileDirectory& dir);

    bool process(const edm::EventBase& event);
    const float b_discriminator_wp;
    const bool doBEffCalcs;
};
#endif
