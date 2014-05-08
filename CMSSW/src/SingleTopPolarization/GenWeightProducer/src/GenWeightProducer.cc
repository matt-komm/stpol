// -*- C++ -*-
//
// Package:    GenWeightProducer
// Class:      GenWeightProducer
// 
/**\class GenWeightProducer GenWeightProducer.cc SingleTopPolarization/GenWeightProducer/src/GenWeightProducer.cc

 Description: Extracts the gen weight from the GenEventInfoProduct structure and puts it into the event as a simple double

 Implementation:
     [Notes on implementation]
*/
//
// Original Author:  Joosep Pata
//         Created:  Thu Nov 28 21:13:42 EET 2013
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

#include <SimDataFormats/GeneratorProducts/interface/GenEventInfoProduct.h>

#include <TMath.h>

class GenWeightProducer : public edm::EDProducer {
   public:
      explicit GenWeightProducer(const edm::ParameterSet&);
      ~GenWeightProducer();

      static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);

   private:
      virtual void beginJob() ;
      virtual void produce(edm::Event&, const edm::EventSetup&);
      virtual void endJob() ;
      
      virtual void beginRun(edm::Run&, edm::EventSetup const&);
      virtual void endRun(edm::Run&, edm::EventSetup const&);
      virtual void beginLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&);
      virtual void endLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&);
      const edm::InputTag genWeightSrc;
};

GenWeightProducer::GenWeightProducer(const edm::ParameterSet& iConfig)
: genWeightSrc(edm::InputTag("generator"))
{
   produces<double>("w");
  
}


GenWeightProducer::~GenWeightProducer()
{
}

// ------------ method called to produce the data  ------------
void
GenWeightProducer::produce(edm::Event& iEvent, const edm::EventSetup& iSetup)
{
    edm::Handle<GenEventInfoProduct> genEventInfo;
    iEvent.getByLabel(genWeightSrc, genEventInfo);

    double w = TMath::QuietNaN();
    if (genEventInfo.isValid())
        w = genEventInfo->weight();
   
    std::auto_ptr<double> pOut(new double(w));
   iEvent.put(pOut, "w");
}

// ------------ method called once each job just before starting event loop  ------------
void 
GenWeightProducer::beginJob()
{
}

// ------------ method called once each job just after ending the event loop  ------------
void 
GenWeightProducer::endJob() {
}

// ------------ method called when starting to processes a run  ------------
void 
GenWeightProducer::beginRun(edm::Run&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a run  ------------
void 
GenWeightProducer::endRun(edm::Run&, edm::EventSetup const&)
{
}

// ------------ method called when starting to processes a luminosity block  ------------
void 
GenWeightProducer::beginLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a luminosity block  ------------
void 
GenWeightProducer::endLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&)
{
}

// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void
GenWeightProducer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(GenWeightProducer);
