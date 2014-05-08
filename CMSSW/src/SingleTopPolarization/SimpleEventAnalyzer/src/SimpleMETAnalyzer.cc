// -*- C++ -*-
//
// Package:    SimpleMETAnalyzer
// Class:      SimpleMETAnalyzer
// 
/**\class SimpleMETAnalyzer SimpleMETAnalyzer.cc PhysicsTools/SimpleMETAnalyzer/src/SimpleMETAnalyzer.cc

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

#include <DataFormats/PatCandidates/interface/MET.h>

#include <DataFormats/Candidate/interface/Candidate.h> //Required for reco::Candidate

#include <FWCore/Utilities/interface/InputTag.h> //Required for edm::InputTag

#include "FWCore/MessageLogger/interface/MessageLogger.h"

//
// class declaration
//

class SimpleMETAnalyzer : public edm::EDAnalyzer {
   public:
      explicit SimpleMETAnalyzer(const edm::ParameterSet&);
      ~SimpleMETAnalyzer();

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
SimpleMETAnalyzer::SimpleMETAnalyzer(const edm::ParameterSet& iConfig)

{
  objectsOfInterest = iConfig.getUntrackedParameter<std::vector<edm::InputTag> >("interestingCollections");
}


SimpleMETAnalyzer::~SimpleMETAnalyzer()
{
 
   // do anything here that needs to be done at desctruction time
   // (e.g. close files, deallocate resources etc.)

}


//
// member functions
//

// ------------ method called for each event  ------------
void
SimpleMETAnalyzer::analyze(const edm::Event& iEvent, const edm::EventSetup& iSetup)
{
  for(auto& o : objectsOfInterest) {
   edm::Handle<edm::View<reco::Candidate>> objects;
   iEvent.getByLabel(o, objects);
   //for (edm::View<reco::Candidate>::const_iterator obj = objects->begin(); obj != objects->end(); obj++) {
   edm::LogInfo("analyze()") << "Collection " << o.label() << " has " << objects->size() << " items";
   int i = 0;
   for (auto& pobj : *objects) {
    const pat::MET& obj = (const pat::MET& )pobj;
    edm::LogInfo("analyze()") << o.label() << "(" << i << "):" <<
    " pt: " << obj.pt() << 
    " px: " << obj.p4().Px() <<
    " py: " << obj.p4().Py() <<
    " pz: " << obj.p4().Pz();
    if (obj.genMET() != 0) {
      edm::LogInfo("analyze()") << "genMET " <<
      " pt: " << obj.genMET()->pt() <<
      " px: " << obj.genMET()->p4().Px() <<
      " py: " << obj.genMET()->p4().Py() <<
      " pz: " << obj.genMET()->p4().Pz();
    }

   }
 }
   
}


// ------------ method called once each job just before starting event loop  ------------
void 
SimpleMETAnalyzer::beginJob()
{
}

// ------------ method called once each job just after ending the event loop  ------------
void 
SimpleMETAnalyzer::endJob() 
{
}

// ------------ method called when starting to processes a run  ------------
void 
SimpleMETAnalyzer::beginRun(edm::Run const&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a run  ------------
void 
SimpleMETAnalyzer::endRun(edm::Run const&, edm::EventSetup const&)
{
}

// ------------ method called when starting to processes a luminosity block  ------------
void 
SimpleMETAnalyzer::beginLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a luminosity block  ------------
void 
SimpleMETAnalyzer::endLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&)
{
}

// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void
SimpleMETAnalyzer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(SimpleMETAnalyzer);
