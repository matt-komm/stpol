// -*- C++ -*-
//
// Package:    SimpleMuonAnalyzer
// Class:      SimpleMuonAnalyzer
// 
/**\class SimpleMuonAnalyzer SimpleMuonAnalyzer.cc PhysicsTools/SimpleMuonAnalyzer/src/SimpleMuonAnalyzer.cc

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

#include <DataFormats/PatCandidates/interface/Muon.h>

#include <DataFormats/Candidate/interface/Candidate.h> //Required for reco::Candidate

#include <FWCore/Utilities/interface/InputTag.h> //Required for edm::InputTag

#include "FWCore/MessageLogger/interface/MessageLogger.h"

//
// class declaration
//

class SimpleMuonAnalyzer : public edm::EDAnalyzer {
   public:
      explicit SimpleMuonAnalyzer(const edm::ParameterSet&);
      ~SimpleMuonAnalyzer();

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
SimpleMuonAnalyzer::SimpleMuonAnalyzer(const edm::ParameterSet& iConfig)

{
  objectsOfInterest = iConfig.getUntrackedParameter<std::vector<edm::InputTag> >("interestingCollections");
}


SimpleMuonAnalyzer::~SimpleMuonAnalyzer()
{
 
   // do anything here that needs to be done at desctruction time
   // (e.g. close files, deallocate resources etc.)

}


//
// member functions
//

// ------------ method called for each event  ------------
void
SimpleMuonAnalyzer::analyze(const edm::Event& iEvent, const edm::EventSetup& iSetup)
{
  for(auto& o : objectsOfInterest) {
   edm::Handle<edm::View<reco::Candidate>> objects;
   iEvent.getByLabel(o, objects);
   //for (edm::View<reco::Candidate>::const_iterator obj = objects->begin(); obj != objects->end(); obj++) {
   edm::LogInfo("analyze()") << "Collection " << o.label() << " has " << objects->size() << " items";
   int i = 0;
   for (auto& pobj : *objects) {
    const pat::Muon& obj = (const pat::Muon& )pobj;
    edm::LogInfo("analyze()") << o.label() << "(" << i << "):" <<
    " pt: " << obj.pt() << 
    " eta: " << obj.eta() <<
    " phi: " << obj.phi() << 
    " rhoCorrRelIso: " << obj.userFloat("rhoCorrRelIso") <<
    " deltaBetaCorrRelIso: " << obj.userFloat("deltaBetaCorrRelIso") <<
    " track_hitPattern_trackerLayersWithMeasurement: " << obj.userFloat("track_hitPattern_trackerLayersWithMeasurement") <<
    " globalTrack_hitPattern_numberOfValidMuonHits: " << obj.userFloat("globalTrack_hitPattern_numberOfValidMuonHits") <<
    " innerTrack_hitPattern_numberOfValidPixelHits: " << obj.userFloat("innerTrack_hitPattern_numberOfValidPixelHits") <<
    " dz: " << obj.userFloat("dz");
    i++;
   
   }
 }
   
}


// ------------ method called once each job just before starting event loop  ------------
void 
SimpleMuonAnalyzer::beginJob()
{
}

// ------------ method called once each job just after ending the event loop  ------------
void 
SimpleMuonAnalyzer::endJob() 
{
}

// ------------ method called when starting to processes a run  ------------
void 
SimpleMuonAnalyzer::beginRun(edm::Run const&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a run  ------------
void 
SimpleMuonAnalyzer::endRun(edm::Run const&, edm::EventSetup const&)
{
}

// ------------ method called when starting to processes a luminosity block  ------------
void 
SimpleMuonAnalyzer::beginLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a luminosity block  ------------
void 
SimpleMuonAnalyzer::endLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&)
{
}

// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void
SimpleMuonAnalyzer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(SimpleMuonAnalyzer);
