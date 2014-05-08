// -*- C++ -*-
//
// Package:    PUWeightProducer
// Class:      PUWeightProducer
//
/**\class PUWeightProducer PUWeightProducer.cc SingleTopPolarization/PUWeightProducer/src/PUWeightProducer.cc

 Description: This class calculates the nominal pile-up weight, taking into account the measured distribution of vertices and the number of true vertices at generation

 Implementation:
    Systematic variations are calculated by variating the minimum bias cross section (FIXME: explain)
    and having new effective data number of vertices distributions corresponding to the variations.
    The class reads the addPileupInfo structure from the EDM event and the number of _true_ vertices
    is accessed via PileupSummaryInfo::getTrueNumInteractions.
    Implemented as in https://twiki.cern.ch/twiki/bin/view/CMS/PileupMCReweightingUtilities

    Pile-up root files are calculated using util/calcDataPUHist.sh
*/
//
// Original Author:  Joosep Pata
//         Created:  Tue Feb 12 11:17:18 EET 2013
// $Id$
//
//

#include <memory>

// user include files
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/EDProducer.h"

#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"
#include "FWCore/ParameterSet/interface/FileInPath.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/MessageLogger/interface/MessageLogger.h"
#include "SimDataFormats/PileupSummaryInfo/interface/PileupSummaryInfo.h"
#include "PhysicsTools/Utilities/interface/LumiReWeighting.h"
#include "TMath.h"
#include <cmath>

class PUWeightProducer : public edm::EDProducer
{
public:
    explicit PUWeightProducer(const edm::ParameterSet &);
    ~PUWeightProducer();

    static void fillDescriptions(edm::ConfigurationDescriptions &descriptions);

private:
    virtual void beginJob() ;
    virtual void produce(edm::Event &, const edm::EventSetup &);
    virtual void endJob() ;

    virtual void beginRun(edm::Run &, edm::EventSetup const &);
    virtual void endRun(edm::Run &, edm::EventSetup const &);
    virtual void beginLuminosityBlock(edm::LuminosityBlock &, edm::EventSetup const &);
    virtual void endLuminosityBlock(edm::LuminosityBlock &, edm::EventSetup const &);
    const unsigned int maxVertices;
    std::vector<double> srcDistr;
    edm::LumiReWeighting *reweighter_nominal,*reweighter_down, *reweighter_up;
    edm::FileInPath weight_file_nominal;
    edm::FileInPath weight_file_up;
    edm::FileInPath weight_file_down;
};

PUWeightProducer::PUWeightProducer(const edm::ParameterSet &iConfig)
    : maxVertices(iConfig.getParameter<unsigned int>("maxVertices"))
    , srcDistr(iConfig.getParameter<std::vector<double>>("srcDistribution"))
    , weight_file_nominal(iConfig.getParameter<edm::FileInPath>("weightFileNominal"))
    , weight_file_up(iConfig.getParameter<edm::FileInPath>("weightFileUp"))
    , weight_file_down(iConfig.getParameter<edm::FileInPath>("weightFileDown"))
{
    srcDistr.resize(maxVertices);
    std::vector<float> _srcDistr;
    std::vector<float> _destDistrNominal;
    std::vector<float> _destDistrUp;
    std::vector<float> _destDistrDown;
    TFile* file_nominal = new TFile(weight_file_nominal.fullPath().c_str());
    TFile* file_up = new TFile(weight_file_up.fullPath().c_str());
    TFile* file_down = new TFile(weight_file_down.fullPath().c_str());
    for (unsigned int i = 0; i < maxVertices; i++)
    {
        _srcDistr.push_back((float)srcDistr[i]);
        _destDistrNominal.push_back(
            (float)
            (((TH1D*)(file_nominal->Get("pileup")))->GetBinContent(i + 1))
        );
        _destDistrUp.push_back(
            (float)
            (((TH1D*)(file_up->Get("pileup")))->GetBinContent(i + 1))
        );
        _destDistrDown.push_back(
            (float)
            (((TH1D*)(file_down->Get("pileup")))->GetBinContent(i + 1))
        );
    }

    produces<double>("PUWeightNtrue");
    produces<double>("PUWeightNtrueUp");
    produces<double>("PUWeightNtrueDown");

    produces<double>("PUWeightN0");
    produces<double>("nVertices0");
    produces<double>("nVerticesBXPlus1");
    produces<double>("nVerticesBXMinus1");
    produces<double>("nVerticesTrue");
    reweighter_nominal = new edm::LumiReWeighting(_srcDistr, _destDistrNominal);
    reweighter_up = new edm::LumiReWeighting(_srcDistr, _destDistrUp);
    reweighter_down = new edm::LumiReWeighting(_srcDistr, _destDistrDown);
}


PUWeightProducer::~PUWeightProducer()
{
}

void
PUWeightProducer::produce(edm::Event &iEvent, const edm::EventSetup &iSetup)
{
    using namespace edm;

    Handle<std::vector< PileupSummaryInfo > > PupInfo;
    iEvent.getByLabel(edm::InputTag("addPileupInfo"), PupInfo);
    std::vector<PileupSummaryInfo>::const_iterator PVI;

    float n0 = TMath::QuietNaN();
    float ntrue = TMath::QuietNaN();
    float nm1 = TMath::QuietNaN();
    float np1 = TMath::QuietNaN();
    int nPUs = 0;
    for (PVI = PupInfo->begin(); PVI != PupInfo->end(); ++PVI)
    {
        int BX = PVI->getBunchCrossing();
        nPUs++;
        if (BX == 0)
        {
            n0 = PVI->getPU_NumInteractions();
            ntrue = PVI->getTrueNumInteractions();
            LogDebug("produce()") << "true num int = " << ntrue;
        }
        else if (BX == 1)
        {
            np1 = PVI->getPU_NumInteractions();
        }
        else if (BX == -1)
        {
            nm1 = PVI->getPU_NumInteractions();
        }
    }
    LogDebug("produce()") << "nPUs=" << nPUs;

    if (std::isnan(ntrue)) {
        LogInfo("NAN") << "Ntrue=" << ntrue; 
    }
    if (std::isnan(n0)) {
        LogInfo("NAN") << "N0=" << n0; 
    }

    double puWeight_n0 = TMath::QuietNaN();
    double puWeight_ntrue = TMath::QuietNaN();
    double puWeight_ntrue_up = TMath::QuietNaN();
    double puWeight_ntrue_down = TMath::QuietNaN();
    if (nPUs > 0 && n0 > 0)
    {
        puWeight_n0 = reweighter_nominal->weight(n0);
    }
    if (nPUs > 0 && ntrue > 0)
    {
        puWeight_ntrue = reweighter_nominal->weight(ntrue);
        puWeight_ntrue_up = reweighter_up->weight(ntrue);
        puWeight_ntrue_down = reweighter_down->weight(ntrue);
    }
    if (std::isnan(puWeight_ntrue)) {
        LogDebug("NAN") << "puWeight_ntrue=" << puWeight_ntrue;
    }
    if (std::isnan(puWeight_n0)) {
        LogDebug("NAN") << "puWeight_n0=" << puWeight_n0;
    }

    LogDebug("produce()") << "calculated PU weight nominal_n0=" << puWeight_n0 << " nominal_ntrue=" << puWeight_ntrue << " up=" << puWeight_ntrue_up << " down=" << puWeight_ntrue_down;
    iEvent.put(std::auto_ptr<double>(new double(n0)), "nVertices0");
    iEvent.put(std::auto_ptr<double>(new double(np1)), "nVerticesBXPlus1");
    iEvent.put(std::auto_ptr<double>(new double(nm1)), "nVerticesBXMinus1");
    iEvent.put(std::auto_ptr<double>(new double(ntrue)), "nVerticesTrue");
    iEvent.put(std::auto_ptr<double>(new double(puWeight_ntrue)), "PUWeightNtrue");
    iEvent.put(std::auto_ptr<double>(new double(puWeight_ntrue_up)), "PUWeightNtrueUp");
    iEvent.put(std::auto_ptr<double>(new double(puWeight_ntrue_down)), "PUWeightNtrueDown");
    iEvent.put(std::auto_ptr<double>(new double(puWeight_n0)), "PUWeightN0");


}

// ------------ method called once each job just before starting event loop  ------------
void
PUWeightProducer::beginJob()
{
}

// ------------ method called once each job just after ending the event loop  ------------
void
PUWeightProducer::endJob()
{
}

// ------------ method called when starting to processes a run  ------------
void
PUWeightProducer::beginRun(edm::Run &, edm::EventSetup const &)
{
}

// ------------ method called when ending the processing of a run  ------------
void
PUWeightProducer::endRun(edm::Run &, edm::EventSetup const &)
{
}

// ------------ method called when starting to processes a luminosity block  ------------
void
PUWeightProducer::beginLuminosityBlock(edm::LuminosityBlock &, edm::EventSetup const &)
{
}

// ------------ method called when ending the processing of a luminosity block  ------------
void
PUWeightProducer::endLuminosityBlock(edm::LuminosityBlock &, edm::EventSetup const &)
{
}

// ------------ method fills "descriptions" with the allowed parameters for the module  ------------
void
PUWeightProducer::fillDescriptions(edm::ConfigurationDescriptions &descriptions)
{
    //The following says we do not know what parameters are allowed so do no validation
    // Please change this to state exactly what you do use, even if it is no parameters
    edm::ParameterSetDescription desc;
    desc.setUnknown();
    descriptions.addDefault(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(PUWeightProducer);
