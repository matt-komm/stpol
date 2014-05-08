// -*- C++ -*-
//
// Package:    EventDoubleFilter
// Class:      EventDoubleFilter
// 
/**\class EventDoubleFilter EventDoubleFilter.cc SingleTopPolarization/EventDoubleFilter/src/EventDoubleFilter.cc

 Description: [one line class summary]

 Implementation:
     [Notes on implementation]
*/
//
// Original Author:  
//         Created:  Mon Oct  1 16:45:29 EEST 2012
// $Id$
//
//


// system include files
#include <memory>

// user include files
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/EDFilter.h"

#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/Utilities/interface/InputTag.h"
#include "FWCore/MessageLogger/interface/MessageLogger.h"

//
// class declaration
//

class EventDoubleFilter : public edm::EDFilter {
   public:
      explicit EventDoubleFilter(const edm::ParameterSet&);
      ~EventDoubleFilter();

      static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);

   private:
      virtual void beginJob() ;
      virtual bool filter(edm::Event&, const edm::EventSetup&);
      virtual void endJob() ;
      
      virtual bool beginRun(edm::Run&, edm::EventSetup const&);
      virtual bool endRun(edm::Run&, edm::EventSetup const&);
      virtual bool beginLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&);
      virtual bool endLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&);

      edm::InputTag src;
      float val_min;
      float val_max;

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
EventDoubleFilter::EventDoubleFilter(const edm::ParameterSet& iConfig)
{
  val_min = (float)iConfig.getParameter<double>("min");
  val_max = (float)iConfig.getParameter<double>("max");
  src = iConfig.getParameter<edm::InputTag>("src");
   //now do what ever initialization is needed

}


EventDoubleFilter::~EventDoubleFilter()
{
 
   // do anything here that needs to be done at desctruction time
   // (e.g. close files, deallocate resources etc.)

}


//
// member functions
//

// ------------ method called on each new Event  ------------
bool
EventDoubleFilter::filter(edm::Event& iEvent, const edm::EventSetup& iSetup)
{
   using namespace edm;
   Handle<double> pIn;
   iEvent.getByLabel(src,pIn);

   if ((*pIn) < val_min) {
    LogDebug("filter()") << src.label() << " < " << val_min << ", vetoing";
    return false;
   }
   else if ((*pIn) > val_max) {
    LogDebug("filter()") << src.label() << " > " << val_max << ", vetoing";
    return false;
   }
   else {
    LogDebug("filter()") << src.label() << " > " << val_min << " && " << src.label() << " < " << val_max << ", allowing";
    return true;
   }

   return true;
}

// ------------ method called once each job just before starting event loop  ------------
void 
EventDoubleFilter::beginJob()
{
}

// ------------ method called once each job just after ending the event loop  ------------
void 
EventDoubleFilter::endJob() {
}

// ------------ method called when starting to processes a run  ------------
bool 
EventDoubleFilter::beginRun(edm::Run&, edm::EventSetup const&)
{ 
  return true;
}

// ------------ method called when ending the processing of a run  ------------
bool 
EventDoubleFilter::endRun(edm::Run&, edm::EventSetup const&)
{
  return true;
}

// ------------ method called when starting to processes a luminosity block  ------------
bool 
EventDoubleFilter::beginLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&)
{
  return true;
}

// ------------ method called when ending the processing of a luminosity block  ------------
bool 
EventDoubleFilter::endLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&)
{
  return true;
}

// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void
EventDoubleFilter::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);
}
//define this as a plug-in
DEFINE_FWK_MODULE(EventDoubleFilter);
