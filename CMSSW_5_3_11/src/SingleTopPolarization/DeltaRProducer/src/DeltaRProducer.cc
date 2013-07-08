// -*- C++ -*-
//
// Package:    DeltaRProducer
// Class:      DeltaRProducer
// 
/**\class DeltaRProducer DeltaRProducer.cc SingleTopPolarization/DeltaRProducer/src/DeltaRProducer.cc

 Description: [one line class summary]

 Implementation:
     [Notes on implementation]
*/
//
// Original Author:  Andres Tiko
//         Created:  K jaan  16 17:12:49 EET 2013
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

#include "DataFormats/PatCandidates/interface/Jet.h"
#include "FWCore/Utilities/interface/InputTag.h"

#include <DataFormats/PatCandidates/interface/Muon.h>
#include "FWCore/MessageLogger/interface/MessageLogger.h"
#include <TMath.h>
#include <Math/GenVector/VectorUtil.h>

//
// class declaration
//

class DeltaRProducer : public edm::EDProducer {
   public:
      explicit DeltaRProducer(const edm::ParameterSet&);
      ~DeltaRProducer();

      static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);

   private:
      virtual void beginJob() ;
      virtual void produce(edm::Event&, const edm::EventSetup&);
      virtual void endJob() ;
      
      virtual void beginRun(edm::Run&, edm::EventSetup const&);
      virtual void endRun(edm::Run&, edm::EventSetup const&);
      virtual void beginLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&);
      virtual void endLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&);

      // ----------member data ---------------------------
      const edm::InputTag jetSrc;
      const edm::InputTag leptonSrc;
      //std::string result_;
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
DeltaRProducer::DeltaRProducer(const edm::ParameterSet& iConfig)
: jetSrc(iConfig.getParameter<edm::InputTag>("jetSrc"))
, leptonSrc(iConfig.getParameter<edm::InputTag>("leptonSrc"))
{
   //produces<edm::ValueMap<double> >().setBranchAlias("deltaR")
   //produces<std::vector<pat::Muon> >();
   produces<std::vector<pat::Jet> >();
   //now do what ever other initialization is needed
  
}


DeltaRProducer::~DeltaRProducer()
{
 
   // do anything here that needs to be done at desctruction time
   // (e.g. close files, deallocate resources etc.)

}


//
// member functions
//

// ------------ method called to produce the data  ------------
void
DeltaRProducer::produce(edm::Event& iEvent, const edm::EventSetup& iSetup)
{
   using namespace edm;

   Handle<View<reco::Candidate> > leptons;
   Handle<std::vector<pat::Jet> > jets;
   iEvent.getByLabel(leptonSrc, leptons);   
   iEvent.getByLabel(jetSrc, jets);

   std::auto_ptr<std::vector<pat::Jet> > outJets(new std::vector<pat::Jet>());
   for ( uint i = 0; i < jets->size(); ++i ) {
      const pat::Jet& jet = jets->at(i);

      float deltaR;
      if (leptons->size()==1){
         const reco::Candidate& lepton = leptons->at(0);

         deltaR =  ROOT::Math::VectorUtil::DeltaR(lepton.p4(), jet.p4());
         outJets->push_back(jet);

         pat::Jet& jet = outJets->back();
         jet.addUserFloat("deltaR", deltaR); 
      }
   }
   iEvent.put(outJets);
}

// ------------ method called once each job just before starting event loop  ------------
void 
DeltaRProducer::beginJob()
{
}

// ------------ method called once each job just after ending the event loop  ------------
void 
DeltaRProducer::endJob() {
}

// ------------ method called when starting to processes a run  ------------
void 
DeltaRProducer::beginRun(edm::Run&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a run  ------------
void 
DeltaRProducer::endRun(edm::Run&, edm::EventSetup const&)
{
}

// ------------ method called when starting to processes a luminosity block  ------------
void 
DeltaRProducer::beginLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a luminosity block  ------------
void 
DeltaRProducer::endLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&)
{
}

// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void
DeltaRProducer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(DeltaRProducer);
