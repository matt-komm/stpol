#include <string>
#include "cuts_base.h"
#include <TVector3.h>
#include <TVectorD.h>
#include <TMatrixD.h>

#ifndef EVENT_SHAPE_H
#define EVENT_SHAPE_H

class EvtShapeVars : public CutsBase {
public:
    bool doEvtShapeVars;
    const std::string leptonChannel;
    
    edm::InputTag lepPtSrc;
    edm::InputTag lepEtaSrc;
    edm::InputTag lepPhiSrc;
    
    edm::InputTag bjPtSrc;
    edm::InputTag bjEtaSrc;
    edm::InputTag bjPhiSrc;
    
    edm::InputTag ljPtSrc;
    edm::InputTag ljEtaSrc;
    edm::InputTag ljPhiSrc;
    
    edm::InputTag nuPtSrc;
    edm::InputTag nuEtaSrc;
    edm::InputTag nuPhiSrc;
    
    EvtShapeVars(const edm::ParameterSet& pars, BranchVars& _branch_vars);
    bool process(const edm::EventBase& event);
    void initialize_branches();
};
#endif
