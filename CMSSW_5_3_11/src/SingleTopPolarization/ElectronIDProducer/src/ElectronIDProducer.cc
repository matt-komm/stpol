// -*- C++ -*-
//
// Package:    ElectronIDProducer
// Class:      ElectronIDProducer
//
/**\class ElectronIDProducer ElectronIDProducer.cc SingleTopPolarization/ElectronIDProducer/src/ElectronIDProducer.cc
 
 Description: This class produces the electron/primary vertex dz and dxy the track counts as userFloats.
 
 Implementation:
 [Notes on implementation]
 */
//
// Original Author:
//         Created:  Thu Sep 27 14:36:33 EEST 2012
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

//PAT
#include <DataFormats/PatCandidates/interface/Electron.h>

//reco::Vertex
#include <DataFormats/VertexReco/interface/Vertex.h>

//for edm::LogInfo etc.
#include "FWCore/MessageLogger/interface/MessageLogger.h"

#include "FWCore/Utilities/interface/InputTag.h"

#include <TMath.h>

//
// class declaration
//

class ElectronIDProducer : public edm::EDProducer {
public:
    explicit ElectronIDProducer(const edm::ParameterSet&);
    ~ElectronIDProducer();
    
    static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);
    
private:
    virtual void beginJob() ;
    virtual void produce(edm::Event&, const edm::EventSetup&);
    virtual void endJob() ;
    
    virtual void beginRun(edm::Run&, edm::EventSetup const&);
    virtual void endRun(edm::Run&, edm::EventSetup const&);
    virtual void beginLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&);
    virtual void endLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&);
    
    const edm::InputTag electronSrc;
    const edm::InputTag primaryVertexSource;
    
    // ----------member data ---------------------------
};

ElectronIDProducer::ElectronIDProducer(const edm::ParameterSet& iConfig) :
electronSrc(iConfig.getParameter<edm::InputTag>("electronSrc")),
primaryVertexSource(iConfig.getParameter<edm::InputTag>("primaryVertexSource"))
{
    produces<std::vector<pat::Electron> >();
}


ElectronIDProducer::~ElectronIDProducer()
{
}

// ------------ method called to produce the data  ------------
void
ElectronIDProducer::produce(edm::Event& iEvent, const edm::EventSetup& iSetup)
{
    using namespace edm;
    
    Handle<std::vector<pat::Electron> > electrons;
    Handle<View<reco::Vertex> > primaryVertices;
    iEvent.getByLabel(electronSrc, electrons);
    iEvent.getByLabel(primaryVertexSource, primaryVertices);
    
    LogDebug("produce()") << "Creating auto_ptr";
    
    std::auto_ptr<std::vector<pat::Electron> > outElectrons(new std::vector<pat::Electron>(*electrons));
    LogDebug("produce()") << "Created auto_ptr";
    LogDebug("produce()") << "Input collection " << electronSrc.label() << " has " << electrons->size() << " items";
    
    float dxy = TMath::QuietNaN();
    int nHits = -9999;
    
    const reco::Vertex::Point* pvPoint;
    if (!(primaryVertices.isValid()) || primaryVertices->size()==0) {
        edm::LogError("produce()") << "No primary vertices";
        pvPoint = 0;
    }
    else {
        pvPoint = &(primaryVertices->at(0).position());
    }
    
    for (auto & electron : (*outElectrons)) {
        if (electron.gsfTrack().isNonnull()) {
            nHits = electron.gsfTrack()->trackerExpectedHitsInner().numberOfHits();
            if (pvPoint) {
                dxy = electron.gsfTrack()->dxy(*pvPoint);
            }
            else {
                dxy = TMath::QuietNaN();
                nHits = -9999;
                edm::LogError("produce()") << "Could not use primary vertex";
            }
        } else {
            nHits = -9999;
            edm::LogError("produce()") << "electron does not have gsfTrack()";
        }
        electron.addUserInt("gsfTrack_trackerExpectedHitsInner_numberOfHits", nHits);
        electron.addUserFloat("dxy", dxy);
        
    }
    iEvent.put(outElectrons);
}

// ------------ method called once each job just before starting event loop  ------------
void
ElectronIDProducer::beginJob()
{
}

// ------------ method called once each job just after ending the event loop  ------------
void
ElectronIDProducer::endJob() {
}

// ------------ method called when starting to processes a run  ------------
void
ElectronIDProducer::beginRun(edm::Run&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a run  ------------
void
ElectronIDProducer::endRun(edm::Run&, edm::EventSetup const&)
{
}

// ------------ method called when starting to processes a luminosity block  ------------
void
ElectronIDProducer::beginLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a luminosity block  ------------
void
ElectronIDProducer::endLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&)
{
}

// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void
ElectronIDProducer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
    //The following says we do not know what parameters are allowed so do no validation
    // Please change this to state exactly what you do use, even if it is no parameters
    edm::ParameterSetDescription desc;
    desc.setUnknown();
    descriptions.addDefault(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(ElectronIDProducer);
