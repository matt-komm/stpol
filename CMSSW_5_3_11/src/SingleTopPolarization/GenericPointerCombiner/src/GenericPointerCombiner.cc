// -*- C++ -*-
//
// Package:    GenericPointerCombiner
// Class:      GenericPointerCombiner
// 
/**\class GenericPointerCombiner GenericPointerCombiner.cc SingleTopPolarization/GenericPointerCombiner/src/GenericPointerCombiner.cc

 Description: Combines multiple View<inClass> type objects into a OwnVector<outClass> type collection, where outClass must be a superclass of inClass.

 Implementation:
     [Notes on implementation]
*/
//
// Original Author:  Joosep Pata <joosep.pata@cern.ch>
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

#include "DataFormats/Common/interface/Ref.h"
#include <DataFormats/Candidate/interface/CompositeCandidate.h>


//
// class declaration
//

template <class inClass, class outClass>
class GenericPointerCombiner : public edm::EDProducer {
   public:
      explicit GenericPointerCombiner(const edm::ParameterSet&);
      ~GenericPointerCombiner();

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
      const bool logErrors;
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
template <class inClass, class outClass>
GenericPointerCombiner<inClass, outClass>::GenericPointerCombiner(const edm::ParameterSet& iConfig)
: collections(iConfig.getParameter<std::vector<std::string> >("sources"))
, minOut(iConfig.getParameter<uint>("minOut"))
, maxOut(iConfig.getParameter<uint>("maxOut"))
, logErrors(iConfig.getParameter<bool>("logErrors"))
{
   produces<edm::OwnVector<outClass> >();  
}

template <class inClass, class outClass>
GenericPointerCombiner<inClass, outClass>::~GenericPointerCombiner()
{
}

template <class inClass, class outClass>
void
GenericPointerCombiner<inClass, outClass>::produce(edm::Event& iEvent, const edm::EventSetup& iSetup)
{
   using namespace edm;

   std::auto_ptr<edm::OwnVector<outClass> > pOut(new edm::OwnVector<outClass> ());

   for (auto & c : collections) {
    Handle<View<inClass> > items;
    iEvent.getByLabel(c, items);
    if(items.isValid()) {
      LogDebug("produce()") << "Collection " << c << " has " << items->size() << " items";

      uint idx = 0;
      for (auto& item : *items) {
        //edm::Ref<View<outClass> > *ref(new edm::Ref<View<outClass> >((const Handle<View<outClass> >&)items, idx));
        idx++;
        pOut->push_back(item);
      }
    } else {
      LogDebug("produce()") << "Collection " << c << " does not exist in event";
    }
   }
   if (logErrors) {
        if((uint)(pOut->size()) < minOut) {
         LogError("produce()") << "Output collection has too few items: " << pOut->size() << "<" << minOut;

        }
        else if( (uint)(pOut->size()) > maxOut) {
         LogError("produce()") << "Output collection has too many items: " << pOut->size() << ">" << maxOut;
        }
   }
   LogDebug("produce()") << "Combined collection has " << pOut->size() << " items" << std::endl;
   iEvent.put(pOut);
}

// ------------ method called once each job just before starting event loop  ------------
template <class inClass, class outClass>
void 
GenericPointerCombiner<inClass, outClass>::beginJob()
{
}

template <class inClass, class outClass>
void 
GenericPointerCombiner<inClass, outClass>::endJob() {
}

// ------------ method called when starting to processes a run  ------------
template <class inClass, class outClass>
void 
GenericPointerCombiner<inClass, outClass>::beginRun(edm::Run&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a run  ------------
template <class inClass, class outClass>
void 
GenericPointerCombiner<inClass, outClass>::endRun(edm::Run&, edm::EventSetup const&)
{
}

// ------------ method called when starting to processes a luminosity block  ------------
template <class inClass, class outClass>
void 
GenericPointerCombiner<inClass, outClass>::beginLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a luminosity block  ------------
template <class inClass, class outClass>
void 
GenericPointerCombiner<inClass, outClass>::endLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&)
{
}

// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
template <class inClass, class outClass>
void
GenericPointerCombiner<inClass, outClass>::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);
}

typedef GenericPointerCombiner<reco::Candidate, reco::Candidate> CandRefCombiner;
//define this as a plug-in
DEFINE_FWK_MODULE(CandRefCombiner);
