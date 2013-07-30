// -*- C++ -*-
//
// Package:    MuonIDProducer
// Class:      MuonIDProducer
//
/**\class MuonIDProducer MuonIDProducer.cc SingleTopPolarization/MuonIDProducer/src/MuonIDProducer.cc
 
 Description: This class produces the muon/primary vertex dz and dxy the track counts as userFloats.
 
 Implementation:
 [Notes on implementation]
 */
//
// Original Author:  Joosep Pata joosep.pata@cern.ch
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
#include <DataFormats/PatCandidates/interface/Muon.h>

//reco::Vertex
#include <DataFormats/VertexReco/interface/Vertex.h>

//for edm::LogInfo etc.
#include "FWCore/MessageLogger/interface/MessageLogger.h"

#include "FWCore/Utilities/interface/InputTag.h"

class MuonIDProducer : public edm::EDProducer {
public:
    explicit MuonIDProducer(const edm::ParameterSet&);
    ~MuonIDProducer();
    
    static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);
    
private:
    virtual void beginJob() ;
    virtual void produce(edm::Event&, const edm::EventSetup&);
    virtual void endJob() ;
    
    virtual void beginRun(edm::Run&, edm::EventSetup const&);
    virtual void endRun(edm::Run&, edm::EventSetup const&);
    virtual void beginLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&);
    virtual void endLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&);
    
    const edm::InputTag muonSource;
    const edm::InputTag primaryVertexSource;
    
    // ----------member data ---------------------------
};

MuonIDProducer::MuonIDProducer(const edm::ParameterSet& iConfig) :
muonSource(iConfig.getParameter<edm::InputTag>("muonSrc")),
primaryVertexSource(iConfig.getParameter<edm::InputTag>("primaryVertexSource"))
{
    produces<std::vector<pat::Muon>>();
}


MuonIDProducer::~MuonIDProducer()
{
}

void
MuonIDProducer::produce(edm::Event& iEvent, const edm::EventSetup& iSetup)
{
    using namespace edm;
    
    Handle<std::vector<pat::Muon> > muons;
    Handle<View<reco::Vertex> > primaryVertices;
    iEvent.getByLabel(muonSource, muons);
    iEvent.getByLabel(primaryVertexSource, primaryVertices);
    
    //assert(muons.isValid());
    //assert(primaryVertices.isValid());
    if(! muons.isValid()) {
        LogError("produce()") << "Muon collection " << muonSource.label() << " was not valid";
        return;
    }
    //if(! primaryVertices.isValid()) {
    //    LogError("produce()") << "Primary vertex collection " << primaryVertexSource.label() << " was not valid";
    //    return;
    //}    
    
    LogDebug("produce()") << "Creating auto_ptr";
    
    std::auto_ptr<std::vector<pat::Muon> > outMuons(new std::vector<pat::Muon>(*muons));
    LogDebug("produce()") << "Created auto_ptr";
    LogDebug("produce()") << "Input collection " << muonSource.label() << " has " << muons->size() << " items";
    float dz = TMath::QuietNaN();
    float dxy = TMath::QuietNaN();
    
    const reco::Vertex::Point* pvPoint;
    if (!(primaryVertices.isValid()) || primaryVertices->size()==0) {
        edm::LogError("produce()") << "No primary vertices";
        pvPoint = 0;
    }
    else {
        pvPoint = &(primaryVertices->at(0).position());
    }
    
    for (auto & muon : (*outMuons)) {
        
        float x = TMath::QuietNaN();
        if(muon.track().isAvailable()) {
            x = muon.track()->hitPattern().trackerLayersWithMeasurement();
        }
        else {
            edm::LogError("produce()") << "muon does not have track()";
        }
        muon.addUserFloat("track_hitPattern_trackerLayersWithMeasurement", x);
        LogDebug("produce()") << "track_hitPattern_trackerLayersWithMeasurement " << x;
        
        x = TMath::QuietNaN();
        if(muon.globalTrack().isAvailable()) {
            x = muon.globalTrack()->hitPattern().numberOfValidMuonHits();
        }
        else {
            edm::LogError("muon track") << "muon does not have globalTrack()";
        }
        muon.addUserFloat("globalTrack_hitPattern_numberOfValidMuonHits", x);
        LogDebug("muon track") << "globalTrack_hitPattern_numberOfValidMuonHits " << x;
        
        x = TMath::QuietNaN();
        if (muon.innerTrack().isAvailable()) {
            x = muon.innerTrack()->hitPattern().numberOfValidPixelHits();
            
            if (pvPoint) {
                dz = muon.innerTrack()->dz(*pvPoint);
                dxy = muon.innerTrack()->dxy(*pvPoint);
            }
            else {
                dz = TMath::QuietNaN();
                dxy = TMath::QuietNaN();
                LogDebug("produce()") << "Could not use primary vertex";
            }
        }
        else {
            edm::LogError("produce()") << "muon does not have innerTrack()";
        }
        muon.addUserFloat("innerTrack_hitPattern_numberOfValidPixelHits", x);
        LogDebug("produce()") << "innerTrack_hitPattern_numberOfValidPixelHits " << x;
        
        muon.addUserFloat("dz", dz);
        LogDebug("produce()") << "dz " << dz;
        muon.addUserFloat("dxy", dxy);
        LogDebug("produce()") << "dxy " << dxy;
        
    }
    iEvent.put(outMuons);
}

// ------------ method called once each job just before starting event loop  ------------
void
MuonIDProducer::beginJob()
{
}

// ------------ method called once each job just after ending the event loop  ------------
void
MuonIDProducer::endJob() {
}

// ------------ method called when starting to processes a run  ------------
void
MuonIDProducer::beginRun(edm::Run&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a run  ------------
void
MuonIDProducer::endRun(edm::Run&, edm::EventSetup const&)
{
}

// ------------ method called when starting to processes a luminosity block  ------------
void
MuonIDProducer::beginLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a luminosity block  ------------
void
MuonIDProducer::endLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&)
{
}

// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void
MuonIDProducer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
    //The following says we do not know what parameters are allowed so do no validation
    // Please change this to state exactly what you do use, even if it is no parameters
    edm::ParameterSetDescription desc;
    desc.setUnknown();
    descriptions.addDefault(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(MuonIDProducer);
