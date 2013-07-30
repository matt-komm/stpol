// -*- C++ -*-
//
// Package:    PUWeightProducer
// Class:      PUWeightProducer
// 
/**\class PUWeightProducer PUWeightProducer.cc SingleTopPolarization/PUWeightProducer/src/PUWeightProducer.cc

 Description: [one line class summary]

 Implementation:
     [Notes on implementation]
*/
//
// Original Author:  Joosep Pata
//         Created:  Tue Feb 12 11:17:18 EET 2013
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
#include "FWCore/MessageLogger/interface/MessageLogger.h"
#include "SimDataFormats/PileupSummaryInfo/interface/PileupSummaryInfo.h"
#include "PhysicsTools/Utilities/interface/LumiReWeighting.h"
#include "TMath.h"

class PUWeightProducer : public edm::EDProducer {
   public:
      explicit PUWeightProducer(const edm::ParameterSet&);
      ~PUWeightProducer();

      static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);

   private:
      virtual void beginJob() ;
      virtual void produce(edm::Event&, const edm::EventSetup&);
      virtual void endJob() ;
      
      virtual void beginRun(edm::Run&, edm::EventSetup const&);
      virtual void endRun(edm::Run&, edm::EventSetup const&);
      virtual void beginLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&);
      virtual void endLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&);
      const unsigned int maxVertices;
      std::vector<double> srcDistr;
      std::vector<double> destDistr;
      edm::LumiReWeighting* reweighter;
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
PUWeightProducer::PUWeightProducer(const edm::ParameterSet& iConfig)
: maxVertices(iConfig.getParameter<unsigned int>("maxVertices"))
, srcDistr(iConfig.getParameter<std::vector<double>>("srcDistribution"))
, destDistr(iConfig.getParameter<std::vector<double>>("destDistribution"))
{
   srcDistr.resize(maxVertices);
   destDistr.resize(maxVertices);
   std::vector<float> _srcDistr;
   std::vector<float> _destDistr;
   for (unsigned int i=0;i<maxVertices;i++) {
       _srcDistr.push_back((float)srcDistr[i]);
       _destDistr.push_back((float)destDistr[i]);
   }

   produces<double>("PUWeightNtrue");
   produces<double>("PUWeightN0");
   produces<double>("nVertices0");
   produces<double>("nVerticesBXPlus1");
   produces<double>("nVerticesBXMinus1");
   produces<double>("nVerticesTrue");
   reweighter = new edm::LumiReWeighting(_srcDistr, _destDistr);
}


PUWeightProducer::~PUWeightProducer()
{
}


//
// member functions
//

// ------------ method called to produce the data  ------------
void
PUWeightProducer::produce(edm::Event& iEvent, const edm::EventSetup& iSetup)
{
   using namespace edm;
   
   Handle<std::vector< PileupSummaryInfo > > PupInfo;
   iEvent.getByLabel(edm::InputTag("addPileupInfo"), PupInfo);
   std::vector<PileupSummaryInfo>::const_iterator PVI;
   
   float n0 = TMath::QuietNaN(); 
   float ntrue = TMath::QuietNaN();
   float nm1 = TMath::QuietNaN();
   float np1 = TMath::QuietNaN();
   int nPUs = 0;
   for(PVI = PupInfo->begin(); PVI != PupInfo->end(); ++PVI) {
      int BX = PVI->getBunchCrossing();
      nPUs++; 
      if(BX == 0) {
        n0 = PVI->getPU_NumInteractions();
        ntrue = PVI->getTrueNumInteractions();
        LogDebug("produce()") << "true num int = " << ntrue;
      }
      else if(BX == 1) {
          np1 = PVI->getPU_NumInteractions();
      }
      else if(BX == -1) {
          nm1 = PVI->getPU_NumInteractions();
      }
   }
   
   double puWeight_n0 = TMath::QuietNaN(); 
   double puWeight_ntrue = TMath::QuietNaN(); 
   if (nPUs>0 && n0>0) {
      puWeight_n0 = reweighter->weight(n0);
   }
   if (nPUs>0 && ntrue>0) {
      puWeight_ntrue = reweighter->weight(ntrue);
   }
   LogDebug("produce()") << "calculated PU weight = " << puWeight_n0;
   iEvent.put(std::auto_ptr<double>(new double(n0)), "nVertices0");   
   iEvent.put(std::auto_ptr<double>(new double(np1)), "nVerticesBXPlus1");   
   iEvent.put(std::auto_ptr<double>(new double(nm1)), "nVerticesBXMinus1");   
   iEvent.put(std::auto_ptr<double>(new double(ntrue)), "nVerticesTrue");   
   iEvent.put(std::auto_ptr<double>(new double(puWeight_ntrue)), "PUWeightNtrue");   
   iEvent.put(std::auto_ptr<double>(new double(puWeight_n0)), "PUWeightN0");   

 
}

// ------------ method called once each job just before starting event loop  ------------
void 
PUWeightProducer::beginJob()
{
}

// ------------ method called once each job just after ending the event loop  ------------
void 
PUWeightProducer::endJob() {
}

// ------------ method called when starting to processes a run  ------------
void 
PUWeightProducer::beginRun(edm::Run&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a run  ------------
void 
PUWeightProducer::endRun(edm::Run&, edm::EventSetup const&)
{
}

// ------------ method called when starting to processes a luminosity block  ------------
void 
PUWeightProducer::beginLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a luminosity block  ------------
void 
PUWeightProducer::endLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&)
{
}

// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void
PUWeightProducer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(PUWeightProducer);
