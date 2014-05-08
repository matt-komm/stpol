// -*- C++ -*-
//
// Package:    ElectronEfficiencyProducer
// Class:      ElectronEfficiencyProducer
//
/**\class ElectronEfficiencyProducer ElectronEfficiencyProducer.cc SingleTopPolarization/ElectronEfficiencyProducer/src/ElectronEfficiencyProducer.cc

 Description: [one line class summary]

 Implementation:
     [Notes on implementation]
*/
//
// Original Author:  Liis Rebane
//         Created:  Thu Apr 18 23:57:15 EEST 2013
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

#include <DataFormats/PatCandidates/interface/Electron.h>

#include "TMath.h"
//
// class declaration
//

class ElectronEfficiencyProducer : public edm::EDProducer
{
public:
    explicit ElectronEfficiencyProducer(const edm::ParameterSet &);
    ~ElectronEfficiencyProducer();

    static void fillDescriptions(edm::ConfigurationDescriptions &descriptions);

private:
    virtual void beginJob() ;
    virtual void produce(edm::Event &, const edm::EventSetup &);
    virtual void endJob() ;

    virtual void beginRun(edm::Run &, edm::EventSetup const &);
    virtual void endRun(edm::Run &, edm::EventSetup const &);
    virtual void beginLuminosityBlock(edm::LuminosityBlock &, edm::EventSetup const &);
    virtual void endLuminosityBlock(edm::LuminosityBlock &, edm::EventSetup const &);

    // ----------member data ---------------------------

    const edm::InputTag src;
    const float err_CONSERVATIVE;
    const bool applyConservativeSyst;
};

//
// constants, enums and typedefs
//


//
// static data member definitions
//

//
// constructors and destructor
//
ElectronEfficiencyProducer::ElectronEfficiencyProducer(const edm::ParameterSet &iConfig):
    src(iConfig.getParameter<edm::InputTag>("src"))
    , err_CONSERVATIVE(iConfig.getParameter<double>("SFError"))
    , applyConservativeSyst(iConfig.getParameter<bool>("applyConservativeSyst"))
{
    produces<double>("electronIdIsoWeight");
    produces<double>("electronIdIsoWeightUp");
    produces<double>("electronIdIsoWeightDown");
    produces<double>("electronTriggerWeight");
    produces<double>("electronTriggerWeightUp");
    produces<double>("electronTriggerWeightDown");
}


ElectronEfficiencyProducer::~ElectronEfficiencyProducer()
{

    // do anything here that needs to be done at desctruction time
    // (e.g. close files, deallocate resources etc.)

}


//
// member functions
//

// ------------ method called to produce the data  ------------
void
ElectronEfficiencyProducer::produce(edm::Event &iEvent, const edm::EventSetup &iSetup)
{
    using namespace edm;

    double weightIdIso = TMath::QuietNaN();
    double weightIdIsoUp = TMath::QuietNaN();
    double weightIdIsoDown = TMath::QuietNaN();
    double weightTrigger = TMath::QuietNaN();
    double weightTriggerUp = TMath::QuietNaN();
    double weightTriggerDown = TMath::QuietNaN();

    Handle<View<reco::Candidate> > electrons;
    iEvent.getByLabel(src, electrons);

    // Scale factors from AN-12-429. Need to be updated to Jan22 ReReco once available

    for (uint i = 0; i < electrons->size(); ++i)
    {
        const reco::Candidate &electron = electrons->at(i);

        if ( fabs(electron.eta()) < 0.8 )
        {
            if ( electron.pt() >= 30. && electron.pt() < 40.)
            {
                weightIdIso = 0.939;
                weightIdIsoUp = weightIdIso + 0.003;
                weightIdIsoDown = weightIdIso - 0.003;

                weightTrigger = 0.987;
                weightTriggerUp = weightTrigger + 0.012;
                weightTriggerDown = weightTrigger - 0.017;
            }
            if ( electron.pt() >= 40. && electron.pt() < 50.)
            {
                weightIdIso = 0.950;
                weightIdIsoUp = weightIdIso + 0.001;
                weightIdIsoDown = weightIdIso - 0.001;

                weightTrigger = 0.997;
                weightTriggerUp = weightTrigger + 0.001;
                weightTriggerDown = weightTrigger - 0.001;
            }
            if ( electron.pt() >= 50. && electron.pt() < 200.)
            {
                weightIdIso = 0.957;
                weightIdIsoUp = weightIdIso + 0.001;
                weightIdIsoDown = weightIdIso - 0.001;

                weightTrigger = 0.998;
                weightTriggerUp = weightTrigger + 0.002;
                weightTriggerDown = weightTrigger - 0.002;
            }
            if (electron.pt() >= 200.)
            {
                weightIdIso = 1; weightTrigger = 1;
                weightIdIsoUp = weightIdIso; weightIdIsoDown = weightIdIso; weightTriggerUp = weightTrigger; weightTriggerDown = weightTrigger;
            }
        }

        if ( fabs(electron.eta()) >= 0.8 && fabs(electron.eta()) < 1.478 )
        {
            if ( electron.pt() >= 30. && electron.pt() < 40.)
            {
                weightIdIso = 0.920;
                weightIdIsoUp = weightIdIso + 0.002;
                weightIdIsoDown = weightIdIso - 0.000;

                weightTrigger = 0.964;
                weightTriggerUp = weightTrigger + 0.002;
                weightTriggerDown = weightTrigger - 0.001;
            }
            if ( electron.pt() >= 40. && electron.pt() < 50.)
            {
                weightIdIso = 0.949;
                weightIdIsoUp = weightIdIso + 0.002;
                weightIdIsoDown = weightIdIso - 0.002;

                weightTrigger = 0.980;
                weightTriggerUp = weightTrigger + 0.001;
                weightTriggerDown = weightTrigger - 0.001;
            }
            if ( electron.pt() >= 50. && electron.pt() < 200.)
            {
                weightIdIso = 0.959;
                weightIdIsoUp = weightIdIso + 0.003;
                weightIdIsoDown = weightIdIso - 0.003;

                weightTrigger = 0.988;
                weightTriggerUp = weightTrigger + 0.002;
                weightTriggerDown = weightTrigger - 0.002;
            }
            if ( electron.pt() >= 200.)
            {
                weightIdIso = 1; weightTrigger = 1;
                weightIdIsoUp = weightIdIso; weightIdIsoDown = weightIdIso; weightTriggerUp = weightTrigger; weightTriggerDown = weightTrigger;
            }
        }

        if ( fabs(electron.eta()) >= 1.478 && fabs(electron.eta()) <= 2.5 )
        {
            if ( electron.pt() >= 30. && electron.pt() < 40.)
            {
                weightIdIso = 0.907;
                weightIdIsoUp = weightIdIso + 0.005;
                weightIdIsoDown = weightIdIso - 0.005;

                weightTrigger = 1.004;
                weightTriggerUp = weightTrigger + 0.006;
                weightTriggerDown = weightTrigger - 0.006;
            }
            if ( electron.pt() >= 40. && electron.pt() < 50.)
            {
                weightIdIso = 0.937;
                weightIdIsoUp = weightIdIso + 0.008;
                weightIdIsoDown = weightIdIso - 0.008;

                weightTrigger = 1.033;
                weightTriggerUp = weightTrigger + 0.007;
                weightTriggerDown = weightTrigger - 0.007;
            }
            if ( electron.pt() >= 50. && electron.pt() < 200.)
            {
                weightIdIso = 0.954;
                weightIdIsoUp = weightIdIso + 0.011;
                weightIdIsoDown = weightIdIso - 0.010;

                weightTrigger = 0.976;
                weightTriggerUp = weightTrigger + 0.015;
                weightTriggerDown = weightTrigger - 0.012;
            }
            if ( electron.pt() >= 200.)
            {
                weightIdIso = 1; weightTrigger = 1;
                weightIdIsoUp = weightIdIso; weightIdIsoDown = weightIdIso; weightTriggerUp = weightTrigger; weightTriggerDown = weightTrigger;
            }
        }
    }


    //Simply set the common variated scale factors using a conservative strategy
    if (applyConservativeSyst)
    {
        weightIdIsoUp = weightIdIso + err_CONSERVATIVE;
        weightIdIsoDown = weightIdIso - err_CONSERVATIVE;
        weightTriggerUp = weightTrigger + err_CONSERVATIVE;
        weightTriggerDown = weightTrigger - err_CONSERVATIVE;
    }

    iEvent.put(std::auto_ptr<double>(new double(weightIdIso)), "electronIdIsoWeight");
    iEvent.put(std::auto_ptr<double>(new double(weightIdIsoUp)), "electronIdIsoWeightUp");
    iEvent.put(std::auto_ptr<double>(new double(weightIdIsoDown)), "electronIdIsoWeightDown");
    iEvent.put(std::auto_ptr<double>(new double(weightTrigger)), "electronTriggerWeight");
    iEvent.put(std::auto_ptr<double>(new double(weightTriggerUp)), "electronTriggerWeightUp");
    iEvent.put(std::auto_ptr<double>(new double(weightTriggerDown)), "electronTriggerWeightDown");

}

// ------------ method called once each job just before starting event loop  ------------
void
ElectronEfficiencyProducer::beginJob()
{
}

// ------------ method called once each job just after ending the event loop  ------------
void
ElectronEfficiencyProducer::endJob()
{
}

// ------------ method called when starting to processes a run  ------------
void
ElectronEfficiencyProducer::beginRun(edm::Run &, edm::EventSetup const &)
{
}

// ------------ method called when ending the processing of a run  ------------
void
ElectronEfficiencyProducer::endRun(edm::Run &, edm::EventSetup const &)
{
}

// ------------ method called when starting to processes a luminosity block  ------------
void
ElectronEfficiencyProducer::beginLuminosityBlock(edm::LuminosityBlock &, edm::EventSetup const &)
{
}

// ------------ method called when ending the processing of a luminosity block  ------------
void
ElectronEfficiencyProducer::endLuminosityBlock(edm::LuminosityBlock &, edm::EventSetup const &)
{
}

// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void
ElectronEfficiencyProducer::fillDescriptions(edm::ConfigurationDescriptions &descriptions)
{
    //The following says we do not know what parameters are allowed so do no validation
    // Please change this to state exactly what you do use, even if it is no parameters
    edm::ParameterSetDescription desc;
    desc.setUnknown();
    descriptions.addDefault(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(ElectronEfficiencyProducer);
