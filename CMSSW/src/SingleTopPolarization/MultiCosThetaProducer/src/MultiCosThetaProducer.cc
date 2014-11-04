// -*- C++ -*-
//
// Package:    MultiCosThetaProducer
// Class:      MultiCosThetaProducer
// 
/**\class MultiCosThetaProducer MultiCosThetaProducer.cc test/MultiCosThetaProducer/src/MultiCosThetaProducer.cc

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

#include <DataFormats/Candidate/interface/Candidate.h>
#include "FWCore/Utilities/interface/InputTag.h"
#include "Math/GenVector/VectorUtil.h"
#include <TMath.h>


class MultiCosThetaProducer: 
    public edm::EDProducer 
{
    public:
        explicit MultiCosThetaProducer(const edm::ParameterSet&);
        ~MultiCosThetaProducer();

        static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);

    private:
        virtual void produce(edm::Event&, const edm::EventSetup&);

    struct CosThetaCalculation
    {
        std::string name;
        edm::InputTag restFrameInput;
        edm::InputTag particleInput1;
        edm::InputTag particleInput2;
        CosThetaCalculation(
            const std::string& name,
            const edm::InputTag& restFrameInput,
            const edm::InputTag& particleInput1,
            const edm::InputTag& particleInput2
        ):
            name(name),
            restFrameInput(restFrameInput),
            particleInput1(particleInput1),
            particleInput2(particleInput2)
        {}
            
    };
    
    std::vector<CosThetaCalculation> _calculations;


};


MultiCosThetaProducer::MultiCosThetaProducer(const edm::ParameterSet& iConfig)
{
    const std::vector<std::string> psetNames = iConfig.getParameterNamesForType<edm::ParameterSet>();
    for (unsigned int iname=0; iname< psetNames.size(); ++iname)
    {
        const std::string& name = psetNames[iname];
        const edm::ParameterSet& localConf = iConfig.getParameter<edm::ParameterSet>(name);
        const edm::InputTag& restFrameInput = localConf.getParameter<edm::InputTag>("restFrame");
        const std::vector<edm::InputTag>& particleInputs = localConf.getParameter<std::vector<edm::InputTag>>("particles");
        if (particleInputs.size()!=2)
        {
            edm::LogWarning("MultiCosThetaProducer::c'tor")<<"particles need vector of InputTag of size 2: size="<<particleInputs.size()<<" was configured";
            continue;
        }
        _calculations.push_back(CosThetaCalculation(name,restFrameInput,particleInputs[0],particleInputs[1]));
        produces<double>(name);
    }

}


MultiCosThetaProducer::~MultiCosThetaProducer()
{
}

void
MultiCosThetaProducer::produce(edm::Event& iEvent, const edm::EventSetup& iSetup)
{
    for (const CosThetaCalculation& calculation: _calculations)
    {
        edm::Handle<edm::View<reco::Candidate>> restFrameCollection;
        bool doBoosting=true;
       
        if (!iEvent.getByLabel(calculation.restFrameInput,restFrameCollection) || restFrameCollection->size()==0)
        {
            edm::LogWarning("MultiCosThetaProducer::produce()")<<"no particles for restframe boost found. Skip boosting!";
            doBoosting=false;
        }
        if (restFrameCollection->size()>1)
        {
            edm::LogWarning("MultiCosThetaProducer::produce()")<<"multiple particles for restframe boost found. Will only use the first one!";
        }
        
        edm::Handle<edm::View<reco::Candidate>> particle1Collection;
        edm::Handle<edm::View<reco::Candidate>> particle2Collection;
        
        if (! iEvent.getByLabel(calculation.particleInput1,particle1Collection) || !iEvent.getByLabel(calculation.particleInput2,particle2Collection) || particle1Collection->size()==0 || particle2Collection->size()==0)
        {
            edm::LogWarning("MultiCosThetaProducer::produce()")<<"no particles for angle calculation found. Skip entire calculation!";
            std::auto_ptr<double> pCosTheta(new double(-2));
            iEvent.put(pCosTheta, calculation.name);
            continue;
        }
        if (particle1Collection->size()>1 || particle2Collection->size()>1)
        {
            edm::LogWarning("MultiCosThetaProducer::produce()")<<"multiple particles for restframe boost found. Will only use the first ones!";
        }
        
        ROOT::Math::LorentzVector<ROOT::Math::PxPyPzE4D<double> > particle1Vector;
        ROOT::Math::LorentzVector<ROOT::Math::PxPyPzE4D<double> > particle2Vector;
        if (doBoosting)
        {
             particle1Vector=ROOT::Math::VectorUtil::boost(particle1Collection->at(0).p4(), restFrameCollection->at(0).p4().BoostToCM());
             particle2Vector=ROOT::Math::VectorUtil::boost(particle2Collection->at(0).p4(), restFrameCollection->at(0).p4().BoostToCM());
        }
        else
        {
            particle1Vector=particle1Collection->at(0).p4();
            particle2Vector=particle2Collection->at(0).p4();
        }

        double cosTheta = ROOT::Math::VectorUtil::CosTheta(particle1Vector.Vect(),particle2Vector.Vect());
        std::auto_ptr<double> pCosTheta(new double(cosTheta));
        iEvent.put(pCosTheta, calculation.name);
    }

} 


void
MultiCosThetaProducer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) 
{

    edm::ParameterSetDescription desc;
    desc.setUnknown();
    descriptions.addDefault(desc);
}


DEFINE_FWK_MODULE(MultiCosThetaProducer);
