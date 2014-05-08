// -*- C++ -*-
//
// Package:    CandTransverseMassProducer
// Class:      CandTransverseMassProducer
// 
/**\class CandTransverseMassProducer CandTransverseMassProducer.cc SingleTopPolarization/CandTransverseMassProducer/src/CandTransverseMassProducer.cc

 Description: [one line class summary]

 Implementation:
     [Notes on implementation]
*/
//
// Original Author:  
//         Created:  Mon Oct  1 17:15:15 EEST 2012
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
#include "DataFormats/RecoCandidate/interface/RecoCandidate.h"
#include "FWCore/Utilities/interface/InputTag.h"

#include <TMath.h>
#include "FWCore/ParameterSet/interface/ParameterSet.h"

//
// class declaration
//

class CandTransverseMassProducer : public edm::EDProducer {
   public:
      explicit CandTransverseMassProducer(const edm::ParameterSet&);
      ~CandTransverseMassProducer();

      static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);

   private:
      virtual void beginJob() ;
      virtual void produce(edm::Event&, const edm::EventSetup&);
      virtual void endJob() ;
      
      virtual void beginRun(edm::Run&, edm::EventSetup const&);
      virtual void endRun(edm::Run&, edm::EventSetup const&);
      virtual void beginLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&);
      virtual void endLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&);

      const std::vector<std::string> collections;


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
CandTransverseMassProducer::CandTransverseMassProducer(const edm::ParameterSet& iConfig)
: collections(iConfig.getUntrackedParameter<std::vector<std::string> >("collections"))
{
   //register your products
   produces<double>();
   LogDebug("constructor") << "Using " << collections.size() << " collections";

   //now do what ever other initialization is needed
  
}


CandTransverseMassProducer::~CandTransverseMassProducer()
{
 
   // do anything here that needs to be done at desctruction time
   // (e.g. close files, deallocate resources etc.)

}


//
// member functions
//

// ------------ method called to produce the data  ------------
void
CandTransverseMassProducer::produce(edm::Event& iEvent, const edm::EventSetup& iSetup)
{
   using namespace edm;

   double sumPx = 0;
   double sumPy = 0;
   double sumPt = 0;

   for (auto& coll : collections) {
    Handle<View<reco::Candidate> > cands;
    iEvent.getByLabel(coll, cands);
    LogDebug("produce()") << "collection " << coll << "(" << cands->size() << ")";


    for(auto& c : *cands) {
      LogDebug("produce()") << "Adding vector: pt " << c.p4().Pt() << " px " << c.p4().Px() << " py " << c.p4().Py();
      sumPx += c.p4().Px();
      sumPy += c.p4().Py();
      sumPt += c.p4().Pt();
    }
   }

   double mt2 = (double)TMath::Power(sumPt, 2) - (double)TMath::Power(sumPx, 2) - (double)TMath::Power(sumPy, 2);
   if (mt2<0.0) {
    LogError("produce()") << "Transverse mass squared is negative, mt will be nan! Probably you only used 1 vector.";
   }
   std::auto_ptr<double> mt( new double(TMath::Sqrt(mt2)) );
   LogDebug("produce()") << "Calculated mt2: " << mt2;
   iEvent.put(mt);


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
CandTransverseMassProducer::beginJob()
{
}

// ------------ method called once each job just after ending the event loop  ------------
void 
CandTransverseMassProducer::endJob() {
}

// ------------ method called when starting to processes a run  ------------
void 
CandTransverseMassProducer::beginRun(edm::Run&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a run  ------------
void 
CandTransverseMassProducer::endRun(edm::Run&, edm::EventSetup const&)
{
}

// ------------ method called when starting to processes a luminosity block  ------------
void 
CandTransverseMassProducer::beginLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a luminosity block  ------------
void 
CandTransverseMassProducer::endLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&)
{
}

// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void
CandTransverseMassProducer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(CandTransverseMassProducer);
