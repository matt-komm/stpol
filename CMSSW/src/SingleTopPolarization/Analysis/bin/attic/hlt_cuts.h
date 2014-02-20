#include "cuts_base.h"
#include <DataFormats/Common/interface/TriggerResults.h>
#include <FWCore/Common/interface/TriggerNames.h>
#ifndef HLT_CUTS_H
#define HLT_CUTS_H


class HLTCuts : public CutsBase {
public:
    edm::InputTag hlt_src;
    std::vector<std::string> hlt_names;
    bool cut_on_HLT;
    bool save_HLT_vars;
    std::vector<std::string> hlt_cut_names;

    edm::Handle<edm::TriggerResults> trig_results;
    void initialize_branches();
     
    HLTCuts(const edm::ParameterSet& pars, BranchVars& _branch_vars);

    bool process(const edm::EventBase& event);
};
#endif
