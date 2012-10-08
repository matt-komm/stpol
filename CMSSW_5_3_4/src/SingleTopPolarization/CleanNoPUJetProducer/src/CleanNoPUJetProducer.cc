// -*- C++ -*-
//
// Package:    CleanNoPUJetProducer
// Class:      CleanNoPUJetProducer
// 
/**\class CleanNoPUJetProducer CleanNoPUJetProducer.cc SingleTopPolarization/CleanNoPUJetProducer/src/CleanNoPUJetProducer.cc

 Description: [one line class summary]

 Implementation:
     [Notes on implementation]
*/
//
// Original Author:  Joosep Pata
//         Created:  Sun Oct  7 17:53:17 EEST 2012
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

#include "FWCore/Utilities/interface/InputTag.h"
#include "DataFormats/PatCandidates/interface/Jet.h"
#include "FWCore/MessageLogger/interface/MessageLogger.h"
#include <TMath.h>
#include "CMGTools/External/interface/PileupJetIdentifier.h"

//
// class declaration
//

class CleanNoPUJetProducer : public edm::EDProducer {
   public:
      explicit CleanNoPUJetProducer(const edm::ParameterSet&);
      ~CleanNoPUJetProducer();

      static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);

   private:
      virtual void beginJob() ;
      virtual void produce(edm::Event&, const edm::EventSetup&);
      virtual void endJob() ;
      
      virtual void beginRun(edm::Run&, edm::EventSetup const&);
      virtual void endRun(edm::Run&, edm::EventSetup const&);
      virtual void beginLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&);
      virtual void endLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&);

      const edm::InputTag jetSrc;
      const edm::InputTag jetPUIdMVASrc;
      const edm::InputTag jetPUIdFlagSrc;

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
CleanNoPUJetProducer::CleanNoPUJetProducer(const edm::ParameterSet& iConfig)
: jetSrc(iConfig.getParameter<edm::InputTag>("jetSrc"))
, jetPUIdMVASrc(iConfig.getParameter<edm::InputTag>("PUidMVA"))
, jetPUIdFlagSrc(iConfig.getParameter<edm::InputTag>("PUidFlag"))
{
  produces<std::vector<pat::Jet> >();
   //register your products
/* Examples
   produces<ExampleData2>();

   //if do put with a label
   produces<ExampleData2>("label");
 
   //if you want to put into the Run
   produces<ExampleData2,InRun>();
*/
   //now do what ever other initialization is needed
  
}


CleanNoPUJetProducer::~CleanNoPUJetProducer()
{
 
   // do anything here that needs to be done at desctruction time
   // (e.g. close files, deallocate resources etc.)

}


//
// member functions
//

// ------------ method called to produce the data  ------------
void
CleanNoPUJetProducer::produce(edm::Event& iEvent, const edm::EventSetup& iSetup)
{
   using namespace edm;
   Handle<View<pat::Jet> > jets;
   Handle<ValueMap<float> > mvaIDs;
   Handle<ValueMap<int> > flags;
   iEvent.getByLabel(jetSrc, jets);
   iEvent.getByLabel(jetPUIdMVASrc, mvaIDs);
   iEvent.getByLabel(jetPUIdFlagSrc, flags);

   std::auto_ptr<std::vector<pat::Jet> > outJets(new std::vector<pat::Jet>());


   for ( uint i = 0; i < jets->size(); ++i ) {
    const pat::Jet& jet = jets->at(i);

    pat::Jet* outJet = jet.clone();
    float mva = (*mvaIDs)[jets->refAt(i)];
    int idflag = (*flags)[jets->refAt(i)];
    LogDebug("produce()") << "jet pt: " << jet.pt() << " eta: " << jet.eta() << " mvaID: " << mva;
    if( PileupJetIdentifier::passJetId( idflag, PileupJetIdentifier::kLoose ) ) {
      LogDebug("produce()") << " pass loose wp";
      outJets->push_back(*outJet);
    } else {
      LogDebug("produce()") << " fail loose wp";
    }
   }
   iEvent.put(outJets);
/* This is an event example
   //Read 'ExampleData' from the Event
   Handle<ExampleData> pIn;
   iEvent.getByLabel("example",pIn);

   //Use the ExampleData to create an ExampleData2 which 
   // is put into the Event
   std::auto_ptr<ExampleData2> pOut(new ExampleData2(*pIn));
   iEvent.put(pOut);
*/

/* this is an EventSetup example
   //Read SetupData from the SetupRecord in the EventSetup
   ESHandle<SetupData> pSetup;
   iSetup.get<SetupRecord>().get(pSetup);
*/
 
}

// ------------ method called once each job just before starting event loop  ------------
void 
CleanNoPUJetProducer::beginJob()
{
}

// ------------ method called once each job just after ending the event loop  ------------
void 
CleanNoPUJetProducer::endJob() {
}

// ------------ method called when starting to processes a run  ------------
void 
CleanNoPUJetProducer::beginRun(edm::Run&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a run  ------------
void 
CleanNoPUJetProducer::endRun(edm::Run&, edm::EventSetup const&)
{
}

// ------------ method called when starting to processes a luminosity block  ------------
void 
CleanNoPUJetProducer::beginLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a luminosity block  ------------
void 
CleanNoPUJetProducer::endLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&)
{
}

// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void
CleanNoPUJetProducer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(CleanNoPUJetProducer);
