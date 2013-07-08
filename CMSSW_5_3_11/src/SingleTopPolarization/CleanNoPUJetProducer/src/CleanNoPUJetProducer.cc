// -*- C++ -*-
//
// Package:    CleanNoPUJetProducer
// Class:      CleanNoPUJetProducer
// 
/**\class CleanNoPUJetProducer CleanNoPUJetProducer.cc SingleTopPolarization/CleanNoPUJetProducer/src/CleanNoPUJetProducer.cc

 Description: [one line class summary]

 Implementation:
     [Notes on implementation]
*/
//
// Original Author:  Joosep Pata
//         Created:  Sun Oct  7 17:53:17 EEST 2012
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

#include "FWCore/Utilities/interface/InputTag.h"
#include "DataFormats/PatCandidates/interface/Jet.h"
#include "FWCore/MessageLogger/interface/MessageLogger.h"
#include <TMath.h>
#include "CMGTools/External/interface/PileupJetIdentifier.h"

//
// class declaration
//

class CleanNoPUJetProducer : public edm::EDProducer {
   public:
      explicit CleanNoPUJetProducer(const edm::ParameterSet&);
      ~CleanNoPUJetProducer();

      static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);

   private:
      virtual void beginJob() ;
      virtual void produce(edm::Event&, const edm::EventSetup&);
      virtual void endJob() ;
      
      virtual void beginRun(edm::Run&, edm::EventSetup const&);
      virtual void endRun(edm::Run&, edm::EventSetup const&);
      virtual void beginLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&);
      virtual void endLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&);

      const edm::InputTag jetSrc;
      const edm::InputTag jetPUIdMVASrc;
      const edm::InputTag jetPUIdFlagSrc;
      const edm::InputTag jetPUIdVarsSrc;

      // ----------member data ---------------------------
      const bool isOriginal;
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
CleanNoPUJetProducer::CleanNoPUJetProducer(const edm::ParameterSet& iConfig)
: jetSrc(iConfig.getParameter<edm::InputTag>("jetSrc"))
, jetPUIdMVASrc(iConfig.getParameter<edm::InputTag>("PUidMVA"))
, jetPUIdFlagSrc(iConfig.getParameter<edm::InputTag>("PUidFlag"))
, jetPUIdVarsSrc(iConfig.getParameter<edm::InputTag>("PUidVars"))
, isOriginal(iConfig.getParameter<bool>("isOriginal"))
{
  produces<std::vector<pat::Jet> >();
  
}


CleanNoPUJetProducer::~CleanNoPUJetProducer()
{
}


//
// member functions
//

// ------------ method called to produce the data  ------------
void
CleanNoPUJetProducer::produce(edm::Event& iEvent, const edm::EventSetup& iSetup)
{
   using namespace edm;
   Handle<View<reco::Candidate> > jets;
   Handle<ValueMap<float> > mvaIDs;
   Handle<ValueMap<int> > flags;
   Handle<ValueMap<StoredPileupJetIdentifier> > jetIDs;

   iEvent.getByLabel(jetSrc, jets);
   iEvent.getByLabel(jetPUIdMVASrc, mvaIDs);
   iEvent.getByLabel(jetPUIdFlagSrc, flags);
   iEvent.getByLabel(jetPUIdVarsSrc, jetIDs);

   std::auto_ptr<std::vector<pat::Jet> > outJets(new std::vector<pat::Jet>());
   for ( uint i = 0; i < jets->size(); ++i ) {
    const pat::Jet& jet = dynamic_cast<const pat::Jet&>(jets->at(i));
    float mva = 0;
    int idflag = 0;
    const StoredPileupJetIdentifier* id = 0;
    if (!isOriginal && jet.hasUserCand("original")) {
        LogDebug("produce") << "Input jet is not original";
        reco::CandidatePtr candP = jet.userCand("original");
        mva = (*mvaIDs)[candP];
        idflag = (*flags)[candP];
        id = &((*jetIDs)[candP]);
        LogDebug("produce") << "Using original jet pointer: mva = " << mva << " idflag = " << idflag;
    } else {
        mva = (*mvaIDs)[jets->refAt(i)];
        idflag = (*flags)[jets->refAt(i)];
        id = &((*jetIDs)[jets->refAt(i)]);
        LogDebug("produce") << "Using original jet: mva = " << mva << " idflag = " << idflag;
    }

    //Get the values from the valueMaps

    LogDebug("produce()") << "jet pt: " << jet.pt() << " eta: " << jet.eta() << " mvaID: " << mva;
    if( PileupJetIdentifier::passJetId( idflag, PileupJetIdentifier::kLoose ) ) {
      LogDebug("produce()") << " pass loose wp";
      outJets->push_back(jet);

      //get the non-const jet
      pat::Jet& jet = outJets->back();
      jet.addUserFloat("rms", id->RMS());
      jet.addUserFloat("mva", mva);
      jet.addUserFloat("nParticles", id->nParticles());
      jet.addUserFloat("nCharged", id->nCharged());
      jet.addUserFloat("nNeutral", id->nNeutrals());
      LogDebug("produce()") << "jet rms=" << jet.userFloat("rms");

    } else {
      LogDebug("produce()") << " fail loose wp";
    }
   }
   iEvent.put(outJets);
    
}

// ------------ method called once each job just before starting event loop  ------------
void 
CleanNoPUJetProducer::beginJob()
{
}

// ------------ method called once each job just after ending the event loop  ------------
void 
CleanNoPUJetProducer::endJob() {
}

// ------------ method called when starting to processes a run  ------------
void 
CleanNoPUJetProducer::beginRun(edm::Run&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a run  ------------
void 
CleanNoPUJetProducer::endRun(edm::Run&, edm::EventSetup const&)
{
}

// ------------ method called when starting to processes a luminosity block  ------------
void 
CleanNoPUJetProducer::beginLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a luminosity block  ------------
void 
CleanNoPUJetProducer::endLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&)
{
}

// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void
CleanNoPUJetProducer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(CleanNoPUJetProducer);
