// -*- C++ -*-
//
// Package:    BTagEfficiencyAnalyzer
// Class:      BTagEfficiencyAnalyzer
//
/**\class BTagEfficiencyAnalyzer BTagEfficiencyAnalyzer.cc SingleTopPolarization/BTagEfficiencyAnalyzer/src/BTagEfficiencyAnalyzer.cc

 Description: This class calculates the probabilities for b-tagging jets of various flavour, as dependent on the pt and eta of the jet.

 Implementation:
     The output is saved in a TFile as TH2F histograms.
*/
//
// Original Author:  Joosep Pata
//         Created:  Tue Jul 30 23:07:31 EEST 2013
// $Id$
//
//


// system include files
#include <memory>

// user include files
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/EDAnalyzer.h"

#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/Utilities/interface/InputTag.h"
#include "FWCore/MessageLogger/interface/MessageLogger.h"

const float eps = std::numeric_limits<float>::epsilon();
bool AreSame(float a, float b)
{
    return std::fabs(a - b) < eps;
}

//Binnings taken as the ones used for the scale factors by the b-tagging POG
static const unsigned int n_eta_bins = 4;
const Double_t eta_bins_low[n_eta_bins] =
{
    (Double_t)0.0,
    (Double_t)0.8,
    (Double_t)1.6,
    (Double_t)2.4
};

static const unsigned int n_pt_bins = 18;
const Double_t pt_bins_low[n_pt_bins] =
{
    0,
    20,
    30,
    40,
    50,
    60,
    70,
    80,
    100,
    120,
    160,
    210,
    260,
    320,
    400,
    500,
    600,
    800
};

class BTagEfficiencyAnalyzer : public edm::EDAnalyzer
{
public:
    explicit BTagEfficiencyAnalyzer(const edm::ParameterSet &);
    ~BTagEfficiencyAnalyzer();

    static void fillDescriptions(edm::ConfigurationDescriptions &descriptions);


private:
    virtual void beginJob() ;
    virtual void analyze(const edm::Event &, const edm::EventSetup &);
    virtual void endJob() ;

    virtual void beginRun(edm::Run const &, edm::EventSetup const &);
    virtual void endRun(edm::Run const &, edm::EventSetup const &);
    virtual void beginLuminosityBlock(edm::LuminosityBlock const &, edm::EventSetup const &);
    virtual void endLuminosityBlock(edm::LuminosityBlock const &, edm::EventSetup const &);

    const edm::InputTag jetPtSrc;
    const edm::InputTag jetEtaSrc;
    const edm::InputTag jetFlavourSrc;
    const edm::InputTag jetBDiscriminatorSrc;
    const edm::InputTag nJetSrc;
    const float bDiscriminatorWP;
};

BTagEfficiencyAnalyzer::BTagEfficiencyAnalyzer(const edm::ParameterSet &iConfig)
    : jetPtSrc(iConfig.getParameter<edm::InputTag>("jetPtSrc"))
    , jetEtaSrc(iConfig.getParameter<edm::InputTag>("jetEtaSrc"))
    , jetFlavourSrc(iConfig.getParameter<edm::InputTag>("jetFlavourSrc"))
    , jetBDiscriminatorSrc(iConfig.getParameter<edm::InputTag>("jetBDiscriminatorSrc"))
    , nJetSrc(iConfig.getParameter<edm::InputTag>("nJetSrc"))
    , bDiscriminatorWP(iConfig.getParameter<float>("bDiscriminatorWP"))
{
    std::map<int, TDirectory *> dirs;
    const std::vector<const char *> flavours;
    flavours.push_back("b");
    flavours.push_back("c");
    flavours.push_back("l");

    const Double_t *p_pt_bins_low = (const Double_t *)&pt_bins_low;
    const Double_t *p_eta_bins_low = (const Double_t *)&eta_bins_low;
    Int_t _n_pt_bins = (Int_t)n_pt_bins - 1;
    Int_t _n_eta_bins = (Int_t)n_eta_bins - 1;

    for (int i = 2; i <= 3; i++)
    {
        std::stringstream ss;
        ss << i << "J";
        dirs[i] = fs->make<TDirectory>(ss.string().c_str());
        for (auto & f : flavours)
        {
            std::stringstream ss;
            ss << "eff_" << f;
            const std::string hn = ss.string();
            dirs[i]->cd();
            fs->make<TH2F>(f.c_str(), f.c_str(), _n_pt_bins, p_pt_bins_low, _n_eta_bins, p_eta_bins_low);
        }
    }
}


BTagEfficiencyAnalyzer::~BTagEfficiencyAnalyzer()
{
}


void
BTagEfficiencyAnalyzer::analyze(const edm::Event &iEvent, const edm::EventSetup &iSetup)
{
    using namespace edm;

    auto &get = [&event](InputTag s)
    {
        Handle<std::vector<float>> h;
        event.getByLabel(s, h);
        return h.product();
    }


    auto jetPts = get(jetPtSrc);
    auto jetEtas = get(jetEtaSrc);
    auto jetFlavours = get(jetFlavourSrc);
    auto jetBDiscriminators = get(jetBDiscriminatorSrc);


}


void
BTagEfficiencyAnalyzer::beginJob()
{
}

void
BTagEfficiencyAnalyzer::endJob()
{
}

void
BTagEfficiencyAnalyzer::beginRun(edm::Run const &, edm::EventSetup const &)
{
}

void
BTagEfficiencyAnalyzer::endRun(edm::Run const &, edm::EventSetup const &)
{
}

void
BTagEfficiencyAnalyzer::beginLuminosityBlock(edm::LuminosityBlock const &, edm::EventSetup const &)
{
}

// ------------ method called when ending the processing of a luminosity block  ------------
void
BTagEfficiencyAnalyzer::endLuminosityBlock(edm::LuminosityBlock const &, edm::EventSetup const &)
{
}

// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void
BTagEfficiencyAnalyzer::fillDescriptions(edm::ConfigurationDescriptions &descriptions)
{
    edm::ParameterSetDescription desc;
    desc.setUnknown();
    descriptions.addDefault(desc);
}

v.begin(), v.end()DEFINE_FWK_MODULE(BTagEfficiencyAnalyzer);
