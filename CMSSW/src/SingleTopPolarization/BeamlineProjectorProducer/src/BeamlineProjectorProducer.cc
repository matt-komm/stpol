// -*- C++ -*-
//
// Package:    BeamlineProjectorProducer
// Class:      BeamlineProjectorProducer
// 
/**\class BeamlineProjectorProducer BeamlineProjectorProducer.cc test/BeamlineProjectorProducer/src/BeamlineProjectorProducer.cc

 Description: [one line class summary]

 Implementation:
     [Notes on implementation]
*/
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

#include <DataFormats/Candidate/interface/LeafCandidate.h>
#include "FWCore/Utilities/interface/InputTag.h"
#include "Math/GenVector/VectorUtil.h"
#include <TMath.h>


class BeamlineProjectorProducer: 
    public edm::EDProducer 
{
    public:
        explicit BeamlineProjectorProducer(const edm::ParameterSet&);
        ~BeamlineProjectorProducer();

        static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);

    private:
        virtual void produce(edm::Event&, const edm::EventSetup&);

        std::vector<std::pair<std::string,edm::InputTag>> inputs;


};


BeamlineProjectorProducer::BeamlineProjectorProducer(const edm::ParameterSet& iConfig)
{
    std::vector<edm::InputTag> inputTags = iConfig.getParameter<std::vector<edm::InputTag>>("src");
    for (unsigned int isrc=0; isrc< inputTags.size(); ++isrc)
    {
        std::string name;
        if (inputTags[isrc].process().length()>0)
        {
            name+=inputTags[isrc].process()+"-";
        }
        if (inputTags[isrc].instance().length()>0)
        {
            name+=inputTags[isrc].instance()+"-";
        }
        if (inputTags[isrc].label().length()>0)
        {
            name+=inputTags[isrc].label();
        }
        inputs.push_back(std::pair<std::string,edm::InputTag>(name,inputTags[isrc]));
        produces<std::vector<reco::LeafCandidate>>(name);
    }

}


BeamlineProjectorProducer::~BeamlineProjectorProducer()
{
}

void
BeamlineProjectorProducer::produce(edm::Event& iEvent, const edm::EventSetup& iSetup)
{
    reco::Candidate::Vector beamline;
    beamline.SetXYZ(0.0,0.0,1.0);
    for (unsigned int isrc=0; isrc<inputs.size();++isrc)
    {
        const std::pair<std::string,edm::InputTag>& input = inputs[isrc];
        const std::string& name = input.first;
        const edm::InputTag& inputTag = input.second;
        edm::Handle<edm::View<reco::Candidate>> particleCollection;
        iEvent.getByLabel(inputTag,particleCollection);
        std::auto_ptr<std::vector<reco::LeafCandidate> > projectedParticles(new std::vector<reco::LeafCandidate>());
        for (unsigned int icandidate=0; icandidate<particleCollection->size(); ++icandidate)
        {
            const reco::Candidate& particle = (*particleCollection)[icandidate];
            const reco::Candidate::Vector& vect = particle.p4().Vect();
            reco::Candidate::Vector projectedVect = beamline*vect.Dot(beamline);
            
            reco::Candidate::LorentzVector projectedLVect;
            projectedLVect.SetPxPyPzE(projectedVect.X(),projectedVect.Y(),projectedVect.Z(),sqrt(projectedVect.Mag2()+particle.mass()*particle.mass()));
            reco::LeafCandidate projectedParticle(
                particle.threeCharge(), 
                projectedLVect,
                particle.vertex(),
                particle.pdgId(),
                particle.status(),
                false //do not multiple charge by 3; it's already three charge
            );
            projectedParticles->push_back(projectedParticle);
        }
        
        
        iEvent.put(projectedParticles, name);
    }

} 


void
BeamlineProjectorProducer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) 
{

    edm::ParameterSetDescription desc;
    desc.setUnknown();
    descriptions.addDefault(desc);
}


DEFINE_FWK_MODULE(BeamlineProjectorProducer);
