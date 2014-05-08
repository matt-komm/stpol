// -*- C++ -*-
//
// Package:    JetMCSmearProducer
// Class:      JetMCSmearProducer
// 
/**\class JetMCSmearProducer JetMCSmearProducer.cc SingleTopPolarization/JetMCSmearProducer/src/JetMCSmearProducer.cc

 Description: [one line class summary]

 Implementation:
     [Notes on implementation]
*/
//
// Original Author:  
//         Created:  Thu Oct  4 10:40:41 EEST 2012
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
#include "FWCore/Utilities/interface/InputTag.h"
#include "DataFormats/PatCandidates/interface/Jet.h"
#include <TMath.h>


//
// class declaration
//

class JetMCSmearProducer : public edm::EDProducer {
   public:
      explicit JetMCSmearProducer(const edm::ParameterSet&);
      ~JetMCSmearProducer();

      static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);

   private:
      virtual void beginJob() ;
      virtual void produce(edm::Event&, const edm::EventSetup&);
      virtual void endJob() ;
      
      virtual void beginRun(edm::Run&, edm::EventSetup const&);
      virtual void endRun(edm::Run&, edm::EventSetup const&);
      virtual void beginLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&);
      virtual void endLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&);

      double smearFactor(const pat::Jet& jet);

      const edm::InputTag jetSrc;
      const bool reportMissingGenJet;

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
JetMCSmearProducer::JetMCSmearProducer(const edm::ParameterSet& iConfig)
: jetSrc(iConfig.getParameter<edm::InputTag>("src"))
, reportMissingGenJet(iConfig.getUntrackedParameter<bool>("reportMissingGenJet", false))
{
   //register your products
   produces<std::vector<pat::Jet> >();

   //now do what ever other initialization is needed
  
}


JetMCSmearProducer::~JetMCSmearProducer()
{
 
   // do anything here that needs to be done at desctruction time
   // (e.g. close files, deallocate resources etc.)

}


//
// member functions
//


// https://twiki.cern.ch/twiki/bin/view/CMS/JetResolution
/*

0.0–0.5  1.052+-0.012+0.062-0.061
0.5–1.1  1.057+-0.012+0.056-0.055
1.1–1.7  1.096+-0.017+0.063-0.062
1.7–2.3  1.134+-0.035+0.087-0.085
2.3–5.0  1.288+-0.127+0.155-0.153

*/
double
JetMCSmearProducer::smearFactor(const pat::Jet& jet) {
  double genJetEta = fabs(jet.genJet()->eta());
  double smearFactor = TMath::QuietNaN();
  if(genJetEta>=0.0 && genJetEta<0.5) {
    smearFactor = 0.052;
  } else if(genJetEta>0.5 && genJetEta<1.1) {
    smearFactor = 0.057;
  } else if(genJetEta>1.1 && genJetEta<1.7) {
    smearFactor = 0.096;
  } else if(genJetEta>1.7 && genJetEta<2.3) {
    smearFactor = 0.134;
  } else if(genJetEta>2.3 && genJetEta<=5.0) {
    smearFactor = 0.288;
  } else {
    LogDebug("produce()") << "genJet eta is out of range: " << genJetEta;
  }
  LogDebug("smearFactor()") << "smearFactor " << smearFactor;
  return smearFactor;
}

// ------------ method called to produce the data  ------------
void
JetMCSmearProducer::produce(edm::Event& iEvent, const edm::EventSetup& iSetup)
{
   using namespace edm;
   Handle<std::vector<pat::Jet> > jets;
   iEvent.getByLabel(jetSrc, jets);

   std::auto_ptr<std::vector<pat::Jet> > outJets(new std::vector<pat::Jet>(*jets));
   int i = 0;
   for(auto & jet : *outJets) {
    

    double smear = TMath::QuietNaN();
    if(jet.genJet()!=0) {
      
      double sf = smearFactor(jet);

      smear = (std::max(0.0, jet.pt() + sf*(jet.pt()-jet.genJet()->pt())))/jet.pt();
    } else {
      if(reportMissingGenJet) {
        LogWarning("produce()") << "Could not access genJet for jet " << jetSrc.label() << "(" << i << ")";
      }
    }

    double pt_smear = smear*jet.pt();
    double M_smear = smear*jet.mass();
    LogDebug("produce()") << "jet smear (" << smear << ") smeared pt (" << pt_smear << ") smeared mass (" << M_smear << ")";

    jet.addUserFloat("pt_smear", pt_smear);
    jet.addUserFloat("M_smear", M_smear);

    i++;
    //ROOT::Math::LorentzVector<ROOT::Math::PtEtaPhiE4D<double> >* vec = new ROOT::Math::LorentzVector<ROOT::Math::PtEtaPhiE4D<double> >(jet.p4());
    //vec->SetPt((double)999.0);
    //jet.setP4(*vec)
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
JetMCSmearProducer::beginJob()
{
}

// ------------ method called once each job just after ending the event loop  ------------
void 
JetMCSmearProducer::endJob() {
}

// ------------ method called when starting to processes a run  ------------
void 
JetMCSmearProducer::beginRun(edm::Run&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a run  ------------
void 
JetMCSmearProducer::endRun(edm::Run&, edm::EventSetup const&)
{
}

// ------------ method called when starting to processes a luminosity block  ------------
void 
JetMCSmearProducer::beginLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a luminosity block  ------------
void 
JetMCSmearProducer::endLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&)
{
}

// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void
JetMCSmearProducer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(JetMCSmearProducer);
