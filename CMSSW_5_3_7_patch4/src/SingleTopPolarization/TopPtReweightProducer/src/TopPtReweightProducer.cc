// -*- C++ -*-
//
// Package:    TopPtReweightProducer
// Class:      TopPtReweightProducer
// 
/**\class TopPtReweightProducer TopPtReweightProducer.cc SingleTopPolarization/TopPtReweightProducer/src/TopPtReweightProducer.cc

 Description: Reweighs the ttbar MC based on https://twiki.cern.ch/twiki/bin/viewauth/CMS/TopPtReweighting

 Implementation:
     The weight is calculated based on the madgraph generator level info. The event is expected to have 2 generated tops with status 3 and |id|==6. The weight is valid for 8 TeV l+jets.
*/
//
// Original Author:  Joosep Pata
//         Created:  Tue Jul  2 15:10:33 EEST 2013
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
#include "DataFormats/HepMCCandidate/interface/GenParticle.h"

#include <TMath.h>

class TopPtReweightProducer : public edm::EDProducer {
   public:
      explicit TopPtReweightProducer(const edm::ParameterSet&);
      ~TopPtReweightProducer();

      static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);

   private:
      virtual void beginJob() ;
      virtual void produce(edm::Event&, const edm::EventSetup&);
      virtual void endJob() ;
      
      virtual void beginRun(edm::Run&, edm::EventSetup const&);
      virtual void endRun(edm::Run&, edm::EventSetup const&);
      virtual void beginLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&);
      virtual void endLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&);
    
    double top_scale_factor(double pt);
    edm::InputTag src;
};

TopPtReweightProducer::TopPtReweightProducer(const edm::ParameterSet& iConfig)
: src(iConfig.getParameter<edm::InputTag>("src"))
{
   produces<double>("weight");
}


TopPtReweightProducer::~TopPtReweightProducer()
{
}


void
TopPtReweightProducer::produce(edm::Event& iEvent, const edm::EventSetup& iSetup)
{
    using namespace edm;
    
    Handle<std::vector<reco::GenParticle>> particles;
    iEvent.getByLabel(src, particles);
   
    int nTops = 0;
    std::vector<reco::GenParticle> tops;
    for (auto & part : *particles) {
        if ( abs(part.pdgId()) == 6 && part.status()==3 ) {
            nTops++;
            tops.push_back(part);
            LogDebug("particle loop") << "Found particle " << part.pdgId() << ", status " << part.status();
        }
    }
    LogDebug("particle total") << "Found " << nTops << " top quarks";
    for (auto& part : tops) {
        LogDebug("tops") << "Top pt " << part.pt();
    }

    double weight = 0.0;
    if(nTops!=2) {
        edm::LogError("tops") << "Event didn't have 2 generated tops!";
        return;
    }

    const reco::GenParticle& top1 = tops[0];
    const reco::GenParticle& top2 = tops[1];

    double sf1 = top_scale_factor(top1.pt());
    double sf2 = top_scale_factor(top2.pt());
    weight = TMath::Sqrt(sf1*sf2);
    LogDebug("weights") << "sf1 " << sf1 << " sf2 " << sf2 << " weight " << weight;

    std::auto_ptr<double> pOut(new double(weight));
    iEvent.put(pOut, "weight");
}

double TopPtReweightProducer::top_scale_factor(double pt) {
    //8 TeV   l+jets  0.159   -0.00141
    return TMath::Exp(0.159+ -0.00141*pt);
}

void 
TopPtReweightProducer::beginJob()
{
}

// ------------ method called once each job just after ending the event loop  ------------
void 
TopPtReweightProducer::endJob() {
}

// ------------ method called when starting to processes a run  ------------
void 
TopPtReweightProducer::beginRun(edm::Run&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a run  ------------
void 
TopPtReweightProducer::endRun(edm::Run&, edm::EventSetup const&)
{
}

// ------------ method called when starting to processes a luminosity block  ------------
void 
TopPtReweightProducer::beginLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a luminosity block  ------------
void 
TopPtReweightProducer::endLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&)
{
}

// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void
TopPtReweightProducer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(TopPtReweightProducer);
