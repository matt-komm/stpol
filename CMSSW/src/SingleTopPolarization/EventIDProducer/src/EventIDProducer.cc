// -*- C++ -*-
//
// Package:    EventIDProducer
// Class:      EventIDProducer
// 
/**\class EventIDProducer EventIDProducer.cc SingleTopPolarization/EventIDProducer/src/EventIDProducer.cc

 Description: [one line class summary]

 Implementation:
     [Notes on implementation]
*/
//
// Original Author:  Joosep Pata
//         Created:  Tue Feb 12 12:46:22 EET 2013
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


//
// class declaration
//

class EventIDProducer : public edm::EDProducer {
   public:
      explicit EventIDProducer(const edm::ParameterSet&);
      ~EventIDProducer();

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
EventIDProducer::EventIDProducer(const edm::ParameterSet& iConfig)
{
   produces<int>("eventId");
   produces<int>("runId");
   produces<int>("lumiId");
}


EventIDProducer::~EventIDProducer()
{
}

void
EventIDProducer::produce(edm::Event& iEvent, const edm::EventSetup& iSetup)
{
   using namespace edm;
   int runId = iEvent.eventAuxiliary().run();
   int lumiId = iEvent.eventAuxiliary().luminosityBlock();
   int eventId = iEvent.eventAuxiliary().event();
   iEvent.put(std::auto_ptr<int>(new int(eventId)), "eventId");   
   iEvent.put(std::auto_ptr<int>(new int(runId)), "runId");   
   iEvent.put(std::auto_ptr<int>(new int(lumiId)), "lumiId");   
}

// ------------ method called once each job just before starting event loop  ------------
void 
EventIDProducer::beginJob()
{
}

// ------------ method called once each job just after ending the event loop  ------------
void 
EventIDProducer::endJob() {
}

// ------------ method called when starting to processes a run  ------------
void 
EventIDProducer::beginRun(edm::Run&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a run  ------------
void 
EventIDProducer::endRun(edm::Run&, edm::EventSetup const&)
{
}

// ------------ method called when starting to processes a luminosity block  ------------
void 
EventIDProducer::beginLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a luminosity block  ------------
void 
EventIDProducer::endLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&)
{
}

// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void
EventIDProducer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(EventIDProducer);
