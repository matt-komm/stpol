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

    double err = 0.02;

    Handle<View<reco::Candidate> > electrons;
    iEvent.getByLabel(src, electrons);

    // Temporarily switch all SFs to 1 (until the Jan22 reprocessing SFs are ready) and apply a conservative 2% uncertainty

    for (uint i = 0; i < electrons->size(); ++i)
    {
        const reco::Candidate &electron = electrons->at(i);

        if ( fabs(electron.eta()) < 0.8 )
        {
            if ( electron.pt() >= 30. && electron.pt() < 40.)
            {
                weightIdIso = 1;
                weightIdIsoUp = weightIdIso + err;
                weightIdIsoDown = weightIdIso - err;

                weightTrigger = 1;
                weightTriggerUp = weightTrigger + err;
                weightTriggerDown = weightTrigger - err;
            }
            if ( electron.pt() >= 40. && electron.pt() < 50.)
            {
                weightIdIso = 1;
                weightIdIsoUp = weightIdIso + err;
                weightIdIsoDown = weightIdIso - err;

                weightTrigger = 1;
                weightTriggerUp = weightTrigger + err;
                weightTriggerDown = weightTrigger - err;
            }
            if ( electron.pt() >= 50. && electron.pt() < 200.)
            {
                weightIdIso = 1;
                weightIdIsoUp = weightIdIso + err;
                weightIdIsoDown = weightIdIso - err;

                weightTrigger = 1;
                weightTriggerUp = weightTrigger + err;
                weightTriggerDown = weightTrigger - err;
            }
            if (electron.pt() >= 200.)
            {
                weightIdIso = 1;
                weightIdIsoUp = weightIdIso + err;
                weightIdIsoDown = weightIdIso - err;

                weightTrigger = 1;
                weightTriggerUp = weightTrigger + err;
                weightTriggerDown = weightTrigger - err;
            }
        }

        if ( fabs(electron.eta()) >= 0.8 && fabs(electron.eta()) < 1.478 )
        {
            if ( electron.pt() >= 30. && electron.pt() < 40.)
            {
                weightIdIso = 1;
                weightIdIsoUp = weightIdIso + err;
                weightIdIsoDown = weightIdIso - err;

                weightTrigger = 1;
                weightTriggerUp = weightTrigger + err;
                weightTriggerDown = weightTrigger - err;
            }
            if ( electron.pt() >= 40. && electron.pt() < 50.)
            {
                weightIdIso = 1;
                weightIdIsoUp = weightIdIso + err;
                weightIdIsoDown = weightIdIso - err;

                weightTrigger = 1;
                weightTriggerUp = weightTrigger + err;
                weightTriggerDown = weightTrigger - err;
            }
            if ( electron.pt() >= 50. && electron.pt() < 200.)
            {
                weightIdIso = 1;
                weightIdIsoUp = weightIdIso + err;
                weightIdIsoDown = weightIdIso - err;

                weightTrigger = 1;
                weightTriggerUp = weightTrigger + err;
                weightTriggerDown = weightTrigger - err;
            }
            if ( electron.pt() >= 200.)
            {
                weightIdIso = 1;
                weightIdIsoUp = weightIdIso + err;
                weightIdIsoDown = weightIdIso - err;

                weightTrigger = 1;
                weightTriggerUp = weightTrigger + err;
                weightTriggerDown = weightTrigger - err;
            }
        }

        if ( fabs(electron.eta()) >= 1.478 && fabs(electron.eta()) <= 2.5 )
        {
            if ( electron.pt() >= 30. && electron.pt() < 40.)
            {
                weightIdIso = 1;
                weightIdIsoUp = weightIdIso + err;
                weightIdIsoDown = weightIdIso - err;

                weightTrigger = 1;
                weightTriggerUp = weightTrigger + err;
                weightTriggerDown = weightTrigger - err;
            }
            if ( electron.pt() >= 40. && electron.pt() < 50.)
            {
                weightIdIso = 1;
                weightIdIsoUp = weightIdIso + err;
                weightIdIsoDown = weightIdIso - err;

                weightTrigger = 1;
                weightTriggerUp = weightTrigger + err;
                weightTriggerDown = weightTrigger - err;
            }
            if ( electron.pt() >= 50. && electron.pt() < 200.)
            {
                weightIdIso = 1;
                weightIdIsoUp = weightIdIso + err;
                weightIdIsoDown = weightIdIso - err;

                weightTrigger = 1;
                weightTriggerUp = weightTrigger + err;
                weightTriggerDown = weightTrigger - err;
            }
            if ( electron.pt() >= 200.)
            {
                weightIdIso = 1;
                weightIdIsoUp = weightIdIso + err;
                weightIdIsoDown = weightIdIso - err;

                weightTrigger = 1;
                weightTriggerUp = weightTrigger + err;
                weightTriggerDown = weightTrigger - err;
            }
        }

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
