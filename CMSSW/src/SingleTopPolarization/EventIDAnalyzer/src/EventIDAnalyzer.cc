// -*- C++ -*-
//
// Package:    EventIDAnalyzer
// Class:      EventIDAnalyzer
// 
/**\class EventIDAnalyzer EventIDAnalyzer.cc SingleTopPolarization/EventIDAnalyzer/src/EventIDAnalyzer.cc

 Description: [one line class summary]

 Implementation:
     [Notes on implementation]
*/
//
// Original Author:  Joosep Pata
//         Created:  Tue Oct  9 09:30:37 EEST 2012
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
#include "FWCore/MessageLogger/interface/MessageLogger.h"

class EventIDAnalyzer : public edm::EDAnalyzer {
   public:
      explicit EventIDAnalyzer(const edm::ParameterSet&);
      ~EventIDAnalyzer();

      static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);


   private:
      virtual void beginJob() ;
      virtual void analyze(const edm::Event&, const edm::EventSetup&);
      virtual void endJob() ;

      virtual void beginRun(edm::Run const&, edm::EventSetup const&);
      virtual void endRun(edm::Run const&, edm::EventSetup const&);
      virtual void beginLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&);
      virtual void endLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&);

      const std::string name;

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
EventIDAnalyzer::EventIDAnalyzer(const edm::ParameterSet& iConfig)
: name(iConfig.getUntrackedParameter<std::string>("name", ""))

{
   //now do what ever initialization is needed

}


EventIDAnalyzer::~EventIDAnalyzer()
{
 
   // do anything here that needs to be done at desctruction time
   // (e.g. close files, deallocate resources etc.)

}


//
// member functions
//

// ------------ method called for each event  ------------
void
EventIDAnalyzer::analyze(const edm::Event& iEvent, const edm::EventSetup& iSetup)
{
   using namespace edm;

   edm::LogInfo("analyze") << name << " ID event: " << iEvent.id().event() << " lumi: " << iEvent.id().luminosityBlock() << " run: " << iEvent.id().run();
}


// ------------ method called once each job just before starting event loop  ------------
void 
EventIDAnalyzer::beginJob()
{
}

// ------------ method called once each job just after ending the event loop  ------------
void 
EventIDAnalyzer::endJob() 
{
}

// ------------ method called when starting to processes a run  ------------
void 
EventIDAnalyzer::beginRun(edm::Run const&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a run  ------------
void 
EventIDAnalyzer::endRun(edm::Run const&, edm::EventSetup const&)
{
}

// ------------ method called when starting to processes a luminosity block  ------------
void 
EventIDAnalyzer::beginLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a luminosity block  ------------
void 
EventIDAnalyzer::endLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&)
{
}

// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void
EventIDAnalyzer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(EventIDAnalyzer);
