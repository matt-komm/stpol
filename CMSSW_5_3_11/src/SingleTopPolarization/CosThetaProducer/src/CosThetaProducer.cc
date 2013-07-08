// -*- C++ -*-
//
// Package:    CosThetaProducer
// Class:      CosThetaProducer
// 
/**\class CosThetaProducer CosThetaProducer.cc SingleTopPolarization/CosThetaProducer/src/CosThetaProducer.cc

 Description: [one line class summary]

 Implementation:
     [Notes on implementation]
*/
//
// Original Author:  
//         Created:  Wed Oct  3 14:29:22 EEST 2012
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
#include <DataFormats/Candidate/interface/Candidate.h> 
#include "FWCore/MessageLogger/interface/MessageLogger.h"

#include "FWCore/Utilities/interface/InputTag.h"

#include "Math/GenVector/VectorUtil.h"
#include <TMath.h>

//
// class declaration
//

class CosThetaProducer : public edm::EDProducer {
   public:
      explicit CosThetaProducer(const edm::ParameterSet&);
      ~CosThetaProducer();

      static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);

   private:
      virtual void beginJob() ;
      virtual void produce(edm::Event&, const edm::EventSetup&);
      virtual void endJob() ;
      
      virtual void beginRun(edm::Run&, edm::EventSetup const&);
      virtual void endRun(edm::Run&, edm::EventSetup const&);
      virtual void beginLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&);
      virtual void endLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&);

      const edm::InputTag leptonSrc;
      const edm::InputTag topSrc;
      const edm::InputTag jetSrc;

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
CosThetaProducer::CosThetaProducer(const edm::ParameterSet& iConfig)
: leptonSrc(iConfig.getParameter<edm::InputTag>("leptonSrc"))
, topSrc(iConfig.getParameter<edm::InputTag>("topSrc"))
, jetSrc(iConfig.getParameter<edm::InputTag>("jetSrc"))
{

  produces<double>("cosThetaLightJet");
  produces<double>("cosThetaEtaBeamline");
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


CosThetaProducer::~CosThetaProducer()
{
 
   // do anything here that needs to be done at desctruction time
   // (e.g. close files, deallocate resources etc.)

}


//
// member functions
//

// ------------ method called to produce the data  ------------
void
CosThetaProducer::produce(edm::Event& iEvent, const edm::EventSetup& iSetup)
{
   using namespace edm;

   double cosThetaLightJet = TMath::QuietNaN();
   double cosThetaEtaBeamline = TMath::QuietNaN();

   Handle<View<reco::Candidate> > tops;
   Handle<View<reco::Candidate> > jets;
   Handle<View<reco::Candidate> > leptons;
   iEvent.getByLabel(topSrc, tops);
   iEvent.getByLabel(jetSrc, jets);
   iEvent.getByLabel(leptonSrc, leptons);
   if (tops->size() > 0 && jets->size() > 0 && leptons->size() > 0) {
    if (tops->size()>1 || jets->size() > 1 || leptons->size() > 1) {
      LogError("produce()") << "Number of items in input collections is ambigous: tops " << tops->size() << " jets " << jets->size() << " leptons " << leptons->size();
    }
    const reco::Candidate& top = tops->at(0);
    const reco::Candidate& jet = jets->at(0);
    const reco::Candidate& lepton = leptons->at(0);

    ROOT::Math::LorentzVector<ROOT::Math::PxPyPzE4D<double> > boostedLeptonVec = ROOT::Math::VectorUtil::boost(lepton.p4(), top.p4().BoostToCM());
    ROOT::Math::LorentzVector<ROOT::Math::PxPyPzE4D<double> > boostedJetVec = ROOT::Math::VectorUtil::boost(jet.p4(), top.p4().BoostToCM());

    cosThetaLightJet = ROOT::Math::VectorUtil::CosTheta(boostedJetVec.Vect(), boostedLeptonVec.Vect());

    LogDebug("produce()") << "cosThetaLightJet: " << cosThetaLightJet;
    LogDebug("produce()") << "cosThetaEtaBeamline: " << cosThetaEtaBeamline;
   }
   else {
    LogError("produce()") << "Number of items in input collections is too small: tops " << tops->size() << " jets " << jets->size() << " leptons " << leptons->size();
   }

   std::auto_ptr<double> pCosThetaLJ(new double(cosThetaLightJet));
   iEvent.put(pCosThetaLJ, "cosThetaLightJet");
   std::auto_ptr<double> pCosThetaEtaBL(new double(cosThetaEtaBeamline));
   iEvent.put(pCosThetaEtaBL, "cosThetaEtaBeamline");

   // math::PtEtaPhiELorentzVector boostedJet = ROOT::Math::VectorUtil::boost(jet, top.BoostToCM());

   // return  ROOT::Math::VectorUtil::CosTheta(boostedJet.Vect(), boostedLepton.Vect());
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
CosThetaProducer::beginJob()
{
}

// ------------ method called once each job just after ending the event loop  ------------
void 
CosThetaProducer::endJob() {
}

// ------------ method called when starting to processes a run  ------------
void 
CosThetaProducer::beginRun(edm::Run&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a run  ------------
void 
CosThetaProducer::endRun(edm::Run&, edm::EventSetup const&)
{
}

// ------------ method called when starting to processes a luminosity block  ------------
void 
CosThetaProducer::beginLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a luminosity block  ------------
void 
CosThetaProducer::endLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&)
{
}

// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void
CosThetaProducer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(CosThetaProducer);
