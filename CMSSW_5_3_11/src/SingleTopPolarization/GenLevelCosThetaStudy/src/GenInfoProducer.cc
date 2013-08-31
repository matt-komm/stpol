// -*- C++ -*-
//
// Package:    GenInfoProducer
// Class:      GenInfoProducer
//
/**\class GenInfoProducer GenInfoProducer.cc GenInfoAnalyzer/GenInfoProducer/src/GenInfoProducer.cc

 Description: [one line class summary]

 Implementation:
     [Notes on implementation]
*/
//
// Original Author:  Dmitri Konstantinov,32 3-A08,+41227677567,
//         Created:  Fri Aug  2 18:34:29 CEST 2013
// $Id$
//
//


// system include files
#include <memory>

// user include files
#include "DataFormats/Math/interface/deltaR.h"

#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/EDProducer.h"
#include "FWCore/Framework/interface/EDFilter.h"

#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"

#include "DataFormats/Candidate/interface/CandidateFwd.h"
#include "DataFormats/Common/interface/Ref.h"
#include "DataFormats/JetReco/interface/Jet.h"
#include "DataFormats/JetReco/interface/GenJet.h"

#include "DataFormats/JetReco/interface/GenJetCollection.h"
#include "DataFormats/JetReco/interface/GenJet.h"

#include "DataFormats/Candidate/interface/Candidate.h"
#include "DataFormats/HepMCCandidate/interface/GenParticle.h"


#include <DataFormats/RecoCandidate/interface/RecoCandidate.h>
#include <DataFormats/Candidate/interface/CompositeCandidate.h>

#include "DataFormats/METReco/interface/CaloMET.h"
#include "DataFormats/METReco/interface/CaloMETCollection.h"
#include "DataFormats/METReco/interface/GenMET.h"
#include "DataFormats/METReco/interface/GenMETCollection.h"

#include "DataFormats/JetReco/interface/Jet.h"
#include "DataFormats/JetReco/interface/JetCollection.h"
#include "DataFormats/JetReco/interface/CaloJetCollection.h"
#include "DataFormats/JetReco/interface/JetFloatAssociation.h"

#include "DataFormats/Common/interface/View.h"
#include "DataFormats/Common/interface/getRef.h"

#include "SimDataFormats/JetMatching/interface/JetFlavour.h"
#include "SimDataFormats/JetMatching/interface/JetFlavourMatching.h"
#include "SimDataFormats/JetMatching/interface/MatchedPartons.h"
#include "SimDataFormats/JetMatching/interface/JetMatchedPartons.h"

#include <TRandom.h>

class GenInfoProducer : public edm::EDFilter
{
public:
    explicit GenInfoProducer(const edm::ParameterSet &);
    ~GenInfoProducer();

    static void fillDescriptions(edm::ConfigurationDescriptions &descriptions);

private:
    virtual void beginJob() ;
    virtual bool filter(edm::Event &, const edm::EventSetup &);
    virtual void endJob() ;

    virtual bool beginRun(edm::Run &, edm::EventSetup const &);
    virtual bool endRun(edm::Run &, edm::EventSetup const &);
    virtual bool beginLuminosityBlock(edm::LuminosityBlock &, edm::EventSetup const &);
    virtual bool endLuminosityBlock(edm::LuminosityBlock &, edm::EventSetup const &);


    edm::InputTag sourcePartons_;
    edm::InputTag sourceByRefer_;
    edm::InputTag sourceByValue_;
    edm::Handle<reco::JetMatchedPartonsCollection> matchedPartons;
    edm::Handle<reco::JetFlavourMatchingCollection> flavourMatching;

    TRandom *rng;

    //The dR cleaning used to disambiguate parton jets from leptons
    // Jets failing this will be thrown away.
    const float jet_lepton_dr;

    const float lepton_pt_low;

};

using namespace std;
using namespace reco;
using namespace edm;


GenInfoProducer::GenInfoProducer(const edm::ParameterSet &iConfig)
    :
    jet_lepton_dr(0.5),
    lepton_pt_low(26)
{
    // sourceByRefer_ = iConfig.getParameter<InputTag> ("srcByReference");
    sourceByValue_ = iConfig.getParameter<InputTag> ("srcByValue");

    produces<std::vector<reco::CompositeCandidate> >("selectedLeptons");
    produces<std::vector<reco::CompositeCandidate> >("selectedMETs");
    produces<std::vector<reco::CompositeCandidate> >("selectedBTagJets");
    produces<std::vector<reco::CompositeCandidate> >("selectedLightJets");

    rng = new TRandom();
}


GenInfoProducer::~GenInfoProducer()
{
    delete rng;
}

bool isGoodJet(reco::Jet jet)
{
    return (jet.pt() > 40 && fabs(jet.eta()) < 4.5);
}

bool isBTag()
{
    return false;
}

float deltaR(reco::CompositeCandidate p1, reco::CompositeCandidate p2)
{
    return reco::deltaR(p1.eta(), p1.phi() , p2.pt() , p2.phi());
}
bool
GenInfoProducer::filter(edm::Event &iEvent, const edm::EventSetup &iSetup)
{
    using namespace edm;
    using namespace std;

    std::auto_ptr<std::vector<reco::CompositeCandidate> > muColl(new std::vector<reco::CompositeCandidate>);
    //std::auto_ptr<std::vector<reco::CompositeCandidate> > bJetColl(new std::vector<reco::CompositeCandidate>);
    std::auto_ptr<std::vector<reco::CompositeCandidate> > jetColl(new std::vector<reco::CompositeCandidate>);
    std::auto_ptr<std::vector<reco::CompositeCandidate> > metColl(new std::vector<reco::CompositeCandidate>);
    std::auto_ptr<std::vector<reco::CompositeCandidate> > lightJetColl(new std::vector<reco::CompositeCandidate>);
    std::auto_ptr<std::vector<reco::CompositeCandidate> > bJetColl(new std::vector<reco::CompositeCandidate>);

    auto finalize = [&] ()
    {
        LogInfo("") << "Putting products to event";
        iEvent.put(muColl, "selectedLeptons");
        iEvent.put(bJetColl, "selectedBTagJets");
        iEvent.put(lightJetColl, "selectedLightJets");
        iEvent.put(metColl, "selectedMETs");
        LogInfo("") << "Done putting products to event";
    };

    edm::LogInfo("produce") << "Getting gen particles";

    Handle<GenParticleCollection> genParticles;
    iEvent.getByLabel("genParticles", genParticles);

    if (!genParticles.isValid())
    {
        LogError("") << "Could not open gen particle collection";
        throw 1;
    }


    for (size_t i = 0; i < genParticles->size(); ++i)
    {
        const Candidate &p = (*genParticles)[i];
        if (abs(p.pdgId()) == 13 && p.status() == 1 && p.pt() > lepton_pt_low)
        {
            reco::CompositeCandidate *cand = new reco::CompositeCandidate(
                p.charge(),
                p.p4(),
                reco::Candidate::Point(0, 0, 0),
                p.pdgId()
            );
            muColl->push_back(*cand);
            delete cand;
        }
    }

    if (muColl->size() != 1)
    {
        LogInfo("") << "Wrong number of muons: " << muColl->size();
        finalize();
        return false;
    }

    const reco::CompositeCandidate &muon = muColl->at(0);
    LogInfo("") << "muon " << muon.pt() << " " << muon.eta() << " " << muon.phi();

    edm::LogInfo("jet_flavour") << "Getting jet flavour objects";
    iEvent.getByLabel (sourceByRefer_, matchedPartons);
    iEvent.getByLabel (sourceByValue_, flavourMatching);
    for (auto & e : *flavourMatching)
    {
        RefToBase<reco::Jet> r_jet = e.first;
        JetFlavour fl = e.second;
        const reco::Jet &jet = *(r_jet.get());
        if (isGoodJet(jet))
        {
            const double dRMuonJet = deltaR(jet, muon);
            if ( dRMuonJet < jet_lepton_dr )
            {
                edm::LogInfo("")
                        << "jet overlapping with muon: " << jet.pt()
                        << " " << muon.pt() << " " << jet.eta()
                        << " " << muon.eta() << " "
                        << jet.phi() << " " << muon.phi();
                continue;
            }
            reco::CompositeCandidate *cand = new reco::CompositeCandidate(
                0,
                jet.p4(),
                reco::Candidate::Point(0, 0, 0),
                fl.getFlavour()
            );
            jetColl->push_back(*cand);
            delete cand;
        }
    }

    if (jetColl->size() != 2)
    {
        LogInfo("") << "Wrong number of jets: " << jetColl->size();
        finalize();
        return false;
    }

    for (auto & jet : *jetColl)
    {
        edm::LogInfo("") << "Selected jet: " << jet.pt() << " " << jet.eta() << " " << jet.phi() << " " << jet.pdgId() << " " << deltaR(jet, muon);
    }

    reco::CompositeCandidate &jet1 = jetColl->at(0);
    reco::CompositeCandidate &jet2 = jetColl->at(1);
    const int id1 = abs(jet1.pdgId());
    const int id2 = abs(jet2.pdgId());
    auto define_b_l = [&] (int b, int l)
    {
        bJetColl->push_back(CompositeCandidate(jetColl->at(b - 1)));
        lightJetColl->push_back(CompositeCandidate(jetColl->at(l - 1)));
    };
    auto define_randomly = [&] ()
    {
        int r = rng->Integer(2);
        if (r == 0)
        {
            LogDebug("random") << "jet 1 is b-tag";
            define_b_l(1, 2);
        }
        else if (r == 1)
        {
            LogDebug("random") << "jet 2 is b-tag";
            define_b_l(2, 1);
        }
    };

    if (id1 == 5 && id2 == 5)
    {
        LogDebug("bchoice") << "dual b event";
        define_randomly();
    }
    else if (id1 == 5)
    {
        LogDebug("bchoice") << "b: jet 1 is b-tag";
        define_b_l(1, 2);
    }
    else if (id2 == 5)
    {
        LogDebug("bchoice") << "b: jet 2 is b-tag";
        define_b_l(2, 1);
    }
    else if (id1 == 4 && id2 == 4)
    {
        LogDebug("bchoice") << "c: dual c-jet event";
        define_randomly();
    }

    //One is c, other is not b or c
    else if (id1 == 4)
    {
        LogDebug("bchoice") << "c: jet 1 is b-tag";
        define_b_l(1, 2);
    }
    else if (id2 == 4)
    {
        LogDebug("bchoice") << "c: jet 2 is b-tag";
        define_b_l(2, 1);
    }
    else
    {
        //Both are light
        LogDebug("bchoice") << "c: dual light jet event";
        define_randomly();
    }

    edm::Handle<GenMETCollection> genMET;
    iEvent.getByLabel("genMetTrue", genMET);

    for (auto & met : *genMET)
    {
        reco::CompositeCandidate *cand = new reco::CompositeCandidate(
            0,
            met.p4(),
            reco::Candidate::Point(0, 0, 0),
            0
        );
        LogDebug("") << "MET: " << met.pt() << " " << met.phi();
        metColl->push_back(*cand);
        delete cand;
    }

    edm::LogInfo("topology") << "nMu=" << muColl->size() << " nJet=" << jetColl->size() << " nTag=" << bJetColl->size() << " nMET=" << metColl->size();

    LogDebug("") << "Putting products to event";
    iEvent.put(muColl, "selectedLeptons");
    iEvent.put(bJetColl, "selectedBTagJets");
    iEvent.put(lightJetColl, "selectedLightJets");
    iEvent.put(metColl, "selectedMETs");
    LogDebug("") << "Done putting products to event";
    return true;
}

// ------------ method called once each job just before starting event loop  ------------
void
GenInfoProducer::beginJob()
{
}

// ------------ method called once each job just after ending the event loop  ------------
void
GenInfoProducer::endJob()
{
}

// ------------ method called when starting to processes a run  ------------
bool
GenInfoProducer::beginRun(edm::Run &, edm::EventSetup const &)
{
    return true;
}

// ------------ method called when ending the processing of a run  ------------
bool
GenInfoProducer::endRun(edm::Run &, edm::EventSetup const &)
{
    return true;
}

// ------------ method called when starting to processes a luminosity block  ------------
bool
GenInfoProducer::beginLuminosityBlock(edm::LuminosityBlock &, edm::EventSetup const &)
{
    return true;
}

// ------------ method called when ending the processing of a luminosity block  ------------
bool
GenInfoProducer::endLuminosityBlock(edm::LuminosityBlock &, edm::EventSetup const &)
{
    return true;
}

// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void
GenInfoProducer::fillDescriptions(edm::ConfigurationDescriptions &descriptions)
{
    //The following says we do not know what parameters are allowed so do no validation
    // Please change this to state exactly what you do use, even if it is no parameters
    edm::ParameterSetDescription desc;
    desc.setUnknown();
    descriptions.addDefault(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(GenInfoProducer);






// metColl->push_back(*metCand);
// iEvent.put(metColl, "mymet");


// int nJets = 0;

// for ( JetFlavourMatchingCollection::const_iterator j  = theTagByValue->begin();
//         j != theTagByValue->end();
//         j ++ )
// {
//     RefToBase<Jet> aJet  = (*j).first;
//     const JetFlavour aFlav = (*j).second;

//     if (  (aJet.get()->et()) > 40 && fabs(aJet.get()->eta()) < 4.5 )
//     {
//         nJets++;
//         double etaJet = aJet.get()->eta();
//         double phiJet = aJet.get()->phi();

//         //            if (  (etaMuon-etaJet)<0.1 && (phiMuon-phiJet) < 0.1)  cout << " * ";
//         /*
//                      printf("[printJetFlavour] (pt,eta,phi) jet = %7.2f %6.3f %6.3f | parton = %7.2f %6.3f %6.3f | %4d\n",
//                      aJet.get()->et(),
//                      aJet.get()->eta(),
//                      aJet.get()->phi(),
//                      aFlav.getLorentzVector().pt(),
//                      aFlav.getLorentzVector().eta(),
//                      aFlav.getLorentzVector().phi(),
//                      aFlav.getFlavour() );
//         */
//     }
// }

// if (nGoodJets != 2 )
// {
//     LogInfo("jets") << "Wrong number of jets: " << nGoodJets;
//     return;
// }

/*

                            if ( dRMuonJet > 0.3 ) {
                 for ( JetFlavourMatchingCollection::const_iterator j  = theTagByValue->begin();
                                                     j != theTagByValue->end();
                                                     j ++ ) {
                                RefToBase<Jet> aJet  = (*j).first;
                                const JetFlavour aFlav = (*j).second;
                                     double etaJet = aJet.get()->eta();
                                     double phiJet = aJet.get()->phi();

                                 if ( abs(etaGen_-etaJet)<0.01 && abs(phiGen_-phiJet)<0.01 )
                                        cout << " Matched " << "etaGen_= " << etaGen_ << "  etaJet = " <<etaJet << "  "  << aFlav.getFlavour()  << endl;

                        }
                             }

                                 std::vector <const GenParticle*> mcparts = i_genjet->getGenConstituents ();
                                 for (unsigned i = 0; i < mcparts.size (); i++) {
                                     const GenParticle* mcpart = mcparts[i];
                                     int PDG = std::abs( mcpart->pdgId());
                                        //    cout << " part " << i << "  "<< PDG <<  "  pt " << mcpart->pt() <<   "  status " << mcpart->status() << endl;
                                }
                        }


        }
*/
