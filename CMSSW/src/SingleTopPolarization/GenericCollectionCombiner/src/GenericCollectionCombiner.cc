// -*- C++ -*-
//
// Package:    GenericCollectionCombiner
// Class:      GenericCollectionCombiner
// 
/**\class GenericCollectionCombiner GenericCollectionCombiner.cc SingleTopPolarization/GenericCollectionCombiner/src/GenericCollectionCombiner.cc

 Description: [one line class summary]

 Implementation:
     [Notes on implementation]
*/
//
// Original Author:  
//         Created:  Tue Oct  2 12:09:11 EEST 2012
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
#include "FWCore/Utilities/interface/InputTag.h"
#include "DataFormats/RecoCandidate/interface/RecoCandidate.h"
#include "FWCore/MessageLogger/interface/MessageLogger.h"

#include "DataFormats/Common/interface/Ptr.h"
#include "DataFormats/Common/interface/PtrVector.h"
#include <DataFormats/Candidate/interface/CompositeCandidate.h>


//
// class declaration
//

template <class T>
class GenericCollectionCombiner : public edm::EDProducer {
   public:
      explicit GenericCollectionCombiner(const edm::ParameterSet&);
      ~GenericCollectionCombiner();

      static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);

   private:
      virtual void beginJob() ;
      virtual void produce(edm::Event&, const edm::EventSetup&);
      virtual void endJob() ;
      
      virtual void beginRun(edm::Run&, edm::EventSetup const&);
      virtual void endRun(edm::Run&, edm::EventSetup const&);
      virtual void beginLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&);
      virtual void endLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&);

      const std::vector<std::string> collections;
      const uint minOut;
      const uint maxOut;
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
GenericCollectionCombiner<T>::GenericCollectionCombiner(const edm::ParameterSet& iConfig)
: collections(iConfig.getUntrackedParameter<std::vector<std::string> >("sources"))
, minOut(iConfig.getUntrackedParameter<uint>("minOut"))
, maxOut(iConfig.getUntrackedParameter<uint>("maxOut"))
{
   produces<std::vector<T> >();  
}

template <typename T>
GenericCollectionCombiner<T>::~GenericCollectionCombiner()
{
 
   // do anything here that needs to be done at desctruction time
   // (e.g. close files, deallocate resources etc.)

}


//
// member functions
//

// ------------ method called to produce the data  ------------
template <typename T>
void
GenericCollectionCombiner<T>::produce(edm::Event& iEvent, const edm::EventSetup& iSetup)
{
   using namespace edm;

   std::auto_ptr<std::vector<T > > pOut(new std::vector<T>());

   for (auto & c : collections) {
    Handle<View<reco::Candidate> > items;
    iEvent.getByLabel(c, items);
    if(items.isValid()) {
      LogDebug("produce()") << "Collection " << c << " has " << items->size() << " items";
      for (auto& item : *items) {
        const T* i = (T*)(item.clone());
        pOut->push_back(*i);
      }
    } else {
      LogDebug("produce()") << "Collection " << c << " does not exist in event";
    }
   }
   if((uint)(pOut->size()) < minOut) {
    LogError("produce()") << "Output collection has too few items: " << pOut->size() << "<" << minOut;
    pOut->clear(); 
    iEvent.put(pOut);
   }
   else if( (uint)(pOut->size()) > maxOut) {
    LogError("produce()") << "Output collection has too many items: " << pOut->size() << ">" << maxOut;
    pOut->clear(); 
    iEvent.put(pOut);
   }
   else {
    iEvent.put(pOut);
   }

/* this is an EventSetup example
   //Read SetupData from the SetupRecord in the EventSetup
   ESHandle<SetupData> pSetup;
   iSetup.get<SetupRecord>().get(pSetup);
*/
 
}

// ------------ method called once each job just before starting event loop  ------------
template <typename T>
void 
GenericCollectionCombiner<T>::beginJob()
{
}

// ------------ method called once each job just after ending the event loop  ------------
template <typename T>
void 
GenericCollectionCombiner<T>::endJob() {
}

// ------------ method called when starting to processes a run  ------------
template <typename T>
void 
GenericCollectionCombiner<T>::beginRun(edm::Run&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a run  ------------
template <typename T>
void 
GenericCollectionCombiner<T>::endRun(edm::Run&, edm::EventSetup const&)
{
}

// ------------ method called when starting to processes a luminosity block  ------------
template <typename T>
void 
GenericCollectionCombiner<T>::beginLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a luminosity block  ------------
template <typename T>
void 
GenericCollectionCombiner<T>::endLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&)
{
}

// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
template <typename T>
void
GenericCollectionCombiner<T>::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);
}

typedef GenericCollectionCombiner<reco::CompositeCandidate> CompositeCandCollectionCombiner;
//define this as a plug-in
DEFINE_FWK_MODULE(CompositeCandCollectionCombiner);
