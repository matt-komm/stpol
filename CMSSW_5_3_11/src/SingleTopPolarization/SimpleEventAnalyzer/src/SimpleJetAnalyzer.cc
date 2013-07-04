// -*- C++ -*-
//
// Package:    SimpleJetAnalyzer
// Class:      SimpleJetAnalyzer
// 
/**\class SimpleJetAnalyzer SimpleJetAnalyzer.cc PhysicsTools/SimpleJetAnalyzer/src/SimpleJetAnalyzer.cc

 Description: The simplest example of an EDAnalyzer that gets a collection from the file and processes it in some fashion

 Implementation:
     [Notes on implementation]
*/
//
// Original Author:  
//         Created:  Wed Sep 19 15:55:51 EEST 2012
// $Id$
//
//


// system include files
#include <memory>

// user include files
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/EDAnalyzer.h"

#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"

#include <DataFormats/PatCandidates/interface/Jet.h>

#include <DataFormats/Candidate/interface/Candidate.h> //Required for reco::Candidate

#include <FWCore/Utilities/interface/InputTag.h> //Required for edm::InputTag

#include "FWCore/MessageLogger/interface/MessageLogger.h"

//
// class declaration
//

class SimpleJetAnalyzer : public edm::EDAnalyzer {
   public:
      explicit SimpleJetAnalyzer(const edm::ParameterSet&);
      ~SimpleJetAnalyzer();

      static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);


   private:
      virtual void beginJob() ;
      virtual void analyze(const edm::Event&, const edm::EventSetup&);
      virtual void endJob() ;

      virtual void beginRun(edm::Run const&, edm::EventSetup const&);
      virtual void endRun(edm::Run const&, edm::EventSetup const&);
      virtual void beginLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&);
      virtual void endLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&);

      std::vector<edm::InputTag> objectsOfInterest;
      const unsigned int maxJets;

      // ----------member data ---------------------------
};

//
// constants, enums and typedefs
//

//
// static data member definitions
//

//
// constructors and destructor
//
SimpleJetAnalyzer::SimpleJetAnalyzer(const edm::ParameterSet& iConfig)
: maxJets(5)
{
  objectsOfInterest = iConfig.getUntrackedParameter<std::vector<edm::InputTag> >("interestingCollections");
}


SimpleJetAnalyzer::~SimpleJetAnalyzer()
{
 
   // do anything here that needs to be done at desctruction time
   // (e.g. close files, deallocate resources etc.)

}


//
// member functions
//

// ------------ method called for each event  ------------
void
SimpleJetAnalyzer::analyze(const edm::Event& iEvent, const edm::EventSetup& iSetup)
{
  for(auto& o : objectsOfInterest) {
   edm::Handle<edm::View<reco::Candidate>> objects;
   iEvent.getByLabel(o, objects);
   //for (edm::View<reco::Candidate>::const_iterator obj = objects->begin(); obj != objects->end(); obj++) {
   edm::LogInfo("analyze()") << "Collection " << o.label() << " has " << objects->size() << " items";
   unsigned int i = 0;
   for (auto& pobj : *objects) {
    const pat::Jet& obj = (const pat::Jet& )pobj;
    edm::LogInfo("analyze()") << o.label() << "(" << i << "):" <<
    " pt: " << obj.pt() << 
    " pt_smear: " << obj.userFloat("pt_smear") << 
    " eta: " << obj.eta() <<
    " phi: " << obj.phi() << 
    " et: " << obj.et() <<
    " bTag('TCHP'): " << obj.bDiscriminator("trackCountingHighPurBJetTags") <<
    " numberOfDaughters: " << obj.numberOfDaughters() << 
    " neutralHadronEnergyFraction: " << obj.neutralHadronEnergyFraction() << 
    " neutralEmEnergyFraction: " << obj.neutralEmEnergyFraction() << 
    " chargedEmEnergyFraction: " << obj.chargedEmEnergyFraction() <<
    " isJet: " << obj.isJet() <<
    " smearedJet " << obj.genJet();
    i++;
    if(obj.genJet()!=0 && i<maxJets) {
      edm::LogInfo("analyze()") <<
      " pt_gen: " << obj.genJet()->pt() << 
      " eta_gen: " << obj.genJet()->eta();
    }
   
   }
 }
   
}


// ------------ method called once each job just before starting event loop  ------------
void 
SimpleJetAnalyzer::beginJob()
{
}

// ------------ method called once each job just after ending the event loop  ------------
void 
SimpleJetAnalyzer::endJob() 
{
}

// ------------ method called when starting to processes a run  ------------
void 
SimpleJetAnalyzer::beginRun(edm::Run const&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a run  ------------
void 
SimpleJetAnalyzer::endRun(edm::Run const&, edm::EventSetup const&)
{
}

// ------------ method called when starting to processes a luminosity block  ------------
void 
SimpleJetAnalyzer::beginLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a luminosity block  ------------
void 
SimpleJetAnalyzer::endLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&)
{
}

// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void
SimpleJetAnalyzer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(SimpleJetAnalyzer);
