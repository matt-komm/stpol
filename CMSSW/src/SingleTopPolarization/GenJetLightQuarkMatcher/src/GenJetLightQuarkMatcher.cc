// -*- C++ -*-
//
// Package:    GenJetLightQuarkMatcher
// Class:      GenJetLightQuarkMatcher
// 

//
// Original Author:  Matthias Komm
//         Created:  Tue Nov  4 13:54:30 CET 2014
// $Id$
//
//


// system include files
#include <memory>
#include <string>
#include <vector>

// user include files
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/EDProducer.h"

#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"
#include "FWCore/MessageLogger/interface/MessageLogger.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"

#include <DataFormats/Candidate/interface/Candidate.h>
#include <DataFormats/Candidate/interface/LeafCandidate.h>
#include <DataFormats/JetReco/interface/GenJet.h>
#include <DataFormats/HepMCCandidate/interface/GenParticle.h>

#include <DataFormats/Math/interface/deltaR.h>

#include "FWCore/Utilities/interface/InputTag.h"
#include "Math/GenVector/VectorUtil.h"
#include <TMath.h>


class GenJetLightQuarkMatcher: 
    public edm::EDProducer 
{
    public:
        explicit GenJetLightQuarkMatcher(const edm::ParameterSet&);
        ~GenJetLightQuarkMatcher();

        static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);

    private:
        virtual void produce(edm::Event&, const edm::EventSetup&);

        double calculateDR(const reco::Candidate& p1, const reco::Candidate& p2);
    
        edm::InputTag _trueLightQuark;
        edm::InputTag _genJetCollection;

};


GenJetLightQuarkMatcher::GenJetLightQuarkMatcher(const edm::ParameterSet& iConfig)
{
    _trueLightQuark = iConfig.getParameter<edm::InputTag>("trueLightQuark");
    _genJetCollection = iConfig.getParameter<edm::InputTag>("genJets");
    produces<std::vector<reco::LeafCandidate>>("dRMatch");
    //produces<reco::GenParticle>("decayMatch");
    //produces<reco::GenParticle>("pT");
}


GenJetLightQuarkMatcher::~GenJetLightQuarkMatcher()
{
}

void
GenJetLightQuarkMatcher::produce(edm::Event& iEvent, const edm::EventSetup& iSetup)
{
    
    edm::Handle<edm::View<reco::GenJet>> genJetCollection;
    iEvent.getByLabel(_genJetCollection,genJetCollection);
    
    edm::Handle<edm::View<reco::GenParticle>> trueLightQuarkCollection;
    iEvent.getByLabel(_trueLightQuark,trueLightQuarkCollection);
    const reco::GenParticle& trueLightQuark = trueLightQuarkCollection->at(0);
    
    const reco::LeafCandidate* dRMatch=&genJetCollection->at(0);
    double mindR2=reco::deltaR2(*dRMatch,trueLightQuark);
    
    for (unsigned int ijet = 1; ijet < genJetCollection->size(); ++ijet)
    {
        double dR2 = reco::deltaR2(genJetCollection->at(ijet),trueLightQuark);
        if (dR2<mindR2)
        {
            mindR2=dR2;
            dRMatch=&genJetCollection->at(ijet);
        }
    }
    std::auto_ptr<std::vector<reco::LeafCandidate> > dRMatchCollection(new std::vector<reco::LeafCandidate>());
    dRMatchCollection->push_back(reco::LeafCandidate(*dRMatch));
    iEvent.put(dRMatchCollection,"dRMatch");
}


void
GenJetLightQuarkMatcher::fillDescriptions(edm::ConfigurationDescriptions& descriptions) 
{

    edm::ParameterSetDescription desc;
    desc.setUnknown();
    descriptions.addDefault(desc);
}


DEFINE_FWK_MODULE(GenJetLightQuarkMatcher);
