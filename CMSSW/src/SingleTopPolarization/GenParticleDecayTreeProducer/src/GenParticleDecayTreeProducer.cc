// -*- C++ -*-
//
// Package:    GenParticleDecayTreeProducer
// Class:      GenParticleDecayTreeProducer
// 
/**\class GenParticleDecayTreeProducer GenParticleDecayTreeProducer.cc SingleTopPolarization/GenParticleDecayTreeProducer/src/GenParticleDecayTreeProducer.cc

 Description: [one line class summary]

 Implementation:
     [Notes on implementation]
*/
//
// Original Author:  Joosep Pata
//         Created:  Tue May 14 16:12:40 EEST 2013
// $Id$
//
//


// system include files
#include <memory>

// user include files
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/EDProducer.h"

#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "DataFormats/HepMCCandidate/interface/GenParticle.h"
#include "DataFormats/RecoCandidate/interface/RecoCandidate.h"
#include "DataFormats/PatCandidates/interface/Muon.h"
#include "DataFormats/PatCandidates/interface/Electron.h"
#include "FWCore/Utilities/interface/InputTag.h"
#include "FWCore/MessageLogger/interface/MessageLogger.h"


//
// class declaration
//

template <typename T>
class GenParticleDecayTreeProducer : public edm::EDProducer {
   public:
      explicit GenParticleDecayTreeProducer(const edm::ParameterSet&);
      ~GenParticleDecayTreeProducer();

      static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);

   private:
      virtual void beginJob() ;
      virtual void produce(edm::Event&, const edm::EventSetup&);
      virtual void endJob() ;
      
      virtual void beginRun(edm::Run&, edm::EventSetup const&);
      virtual void endRun(edm::Run&, edm::EventSetup const&);
      virtual void beginLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&);
      virtual void endLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&);

      edm::InputTag src;
};

template <typename T>
GenParticleDecayTreeProducer<T>::GenParticleDecayTreeProducer(const edm::ParameterSet& iConfig)
: src(iConfig.getUntrackedParameter<edm::InputTag>("src"))
{
    produces<std::string>();
}


template <typename T>
GenParticleDecayTreeProducer<T>::~GenParticleDecayTreeProducer()
{

}

std::string recurseDecayTree(const reco::Candidate& part) {
    std::stringstream ss;
    ss << "(" << part.pdgId() << ":" << part.status();
    LogDebug("recurseDecayTree") << "particle " << part.pdgId() << " nMothers=" << part.numberOfMothers();
    for(unsigned int i=0; i<part.numberOfMothers(); i++) {
        const reco::Candidate* pMother = part.mother(i);
        if (pMother==0 || pMother == &part) continue;
        const reco::Candidate& mother = (const reco::Candidate&)(*pMother);
        ss << ", ";
        ss << recurseDecayTree(mother);
    }
    ss << ")";
    return ss.str();
}

template <typename T>
void
GenParticleDecayTreeProducer<T>::produce(edm::Event& iEvent, const edm::EventSetup& iSetup)
{
   using namespace edm;
   LogDebug("") << "GenParticleDecayTreeProducer produce";
   //Need to open reco::Candidate as this is the most general form
   Handle<View<reco::Candidate> > particles;
   iEvent.getByLabel(src, particles);
   if (particles->size()>0) {

       //Need to case to a derived of PATObject to access genParticle, must insure type-safety at runtime
       auto& part = static_cast<const T&>(particles->at(0));

       if (part.genParticlesSize()>0) {
           std::string decayTree("");
           decayTree = recurseDecayTree((const reco::GenParticle&)*part.genParticle(0));
           std::auto_ptr<std::string> pOut(new std::string(decayTree));
           iEvent.put(pOut);
       } 
   }

}

// ------------ method called once each job just before starting event loop  ------------
template <typename T>
void 
GenParticleDecayTreeProducer<T>::beginJob()
{
}

// ------------ method called once each job just after ending the event loop  ------------
template <typename T>
void 
GenParticleDecayTreeProducer<T>::endJob() {
}

// ------------ method called when starting to processes a run  ------------
template <typename T>
void 
GenParticleDecayTreeProducer<T>::beginRun(edm::Run&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a run  ------------
template <typename T>
void 
GenParticleDecayTreeProducer<T>::endRun(edm::Run&, edm::EventSetup const&)
{
}

// ------------ method called when starting to processes a luminosity block  ------------
template <typename T>
void 
GenParticleDecayTreeProducer<T>::beginLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a luminosity block  ------------
template <typename T>
void 
GenParticleDecayTreeProducer<T>::endLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&)
{
}

// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
template <typename T>
void
GenParticleDecayTreeProducer<T>::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(GenParticleDecayTreeProducer<pat::Muon>);
DEFINE_FWK_MODULE(GenParticleDecayTreeProducer<pat::Electron>);
