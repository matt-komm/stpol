// -*- C++ -*-
//
// Package:    MuonEfficiencyProducer
// Class:      MuonEfficiencyProducer
// 
/**\class MuonEfficiencyProducer MuonEfficiencyProducer.cc SingleTopPolarization/MuonEfficiencyProducer/src/MuonEfficiencyProducer.cc

 Description: [one line class summary]

 Implementation:
     [Notes on implementation]
*/
//
// Original Author:  Andres Tiko
//         Created:  R märts  8 18:40:17 EET 2013
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

#include "FWCore/MessageLogger/interface/MessageLogger.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"

#include <DataFormats/PatCandidates/interface/Muon.h>

//
// class declaration
//

class MuonEfficiencyProducer : public edm::EDProducer {
   public:
      explicit MuonEfficiencyProducer(const edm::ParameterSet&);
      ~MuonEfficiencyProducer();

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
      const edm::InputTag src;
      const std::string dataRun;
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
MuonEfficiencyProducer::MuonEfficiencyProducer(const edm::ParameterSet& iConfig)
: src(iConfig.getParameter<edm::InputTag>("src"))
, dataRun(iConfig.getParameter<std::string>("dataRun"))
{
   edm::LogInfo("constructor") << "dataRun=" << dataRun;
   produces<double>("muonIDWeight");
   produces<double>("muonIDWeightUp");
   produces<double>("muonIDWeightDown");
   produces<double>("muonIsoWeight");
   produces<double>("muonIsoWeightUp");
   produces<double>("muonIsoWeightDown");   
   produces<double>("muonTriggerWeight");
   produces<double>("muonTriggerWeightUp");
   produces<double>("muonTriggerWeightDown");   
}


MuonEfficiencyProducer::~MuonEfficiencyProducer()
{
 
   // do anything here that needs to be done at desctruction time
   // (e.g. close files, deallocate resources etc.)

}


//
// member functions
//

// ------------ method called to produce the data  ------------
void
MuonEfficiencyProducer::produce(edm::Event& iEvent, const edm::EventSetup& iSetup)
{
   using namespace edm;
   float weightID = TMath::QuietNaN();
   float weightIDUp = TMath::QuietNaN();
   float weightIDDown = TMath::QuietNaN();
   float weightIso = TMath::QuietNaN();
   float weightIsoUp = TMath::QuietNaN();
   float weightIsoDown = TMath::QuietNaN();
   float weightTrig = TMath::QuietNaN();
   float weightTrigUp = TMath::QuietNaN();
   float weightTrigDown = TMath::QuietNaN();

   Handle<View<reco::Candidate> > muons;
   iEvent.getByLabel(src, muons);
   if (muons->size()>1)
       LogError("muon weights") << "Muon weights are only defined for a single-muon event, but you have " << muons->size();

   for ( uint i = 0; i < 1; ++i ) {
      const pat::Muon& muon = (pat::Muon&)muons->at(i);
   
      LogDebug("eta ") << muon.eta() << std::endl;
      LogDebug("iso ") << muon.userFloat("deltaBetaCorrRelIso") << std::endl;
      
      if(fabs(muon.eta())<0.9){
         weightID = 0.9939;
         weightIDUp = weightID + 0.0002;
         weightIDDown = weightID - 0.0002;
         if(muon.userFloat("deltaBetaCorrRelIso")<0.12  || muon.userFloat("deltaBetaCorrRelIso")>0.2){
            weightIso = 1.0004;
            weightIsoUp = weightIso + 0.0002;
            weightIsoDown = weightIso - 0.0002;
         }else if(muon.userFloat("deltaBetaCorrRelIso")<0.2){
            weightIso = 0.9999;
            weightIsoUp = weightIso + 0.0001;
            weightIsoDown = weightIso - 0.0001;
         }

         //https://indico.cern.ch/getFile.py/access?contribId=2&resId=0&materialId=slides&confId=228197
         if (dataRun == "RunA") {
             weightTrig = 0.9560;
             float err = 0.0008;
             weightTrigUp = weightTrig + err;
             weightTrigDown = weightTrig - err; 
         }
         else if(dataRun == "RunB") {
             weightTrig = 0.9798;
             float err = 0.0004;
             weightTrigUp = weightTrig + err;
             weightTrigDown = weightTrig - err; 
         }
         else if(dataRun == "RunC") {
             weightTrig = 0.9841;
             float err = 0.0003;
             weightTrigUp = weightTrig + err;
             weightTrigDown = weightTrig - err; 
         }
         //https://indico.cern.ch/getFile.py/access?contribId=2&resId=0&materialId=slides&confId=228197
         else if(dataRun == "RunD") {
             weightTrig = 0.98151;
             float err = 0.00032;
             weightTrigUp = weightTrig + err;
             weightTrigDown = weightTrig - err; 
         }

         //weighted avg according to lumi
         else if(dataRun == "RunABCD") {
             weightTrig = 0.980917;
             float err = 0.000187267;
             weightTrigUp = weightTrig + err;
             weightTrigDown = weightTrig - err; 
         }
      }
      else if (fabs(muon.eta()) < 1.2){
         weightID = 0.9902;
         weightIDUp = weightID + 0.0003;
         weightIDDown = weightID - 0.0003;
         if(muon.userFloat("deltaBetaCorrRelIso")<0.12 || muon.userFloat("deltaBetaCorrRelIso")>0.2){
            weightIso = 1.0031;
            weightIsoUp = weightIso + 0.0003;
            weightIsoDown = weightIso - 0.0003;
         }else if(muon.userFloat("deltaBetaCorrRelIso")<0.2){
            weightIso = 1.0013;
            weightIsoUp = weightIso + 0.0002;
            weightIsoDown = weightIso - 0.0002;
         }
         
         //https://indico.cern.ch/getFile.py/access?contribId=2&resId=0&materialId=slides&confId=228197
         if (dataRun == "RunA") {
             weightTrig = 0.9528;  
             float err = 0.0021;
             weightTrigUp = weightTrig + err;
             weightTrigDown = weightTrig - err; 
         }
         else if(dataRun == "RunB") {
             weightTrig = 0.9618;
             float err = 0.0010;
             weightTrigUp = weightTrig + err;
             weightTrigDown = weightTrig - err; 
         }
         else if(dataRun == "RunC") {
             weightTrig = 0.9688;
             float err = 0.0009;
             weightTrigUp = weightTrig + err;
             weightTrigDown = weightTrig - err; 
         }
         //https://indico.cern.ch/getFile.py/access?contribId=2&resId=0&materialId=slides&confId=228197
         else if(dataRun == "RunD") {
             weightTrig = 0.96156;
             float err = 0.00091;
             weightTrigUp = weightTrig + err;
             weightTrigDown = weightTrig - err; 
         }
         //weighted avg according to lumi
         else if(dataRun == "RunABCD") {
             weightTrig = 0.963837;
             float err = 0.00052732;
             weightTrigUp = weightTrig + err;
             weightTrigDown = weightTrig - err; 
         }
      }
      else if(fabs(muon.eta())<2.1){
         weightID = 0.9970;
         weightIDUp = weightID + 0.0003;
         weightIDDown = weightID - 0.0003;
         if(muon.userFloat("deltaBetaCorrRelIso")<0.12 || muon.userFloat("deltaBetaCorrRelIso")>0.2){
            weightIso = 1.0050;
            weightIsoUp = weightIso + 0.0002;
            weightIsoDown = weightIso - 0.0002;
         }else if(muon.userFloat("deltaBetaCorrRelIso")<0.2){
            weightIso = 1.0023;
            weightIsoUp = weightIso + 0.0001;
            weightIsoDown = weightIso - 0.0001;
         }
         
         //https://indico.cern.ch/getFile.py/access?contribId=2&resId=0&materialId=slides&confId=228197
         if (dataRun == "RunA") {
             weightTrig = 0.9809; 
             float err = 0.0016;
             weightTrigUp = weightTrig + err;
             weightTrigDown = weightTrig - err; 
         }
         else if(dataRun == "RunB") {
             weightTrig = 0.9814;
             float err = 0.0008;
             weightTrigUp = weightTrig + err;
             weightTrigDown = weightTrig - err; 
         }
         else if(dataRun == "RunC") {
             weightTrig = 1.0021;
             float err = 0.0007;
             weightTrigUp = weightTrig + err;
             weightTrigDown = weightTrig - err; 
         }
         //https://indico.cern.ch/getFile.py/access?contribId=2&resId=0&materialId=slides&confId=228197
         else if(dataRun == "RunD") {
             weightTrig = 0.99721;
             float err = 0.00069;
             weightTrigUp = weightTrig + err;
             weightTrigDown = weightTrig - err; 
         }
         //weighted avg according to lumi
         else if(dataRun == "RunABCD") {
             weightTrig = 0.994706;
             float err = 0.000407864;
             weightTrigUp = weightTrig + err;
             weightTrigDown = weightTrig - err; 
         }
      }

      
   }

   

   LogDebug("Muon with id weights") << weightID << weightIDUp << weightIDDown;
   
   /*
   //tight
   abs(eta)<0.9 -> sf = 0.9939+-0.0002
   0.9<abs(eta)<1.2 -> 0.9902+-0.0003
   1.2<abs(eta)<2.1 -> 0.9970+-0.0003
   //loose
   A+B
   abs(eta)<0.9 -> sf = 0.9988+-0.0002
   0.9<abs(eta)<1.2 -> 0.9993+-0.0005
   1.2<abs(eta)<2.1 -> 0.9982+-0.0002
   C+D
   abs(eta)<0.9 -> sf = 0.9985+-0.0001
   0.9<abs(eta)<1.2 -> 0.9988+-0.0002
   1.2<abs(eta)<2.1 -> 0.9984+-0.0001

   ____
   PFComb dBeta RelIso <0.12
   abs(eta)<0.9 -> sf = 1.0004+-0.0002
   0.9<abs(eta)<1.2 -> 1.0031+-0.0003
   1.2<abs(eta)<2.1 -> 1.0050+-0.0002

   PFComb dBeta RelIso <0.2
   abs(eta)<0.9 -> sf = 0.9999+-0.0001
   0.9<abs(eta)<1.2 -> 1.0013+-0.0002
   1.2<abs(eta)<2.1 -> 1.0023+-0.0001

   */
   iEvent.put(std::auto_ptr<double>(new double(weightID)), "muonIDWeight");
   iEvent.put(std::auto_ptr<double>(new double(weightIDUp)), "muonIDWeightUp");
   iEvent.put(std::auto_ptr<double>(new double(weightIDDown)), "muonIDWeightDown");
   iEvent.put(std::auto_ptr<double>(new double(weightIso)), "muonIsoWeight");
   iEvent.put(std::auto_ptr<double>(new double(weightIsoUp)), "muonIsoWeightUp");
   iEvent.put(std::auto_ptr<double>(new double(weightIsoDown)), "muonIsoWeightDown");
   iEvent.put(std::auto_ptr<double>(new double(weightTrig)), "muonTriggerWeight");
   iEvent.put(std::auto_ptr<double>(new double(weightTrigUp)), "muonTriggerWeightUp");
   iEvent.put(std::auto_ptr<double>(new double(weightTrigDown)), "muonTriggerWeightDown");
}

// ------------ method called once each job just before starting event loop  ------------
void 
MuonEfficiencyProducer::beginJob()
{
}

// ------------ method called once each job just after ending the event loop  ------------
void 
MuonEfficiencyProducer::endJob() {
}

// ------------ method called when starting to processes a run  ------------
void 
MuonEfficiencyProducer::beginRun(edm::Run&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a run  ------------
void 
MuonEfficiencyProducer::endRun(edm::Run&, edm::EventSetup const&)
{
}

// ------------ method called when starting to processes a luminosity block  ------------
void 
MuonEfficiencyProducer::beginLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a luminosity block  ------------
void 
MuonEfficiencyProducer::endLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&)
{
}

// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void
MuonEfficiencyProducer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(MuonEfficiencyProducer);
