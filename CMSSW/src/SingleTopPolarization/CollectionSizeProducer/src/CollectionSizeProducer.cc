// -*- C++ -*-
//
// Package:    CollectionSizeProducer
// Class:      CollectionSizeProducer
// 
/**\class CollectionSizeProducer CollectionSizeProducer.cc SingleTopPolarization/CollectionSizeProducer/src/CollectionSizeProducer.cc

 Description: Produces an 'int' containing the size of the input collection.

 Implementation:
     [Notes on implementation]
*/
//
// Original Author:  Morten Piibeleht
//         Created:  Mon Oct  8 18:18:34 EEST 2012
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

#include <DataFormats/Common/interface/View.h>
#include <DataFormats/MuonReco/interface/Muon.h>
#include <DataFormats/PatCandidates/interface/Muon.h>
#include <DataFormats/EgammaCandidates/interface/Photon.h>
#include <DataFormats/VertexReco/interface/Vertex.h>

//
// class declaration
//

template<class T>
class CollectionSizeProducer : public edm::EDProducer {
   public:
      explicit CollectionSizeProducer(const edm::ParameterSet&);
      ~CollectionSizeProducer();

      static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);

   private:
      virtual void beginJob() ;
      virtual void produce(edm::Event&, const edm::EventSetup&);
      virtual void endJob() ;
      
      virtual void beginRun(edm::Run&, edm::EventSetup const&);
      virtual void endRun(edm::Run&, edm::EventSetup const&);
      virtual void beginLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&);
      virtual void endLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&);

      // ----------member data ---------------------------
      edm::InputTag src;
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
template<class T>
CollectionSizeProducer<T>::CollectionSizeProducer(const edm::ParameterSet& iConfig)
{
	src = iConfig.getParameter<edm::InputTag>("src");
	produces<int>();
}


template<class T>
CollectionSizeProducer<T>::~CollectionSizeProducer()
{
 
   // do anything here that needs to be done at desctruction time
   // (e.g. close files, deallocate resources etc.)

}


//
// member functions
//

// ------------ method called to produce the data  ------------
template<class T>
void CollectionSizeProducer<T>::produce(edm::Event& iEvent, const edm::EventSetup& iSetup)
{
   edm::Handle< edm::View<T> > vector;
   iEvent.getByLabel(src, vector);
	
   std::auto_ptr<int> outCount(new int(vector->size()));
   iEvent.put(outCount);
   
   //std::cout << "Count: " << *outCount << std::endl;
   //std::cout << "Count: " << (vector->size()) << std::endl;
   //LogDebug("Count: ") << vector->size();
}

// ------------ method called once each job just before starting event loop  ------------
template<class T>
void CollectionSizeProducer<T>::beginJob()
{
}

// ------------ method called once each job just after ending the event loop  ------------
template<class T>
void CollectionSizeProducer<T>::endJob() {
}

// ------------ method called when starting to processes a run  ------------
template<class T>
void CollectionSizeProducer<T>::beginRun(edm::Run&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a run  ------------
template<class T>
void CollectionSizeProducer<T>::endRun(edm::Run&, edm::EventSetup const&)
{
}

// ------------ method called when starting to processes a luminosity block  ------------
template<class T>
void CollectionSizeProducer<T>::beginLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a luminosity block  ------------
template<class T>
void CollectionSizeProducer<T>::endLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&)
{
}

// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
template<class T>
void CollectionSizeProducer<T>::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(CollectionSizeProducer<reco::Candidate>);
DEFINE_FWK_MODULE(CollectionSizeProducer<reco::Vertex>);
DEFINE_FWK_MODULE(CollectionSizeProducer<pat::Muon>);
DEFINE_FWK_MODULE(CollectionSizeProducer<reco::Muon>);
DEFINE_FWK_MODULE(CollectionSizeProducer<reco::Photon>);
