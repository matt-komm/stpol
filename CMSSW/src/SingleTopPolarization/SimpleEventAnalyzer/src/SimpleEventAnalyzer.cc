// -*- C++ -*-
//
// Package:    SimpleEventAnalyzer
// Class:      SimpleEventAnalyzer
// 
/**\class SimpleEventAnalyzer SimpleEventAnalyzer.cc PhysicsTools/SimpleEventAnalyzer/src/SimpleEventAnalyzer.cc

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

//#include <DataFormats/PatCandidates/interface/Muon.h> //Requred for pat::Muon

#include <DataFormats/Candidate/interface/Candidate.h> //Required for reco::Candidate

#include <FWCore/Utilities/interface/InputTag.h> //Required for edm::InputTag

#include "FWCore/MessageLogger/interface/MessageLogger.h"

#include "DataFormats/Provenance/interface/Provenance.h"

//
// class declaration
//

class SimpleEventAnalyzer : public edm::EDAnalyzer {
   public:
      explicit SimpleEventAnalyzer(const edm::ParameterSet&);
      ~SimpleEventAnalyzer();

      static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);


   private:
      virtual void beginJob() ;
      virtual void analyze(const edm::Event&, const edm::EventSetup&);
      virtual void endJob() ;

      virtual void beginRun(edm::Run const&, edm::EventSetup const&);
      virtual void endRun(edm::Run const&, edm::EventSetup const&);
      virtual void beginLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&);
      virtual void endLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&);

      const std::vector<edm::InputTag> objectsOfInterest;
      const unsigned int maxObjects;
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
SimpleEventAnalyzer::SimpleEventAnalyzer(const edm::ParameterSet& iConfig)
: objectsOfInterest(iConfig.getUntrackedParameter<std::vector<edm::InputTag> >("interestingCollections"))
, maxObjects(iConfig.getUntrackedParameter<unsigned int>("maxObjects"))
{
}


SimpleEventAnalyzer::~SimpleEventAnalyzer()
{
 
   // do anything here that needs to be done at desctruction time
   // (e.g. close files, deallocate resources etc.)

}


//
// member functions
//

// ------------ method called for each event  ------------
void
SimpleEventAnalyzer::analyze(const edm::Event& iEvent, const edm::EventSetup& iSetup)
{
  for(auto& o : objectsOfInterest) {
   edm::Handle<edm::View<reco::Candidate>> objects;
   iEvent.getByLabel(o, objects);
   const edm::Provenance& prov = iEvent.getProvenance(objects.id());
   std::stringstream ss; 
   prov.write(ss);
   edm::LogInfo("provenance:") << ss.str(); 
   //for (edm::View<reco::Candidate>::const_iterator obj = objects->begin(); obj != objects->end(); obj++) {
   edm::LogInfo("analyze()") << "Collection " << o.label() << " has " << objects->size() << " items";
   unsigned int i = 0;
   for (auto& obj : *objects) {
     if (i>maxObjects) break;
     edm::LogInfo("analyze()") << o.label() << "(" << i << "): pt: " << obj.pt() << " eta: " << obj.eta() << " phi: " << obj.phi() << " et: " << obj.et() << std::endl;
     i++; 
   }
 }
   
}


// ------------ method called once each job just before starting event loop  ------------
void 
SimpleEventAnalyzer::beginJob()
{
}

// ------------ method called once each job just after ending the event loop  ------------
void 
SimpleEventAnalyzer::endJob() 
{
}

// ------------ method called when starting to processes a run  ------------
void 
SimpleEventAnalyzer::beginRun(edm::Run const&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a run  ------------
void 
SimpleEventAnalyzer::endRun(edm::Run const&, edm::EventSetup const&)
{
}

// ------------ method called when starting to processes a luminosity block  ------------
void 
SimpleEventAnalyzer::beginLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a luminosity block  ------------
void 
SimpleEventAnalyzer::endLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&)
{
}

// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void
SimpleEventAnalyzer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(SimpleEventAnalyzer);
