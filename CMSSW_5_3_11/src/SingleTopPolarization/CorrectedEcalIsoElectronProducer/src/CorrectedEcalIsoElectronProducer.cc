// -*- C++ -*-
//
// Package:    CorrectedEcalIsoElectronProducer
// Class:      CorrectedEcalIsoElectronProducer
// 
/**\class CorrectedEcalIsoElectronProducer CorrectedEcalIsoElectronProducer.cc SingleTopPolarization/CorrectedEcalIsoElectronProducer/src/CorrectedEcalIsoElectronProducer.cc

 Description: [one line class summary]

 Implementation:
     [Notes on implementation]
*/
//
// Original Author:  Joosep Pata
//         Created:  Tue Jul  2 12:52:46 EEST 2013
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
#include "EgammaAnalysis/ElectronTools/interface/EcalIsolationCorrector.h"

#include <DataFormats/PatCandidates/interface/Electron.h>
#include <FWCore/Utilities/interface/InputTag.h>


//
// class declaration
//

class CorrectedEcalIsoElectronProducer : public edm::EDProducer {
   public:
      explicit CorrectedEcalIsoElectronProducer(const edm::ParameterSet&);
      ~CorrectedEcalIsoElectronProducer();

      static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);

   private:
    virtual void beginJob() ;
    virtual void produce(edm::Event&, const edm::EventSetup&);
    virtual void endJob() ;
    
    virtual void beginRun(edm::Run&, edm::EventSetup const&);
    virtual void endRun(edm::Run&, edm::EventSetup const&);
    virtual void beginLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&);
    virtual void endLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&);
    const edm::InputTag src;
    const bool isMC;
    EcalIsolationCorrector* ecalIsoCorr;
};

CorrectedEcalIsoElectronProducer::CorrectedEcalIsoElectronProducer(const edm::ParameterSet& iConfig)
: src(iConfig.getParameter<edm::InputTag>("src"))
, isMC(iConfig.getParameter<bool>("isMC"))
{
   produces<std::vector<pat::Electron>>();

   ecalIsoCorr = new EcalIsolationCorrector(true);
}


CorrectedEcalIsoElectronProducer::~CorrectedEcalIsoElectronProducer()
{
    delete ecalIsoCorr; 

}

void
CorrectedEcalIsoElectronProducer::produce(edm::Event& iEvent, const edm::EventSetup& iSetup)
{
    using namespace edm;
    Handle<View<pat::Electron>> eles;
    iEvent.getByLabel(src, eles);
    
    std::vector<pat::Electron> out;
    for(auto& ele : *eles) {
        reco::GsfElectron::IsolationVariables isos = reco::GsfElectron::IsolationVariables(ele.dr03IsolationVariables());
        isos.ecalRecHitSumEt = ecalIsoCorr->correctForHLTDefinition(ele, !isMC, iEvent.id().run());
        LogDebug("electron corrector") <<
            "Corrected ecal iso from " << ele.dr03IsolationVariables() << " to " << isos.ecalRecHitSumEt;
        pat::Electron corrEle(ele);
        corrEle.setDr03Isolation(isos);
        out.push_back(corrEle);
    }
    std::auto_ptr<std::vector<pat::Electron>> pOut(new std::vector<pat::Electron>(out));
    iEvent.put(pOut);
 
}

// ------------ method called once each job just before starting event loop  ------------
void 
CorrectedEcalIsoElectronProducer::beginJob()
{
}

// ------------ method called once each job just after ending the event loop  ------------
void 
CorrectedEcalIsoElectronProducer::endJob() {
}

// ------------ method called when starting to processes a run  ------------
void 
CorrectedEcalIsoElectronProducer::beginRun(edm::Run&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a run  ------------
void 
CorrectedEcalIsoElectronProducer::endRun(edm::Run&, edm::EventSetup const&)
{
}

// ------------ method called when starting to processes a luminosity block  ------------
void 
CorrectedEcalIsoElectronProducer::beginLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a luminosity block  ------------
void 
CorrectedEcalIsoElectronProducer::endLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&)
{
}

// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void
CorrectedEcalIsoElectronProducer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(CorrectedEcalIsoElectronProducer);
