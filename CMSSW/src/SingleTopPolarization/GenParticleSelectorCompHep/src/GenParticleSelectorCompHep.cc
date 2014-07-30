// -*- C++ -*-
//
// Package:    GenParticleSelectorCompHep
// Class:      GenParticleSelectorCompHep
//
/**\class GenParticleSelectorCompHep GenParticleSelectorCompHep.cc SingleTopPolarization/GenParticleSelectorCompHep/src/GenParticleSelectorCompHep.cc
 
 Description: [one line class summary]
 
 Implementation:
 [Notes on implementation]
 */
//
// Original Author:  Andres Tiko
//         Created:  N apr    4 11:47:22 EEST 2013
// $Id$
//
//


// system include files
#include <memory>
#include <TMath.h>

// user include files
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/EDProducer.h"

#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "DataFormats/HepMCCandidate/interface/GenParticle.h"

#include "DataFormats/PatCandidates/interface/Jet.h"
#include "FWCore/MessageLogger/interface/MessageLogger.h"

using namespace edm;
using namespace std;
using namespace reco;

//
// class declaration
//

class GenParticleSelectorCompHep : public edm::EDProducer {
public:
    explicit GenParticleSelectorCompHep(const edm::ParameterSet&);
    ~GenParticleSelectorCompHep();
    
    static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);
    
private:
    edm::InputTag _srcTag;

    virtual void beginJob() ;
    virtual void produce(edm::Event&, const edm::EventSetup&);
    virtual void endJob() ;
    
    virtual void beginRun(edm::Run&, edm::EventSetup const&);
    virtual void endRun(edm::Run&, edm::EventSetup const&);
    virtual void beginLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&);
    virtual void endLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&);
    
};


GenParticleSelectorCompHep::GenParticleSelectorCompHep(const edm::ParameterSet& iConfig)
{
    produces<std::vector<GenParticle>>("trueTop");
    produces<std::vector<GenParticle>>("trueLightJet");
    produces<std::vector<GenParticle>>("trueBJet");
    produces<std::vector<GenParticle>>("trueLepton");
    produces<std::vector<GenParticle>>("trueNeutrino");
    produces<std::vector<GenParticle>>("trueWboson");
    produces<int>("trueLeptonPdgId");
    
    _srcTag = iConfig.getParameter<edm::InputTag>("src");
    
}


GenParticleSelectorCompHep::~GenParticleSelectorCompHep()
{
    
    // do anything here that needs to be done at desctruction time
    // (e.g. close files, deallocate resources etc.)
    
}


//
// member functions
//

// ------------ method called to produce the data  ------------
void
GenParticleSelectorCompHep::produce(edm::Event& iEvent, const edm::EventSetup& iSetup)
{

    Handle<GenParticleCollection> genParticles;
    iEvent.getByLabel(_srcTag, genParticles);

    
    //std::auto_ptr<std::vector<GenParticle> > outTops(new std::vector<GenParticle>());
    std::auto_ptr<std::vector<GenParticle> > outLightJets(new std::vector<GenParticle>());
    std::auto_ptr<std::vector<GenParticle> > outBJets(new std::vector<GenParticle>());
    std::auto_ptr<std::vector<GenParticle> > outLeptons(new std::vector<GenParticle>());
    std::auto_ptr<std::vector<GenParticle> > outNeutrinos(new std::vector<GenParticle>());
    std::auto_ptr<std::vector<GenParticle> > outWbosons(new std::vector<GenParticle>());
    std::auto_ptr<std::vector<GenParticle> > outTop(new std::vector<GenParticle>());
    
    const GenParticle* lightJet = nullptr;
    const GenParticle* bJet = nullptr;
    const GenParticle* lepton = nullptr;
    const GenParticle* neutrino = nullptr;
    
    for(size_t iparticle = 0; iparticle < genParticles->size(); ++ iparticle) 
    {
        const GenParticle& p = (*genParticles)[iparticle];
        
        if (!((p.status() == 3) && p.numberOfMothers ()==2) && !((abs(p.pdgId())==15) && (p.status() == 1)))
        {
            //particle is neither final nor an intermediate tau
            continue;
        }
        
        if (!lepton && ((abs(p.pdgId())==11) or (abs(p.pdgId())==13) or (abs(p.pdgId())==15)))
        {
            outLeptons->push_back(p);
            lepton=&p;
        }
        
        if (!neutrino && ((abs(p.pdgId())==12) or (abs(p.pdgId())==14) or abs(p.pdgId())==16))
        {
            outNeutrinos->push_back(p);
            neutrino=&p;
        }
        
        if (!lightJet && (abs(p.pdgId())<5))
        {
            outLightJets->push_back(p);
            lightJet=&p;
        }
        
    }
    if (!lepton || !neutrino || !lightJet)
    {
        LogWarning("lepton, neutrino, or light quark not found in current event");
        iEvent.put(outLeptons, "trueLepton");
        iEvent.put(outLightJets, "trueLightJet");
        iEvent.put(outBJets, "trueBJet");
        iEvent.put(outNeutrinos, "trueNeutrino");
        iEvent.put(outWbosons, "trueWboson");
        iEvent.put(outTop,"trueTop");
        iEvent.put(std::auto_ptr<int>(new int(0)), "trueLeptonPdgId");
        return;
    }
    
    for(size_t i = 0; i < genParticles->size(); ++ i) 
    {
        const GenParticle& p = (*genParticles)[i];
        if ((p.status() == 3) && (p.numberOfMothers()==2) && (abs(p.pdgId())==5) && (p.pdgId()*lepton->pdgId()<0))
        {
            outBJets->push_back(p);
            bJet=&p;
            break;
        }
    }
        
    if (!bJet)
    {
        LogWarning("lepton, neutrino, or light quark not found in current event");
        iEvent.put(outLeptons, "trueLepton");
        iEvent.put(outLightJets, "trueLightJet");
        iEvent.put(outBJets, "trueBJet");
        iEvent.put(outNeutrinos, "trueNeutrino");
        iEvent.put(outWbosons, "trueWboson");
        iEvent.put(outTop,"trueTop");
        iEvent.put(std::auto_ptr<int>(new int(0)), "trueLeptonPdgId");
        return;
    }
   
    LogDebug("part") << "lepton " << lepton->p4(); 
    LogDebug("part") << "neutrino " << neutrino->p4(); 
    //GenParticle (Charge q, const LorentzVector &p4, const Point &vtx, int pdgId, int status, bool integerCharge)
    GenParticle wboson(lepton->charge(),lepton->p4()+neutrino->p4(),reco::Candidate::Point(),24*lepton->charge(),1,true);
    LogDebug("part") << "W " << wboson.p4(); 
    outWbosons->push_back(wboson);
    
    GenParticle top(wboson.charge(),bJet->p4()+wboson.p4(),reco::Candidate::Point(),6*wboson.charge(),1,false);
    LogDebug("part") << "bJet " << bJet->p4(); 
    LogDebug("part") << "top " << top.mass(); 
    outTop->push_back(top);
    
    iEvent.put(outLeptons, "trueLepton");
    iEvent.put(outLightJets, "trueLightJet");
    iEvent.put(outBJets, "trueBJet");
    iEvent.put(outNeutrinos, "trueNeutrino");
    iEvent.put(outWbosons, "trueWboson");
    iEvent.put(outTop,"trueTop");
    iEvent.put(std::auto_ptr<int>(new int(lepton->pdgId())), "trueLeptonPdgId");
    
}

// ------------ method called once each job just before starting event loop  ------------
void
GenParticleSelectorCompHep::beginJob()
{
}

// ------------ method called once each job just after ending the event loop  ------------
void
GenParticleSelectorCompHep::endJob() {

}

// ------------ method called when starting to processes a run  ------------
void
GenParticleSelectorCompHep::beginRun(edm::Run&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a run  ------------
void
GenParticleSelectorCompHep::endRun(edm::Run&, edm::EventSetup const&)
{
}

// ------------ method called when starting to processes a luminosity block  ------------
void
GenParticleSelectorCompHep::beginLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a luminosity block  ------------
void
GenParticleSelectorCompHep::endLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&)
{
}

// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void
GenParticleSelectorCompHep::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
    //The following says we do not know what parameters are allowed so do no validation
    // Please change this to state exactly what you do use, even if it is no parameters
    edm::ParameterSetDescription desc;
    desc.setUnknown();
    descriptions.addDefault(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(GenParticleSelectorCompHep);
