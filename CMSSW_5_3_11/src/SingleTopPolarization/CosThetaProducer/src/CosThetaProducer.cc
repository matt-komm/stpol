// -*- C++ -*-
//
// Package:    CosThetaProducer
// Class:      CosThetaProducer
//
/**\class CosThetaProducer CosThetaProducer.cc SingleTopPolarization/CosThetaProducer/src/CosThetaProducer.cc

 Description: This class calculates the cosine of the angle between the supplied jet and the lepton in the reference frame of the top quark.

 Implementation:
     See http://arxiv.org/pdf/hep-ph/9912458v1.pdf for a summary on the spin bases.
*/
//
// Original Author: Joosep Pata
//         Created:  Wed Oct  3 14:29:22 EEST 2012
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
#include <DataFormats/Candidate/interface/Candidate.h>
#include "FWCore/MessageLogger/interface/MessageLogger.h"

#include "FWCore/Utilities/interface/InputTag.h"

#include "Math/GenVector/VectorUtil.h"
#include <TMath.h>

class CosThetaProducer : public edm::EDProducer
{
public:
    explicit CosThetaProducer(const edm::ParameterSet &);
    ~CosThetaProducer();

    static void fillDescriptions(edm::ConfigurationDescriptions &descriptions);

private:
    virtual void beginJob() ;
    virtual void produce(edm::Event &, const edm::EventSetup &);
    virtual void endJob() ;

    virtual void beginRun(edm::Run &, edm::EventSetup const &);
    virtual void endRun(edm::Run &, edm::EventSetup const &);
    virtual void beginLuminosityBlock(edm::LuminosityBlock &, edm::EventSetup const &);
    virtual void endLuminosityBlock(edm::LuminosityBlock &, edm::EventSetup const &);

    const edm::InputTag leptonSrc;
    const edm::InputTag topSrc;
    const edm::InputTag jetSrc;

    const ROOT::Math::LorentzVector<ROOT::Math::PxPyPzE4D<double> > beamline_pos;
    const ROOT::Math::LorentzVector<ROOT::Math::PxPyPzE4D<double> > beamline_neg;
};

CosThetaProducer::CosThetaProducer(const edm::ParameterSet &iConfig)
    : leptonSrc(iConfig.getParameter<edm::InputTag>("leptonSrc"))
    , topSrc(iConfig.getParameter<edm::InputTag>("topSrc"))
    , jetSrc(iConfig.getParameter<edm::InputTag>("jetSrc"))
    , beamline_pos(0, 0, iConfig.getParameter<double>("Ecm"), iConfig.getParameter<double>("Ecm"))
    , beamline_neg(0, 0, -iConfig.getParameter<double>("Ecm"), iConfig.getParameter<double>("Ecm"))
{
    produces<double>("cosThetaLightJet");
    produces<double>("cosThetaEtaBeamline");
}


CosThetaProducer::~CosThetaProducer()
{
}

void
CosThetaProducer::produce(edm::Event &iEvent, const edm::EventSetup &iSetup)
{
    using namespace edm;

    double cosThetaLightJet = TMath::QuietNaN();
    double cosThetaEtaBeamline = TMath::QuietNaN();

    Handle<View<reco::Candidate> > tops;
    Handle<View<reco::Candidate> > jets;
    Handle<View<reco::Candidate> > leptons;
    iEvent.getByLabel(topSrc, tops);
    iEvent.getByLabel(jetSrc, jets);
    iEvent.getByLabel(leptonSrc, leptons);
    if (tops->size() > 0 && jets->size() > 0 && leptons->size() > 0)
    {
        if (tops->size() > 1 || jets->size() > 1 || leptons->size() > 1)
        {
            LogError("produce()") << "Number of items in input collections is ambigous: tops "
                << tops->size() << " jets "
                << jets->size() << " leptons "
                << leptons->size() << ", first elements will be used";
        }
        const reco::Candidate &top = tops->at(0);
        const reco::Candidate &jet = jets->at(0);
        const reco::Candidate &lepton = leptons->at(0);
        LogDebug("costheta_input") << "top: " << top.pt() << ":" << top.eta() << ":" << top.phi();
        LogDebug("costheta_input") << "jet: " << jet.pt() << ":" << jet.eta() << ":" << jet.phi();
        LogDebug("costheta_input") << "lepton: " << lepton.pt() << ":" << lepton.eta() << ":" << lepton.phi();

        const ROOT::Math::LorentzVector<ROOT::Math::PxPyPzE4D<double> > boostedLeptonVec = ROOT::Math::VectorUtil::boost(lepton.p4(), top.p4().BoostToCM());
        const ROOT::Math::LorentzVector<ROOT::Math::PxPyPzE4D<double> > boostedJetVec = ROOT::Math::VectorUtil::boost(jet.p4(), top.p4().BoostToCM());
        
        const ROOT::Math::LorentzVector<ROOT::Math::PxPyPzE4D<double> >& beamline = jet.eta()> 0 ? beamline_pos : beamline_neg;
        const ROOT::Math::LorentzVector<ROOT::Math::PxPyPzE4D<double> > boostedBeamline = ROOT::Math::VectorUtil::boost(beamline, top.p4().BoostToCM());

        cosThetaLightJet = ROOT::Math::VectorUtil::CosTheta(boostedJetVec.Vect(), boostedLeptonVec.Vect());
        cosThetaEtaBeamline = ROOT::Math::VectorUtil::CosTheta(boostedBeamline.Vect(), boostedLeptonVec.Vect());

        LogDebug("produce()") << "cosThetaLightJet: " << cosThetaLightJet;
        LogDebug("produce()") << "cosThetaEtaBeamline: " << cosThetaEtaBeamline;
    }
    else
    {
        LogError("produce()") << "Number of items in input collections is too small: tops " << tops->size() << " jets " << jets->size() << " leptons " << leptons->size();
    }

    std::auto_ptr<double> pCosThetaLJ(new double(cosThetaLightJet));
    iEvent.put(pCosThetaLJ, "cosThetaLightJet");
    std::auto_ptr<double> pCosThetaEtaBL(new double(cosThetaEtaBeamline));
    iEvent.put(pCosThetaEtaBL, "cosThetaEtaBeamline");
}

void
CosThetaProducer::beginJob()
{
}

void
CosThetaProducer::endJob()
{
}

void
CosThetaProducer::beginRun(edm::Run &, edm::EventSetup const &)
{
}

void
CosThetaProducer::endRun(edm::Run &, edm::EventSetup const &)
{
}

void
CosThetaProducer::beginLuminosityBlock(edm::LuminosityBlock &, edm::EventSetup const &)
{
}

void
CosThetaProducer::endLuminosityBlock(edm::LuminosityBlock &, edm::EventSetup const &)
{
}

void
CosThetaProducer::fillDescriptions(edm::ConfigurationDescriptions &descriptions)
{
    edm::ParameterSetDescription desc;
    desc.setUnknown();
    descriptions.addDefault(desc);
}

DEFINE_FWK_MODULE(CosThetaProducer);
