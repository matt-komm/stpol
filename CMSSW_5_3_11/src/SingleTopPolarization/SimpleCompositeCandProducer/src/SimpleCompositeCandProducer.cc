// -*- C++ -*-
//
// Package:    SimpleCompositeCandProducer
// Class:      SimpleCompositeCandProducer
// 
/**\class SimpleCompositeCandProducer SimpleCompositeCandProducer.cc SingleTopPolarization/SimpleCompositeCandProducer/src/SimpleCompositeCandProducer.cc

 Description: Creates a new particle, the 4-momentum of which is the vector sum of the momenta of the input particles.

 Implementation:
     [Notes on implementation]
*/
//
// Original Author: Joosep Pata joosep.pata@cern.ch
//         Created:  Tue Oct  2 17:44:39 EEST 2012
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

#include <DataFormats/Candidate/interface/CompositeCandidate.h>
#include <DataFormats/RecoCandidate/interface/RecoCandidate.h>
#include "FWCore/Utilities/interface/InputTag.h"

#include <CommonTools/CandUtils/interface/AddFourMomenta.h>
#include <FWCore/MessageLogger/interface/MessageLogger.h>

//
// class declaration
//

class SimpleCompositeCandProducer : public edm::EDProducer {
   public:
      explicit SimpleCompositeCandProducer(const edm::ParameterSet&);
      ~SimpleCompositeCandProducer();

      static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);

   private:
      virtual void beginJob() ;
      virtual void produce(edm::Event&, const edm::EventSetup&);
      virtual void endJob() ;
      
      virtual void beginRun(edm::Run&, edm::EventSetup const&);
      virtual void endRun(edm::Run&, edm::EventSetup const&);
      virtual void beginLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&);
      virtual void endLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&);

      const std::vector<edm::InputTag> sources;

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
SimpleCompositeCandProducer::SimpleCompositeCandProducer(const edm::ParameterSet& iConfig)
: sources(iConfig.getParameter<std::vector< edm::InputTag> >("sources"))
{

   produces<std::vector<reco::CompositeCandidate> >();

   //now do what ever other initialization is needed
  
}


SimpleCompositeCandProducer::~SimpleCompositeCandProducer()
{
 
   // do anything here that needs to be done at desctruction time
   // (e.g. close files, deallocate resources etc.)

}


//
// member functions
//

// ------------ method called to produce the data  ------------
void
SimpleCompositeCandProducer::produce(edm::Event& iEvent, const edm::EventSetup& iSetup)
{
   using namespace edm;

   std::auto_ptr<std::vector<reco::CompositeCandidate> > pOut(new std::vector<reco::CompositeCandidate>());

   auto outCand = reco::CompositeCandidate();
   for (auto& source : sources) {
    Handle<View<reco::Candidate> > pIn;
    iEvent.getByLabel(source, pIn);
    int i = 0;
    for (auto& particle : *pIn) {
      LogDebug("produce()") << "Adding particle " << i << " from collection "  << source.label() << " as daughter";
      outCand.addDaughter(particle);
      i++;
    }
   }
   LogDebug("produce()") << "Adding 4-momenta of daughters";
   AddFourMomenta adder;
   adder.set(outCand);
   
   //Set the p4 manually
   //const math::PtEtaPhiMLorentzVectorD p4(0.0, 0.0, 0.0, 0.0);
   //outCand->setP4(p4);
   LogDebug("produce()") << "Particle 4-momentum: " << ") pt (" << outCand.p4().Pt() << ") eta(" << outCand.p4().Eta() << ") phi(" << outCand.p4().Phi() << ") Et" << outCand.p4().Et();
   
   pOut->push_back(outCand);
   iEvent.put(pOut);
}

// ------------ method called once each job just before starting event loop  ------------
void 
SimpleCompositeCandProducer::beginJob()
{
}

// ------------ method called once each job just after ending the event loop  ------------
void 
SimpleCompositeCandProducer::endJob() {
}

// ------------ method called when starting to processes a run  ------------
void 
SimpleCompositeCandProducer::beginRun(edm::Run&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a run  ------------
void 
SimpleCompositeCandProducer::endRun(edm::Run&, edm::EventSetup const&)
{
}

// ------------ method called when starting to processes a luminosity block  ------------
void 
SimpleCompositeCandProducer::beginLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a luminosity block  ------------
void 
SimpleCompositeCandProducer::endLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&)
{
}

// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void
SimpleCompositeCandProducer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(SimpleCompositeCandProducer);
