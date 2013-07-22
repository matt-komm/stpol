// -*- C++ -*-
//
// Package:    SimpleElectronAnalyzer
// Class:      SimpleElectronAnalyzer
// 
/**\class SimpleElectronAnalyzer SimpleElectronAnalyzer.cc PhysicsTools/SimpleElectronAnalyzer/src/SimpleElectronAnalyzer.cc

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

#include <DataFormats/PatCandidates/interface/Electron.h>

#include <DataFormats/Candidate/interface/Candidate.h> //Required for reco::Candidate

#include <FWCore/Utilities/interface/InputTag.h> //Required for edm::InputTag

#include "FWCore/MessageLogger/interface/MessageLogger.h"

//
// class declaration
//

class SimpleElectronAnalyzer : public edm::EDAnalyzer {
   public:
      explicit SimpleElectronAnalyzer(const edm::ParameterSet&);
      ~SimpleElectronAnalyzer();

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
SimpleElectronAnalyzer::SimpleElectronAnalyzer(const edm::ParameterSet& iConfig)

{
  objectsOfInterest = iConfig.getUntrackedParameter<std::vector<edm::InputTag> >("interestingCollections");
}


SimpleElectronAnalyzer::~SimpleElectronAnalyzer()
{
 
   // do anything here that needs to be done at desctruction time
   // (e.g. close files, deallocate resources etc.)

}


//
// member functions
//

// ------------ method called for each event  ------------
void
SimpleElectronAnalyzer::analyze(const edm::Event& iEvent, const edm::EventSetup& iSetup)
{
  for(auto& o : objectsOfInterest) {
   edm::Handle<edm::View<reco::Candidate>> objects;
   iEvent.getByLabel(o, objects);
   //for (edm::View<reco::Candidate>::const_iterator obj = objects->begin(); obj != objects->end(); obj++) {
   edm::LogInfo("analyze()") << "Collection " << o.label() << " has " << objects->size() << " items";
   int i = 0;

   for (auto& pobj : *objects) {
    const pat::Electron& obj = (const pat::Electron& )pobj;
    edm::LogInfo("analyze()") << o.label() << "(" << i << "):" <<
    "\n\t pt: " << obj.pt() << 
    "\n\t ecalPt: " << obj.ecalDrivenMomentum().Pt() << 
    "\n\t eta: " << obj.eta() <<
    "\n\t supercluster.eta: " << obj.superCluster()->eta() <<
    "\n\t phi: " << obj.phi() << 
    "\n\t passConversionVeto: " << obj.passConversionVeto() << 
 
    "\n\t rhoCorrRelIso: " << obj.userFloat("rhoCorrRelIso") <<
    "\n\t deltaBetaCorrRelIso: " << obj.userFloat("deltaBetaCorrRelIso") <<
 
    "\n\t dxy: " << obj.userFloat("dxy") <<
    "\n\t MVa: " << obj.electronID("mvaTrigV0") <<

    "\n\t sigmaIetaIeta: " << obj.sigmaIetaIeta() <<
    "\n\t hadronicOverEm: " << obj.hadronicOverEm() <<
    "\n\t dr03TkSumPt()/pt(): " << obj.dr03TkSumPt()/obj.pt() <<
    "\n\t dr03EcalRecHitSumEt()/pt(): " << obj.dr03EcalRecHitSumEt()/obj.pt() <<
    "\n\t dr03HcalTowerSumEt()/pt(): " << obj.dr03HcalTowerSumEt()/obj.pt() <<
    "\n\t deltaEtaSuperClusterTrackAtVtx(): " << obj.deltaEtaSuperClusterTrackAtVtx() <<
    "\n\t deltaPhiSuperClusterTrackAtVtx(): " << obj.deltaPhiSuperClusterTrackAtVtx() <<

    "\n\t gsfTrack_trackerExpectedHitsInner_numberOfHits: " << obj.userFloat("gsfTrack_trackerExpectedHitsInner_numberOfHits");

    i++;   
   }
 }
   
}


// ------------ method called once each job just before starting event loop  ------------
void 
SimpleElectronAnalyzer::beginJob()
{
}

// ------------ method called once each job just after ending the event loop  ------------
void 
SimpleElectronAnalyzer::endJob() 
{
}

// ------------ method called when starting to processes a run  ------------
void 
SimpleElectronAnalyzer::beginRun(edm::Run const&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a run  ------------
void 
SimpleElectronAnalyzer::endRun(edm::Run const&, edm::EventSetup const&)
{
}

// ------------ method called when starting to processes a luminosity block  ------------
void 
SimpleElectronAnalyzer::beginLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a luminosity block  ------------
void 
SimpleElectronAnalyzer::endLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&)
{
}

// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void
SimpleElectronAnalyzer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(SimpleElectronAnalyzer);
