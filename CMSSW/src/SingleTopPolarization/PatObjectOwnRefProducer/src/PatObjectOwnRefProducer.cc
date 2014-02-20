// -*- C++ -*-
//
// Package:    PatObjectOwnRefProducer<T>
// Class:      PatObjectOwnRefProducer<T>
//
/**\class PatObjectOwnRefProducer<T> PatObjectOwnRefProducer.cc SingleTopPolarization/PatObjectOwnRefProducer/src/PatObjectOwnRefProducer.cc
 
 Description: [one line class summary]
 
 Implementation:
 [Notes on implementation]
 */
//
// Original Author:  Joosep Pata
//         Created:  Wed Jan 30 09:28:16 EET 2013
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
#include <DataFormats/PatCandidates/interface/Jet.h>
#include "FWCore/Utilities/interface/InputTag.h"
#include "FWCore/MessageLogger/interface/MessageLogger.h"


//
// class declaration
//
template <typename T>
class PatObjectOwnRefProducer : public edm::EDProducer {
public:
    explicit PatObjectOwnRefProducer(const edm::ParameterSet&);
    ~PatObjectOwnRefProducer();
    
    static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);
    
private:
    virtual void beginJob() ;
    virtual void produce(edm::Event&, const edm::EventSetup&);
    virtual void endJob() ;
    
    virtual void beginRun(edm::Run&, edm::EventSetup const&);
    virtual void endRun(edm::Run&, edm::EventSetup const&);
    virtual void beginLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&);
    virtual void endLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&);
    
    const edm::InputTag src;
    
    // ----------member data ---------------------------
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
template <typename T>
PatObjectOwnRefProducer<T>::PatObjectOwnRefProducer(const edm::ParameterSet& iConfig)
: src(iConfig.getParameter<edm::InputTag>("src"))
{
    produces<std::vector<T>>();
}


template <typename T>
PatObjectOwnRefProducer<T>::~PatObjectOwnRefProducer()
{
}

template <typename T>
void
PatObjectOwnRefProducer<T>::produce(edm::Event& iEvent, const edm::EventSetup& iSetup)
{
    using namespace edm;
    
    Handle<View<reco::Candidate>> inCollCand;
    Handle<View<T>> inColl;

    iEvent.getByLabel(src, inCollCand);
    iEvent.getByLabel(src, inColl);
    
    if(!inColl.isValid() || !inCollCand.isValid())
        throw cms::Exception("produce") << "Input collections were invalid: inColl=" << inColl.isValid() << " inCollCand=" << inCollCand.isValid();
    LogDebug("produce") << "Input collections have " << inColl->size() << ", " << inCollCand->size() << " items"; 
    
    std::auto_ptr<std::vector<T>> outColl(new std::vector<T>());
    
    unsigned int i = 0;
    for( auto& elem : *inColl) {
        T nElem(elem);
        nElem.addUserCand("original", inCollCand->ptrAt(i));
        outColl->push_back(nElem); 
        i++;
    }
    LogDebug("produce") << "Output collection has " << outColl->size() << " items"; 
    iEvent.put(outColl);
}

// ------------ method called once each job just before starting event loop  ------------
template <typename T>
void
PatObjectOwnRefProducer<T>::beginJob()
{
}

// ------------ method called once each job just after ending the event loop  ------------
template <typename T>
void
PatObjectOwnRefProducer<T>::endJob() {
}

// ------------ method called when starting to processes a run  ------------
template <typename T>
void
PatObjectOwnRefProducer<T>::beginRun(edm::Run&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a run  ------------
template <typename T>
void
PatObjectOwnRefProducer<T>::endRun(edm::Run&, edm::EventSetup const&)
{
}

// ------------ method called when starting to processes a luminosity block  ------------
template <typename T>
void
PatObjectOwnRefProducer<T>::beginLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a luminosity block  ------------
template <typename T>
void
PatObjectOwnRefProducer<T>::endLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&)
{
}

// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
template <typename T>
void
PatObjectOwnRefProducer<T>::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
    //The following says we do not know what parameters are allowed so do no validation
    // Please change this to state exactly what you do use, even if it is no parameters
    edm::ParameterSetDescription desc;
    desc.setUnknown();
    descriptions.addDefault(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(PatObjectOwnRefProducer<pat::Jet>);
