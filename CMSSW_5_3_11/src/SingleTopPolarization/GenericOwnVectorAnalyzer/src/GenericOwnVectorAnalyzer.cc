// -*- C++ -*-
//
// Package:    GenericOwnVectorAnalyzer
// Class:      GenericOwnVectorAnalyzer
// 
/**\class GenericOwnVectorAnalyzer GenericOwnVectorAnalyzer.cc PhysicsTools/GenericOwnVectorAnalyzer/src/GenericOwnVectorAnalyzer.cc

 Description: The simplest example of an EDAnalyzer that gets a collection from the file and processes it in some fashion

 Implementation:
     [Notes on implementation]
*/
//
// Original Author:  
//         Created:  Wed Sep 19 15:55:51 EEST 2012
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

#include <DataFormats/PatCandidates/interface/Jet.h> //Requred for pat::Jet

#include <DataFormats/Candidate/interface/Candidate.h> //Required for reco::Candidate

#include <FWCore/Utilities/interface/InputTag.h> //Required for edm::InputTag

//
// class declaration
//

template <class T>
class GenericOwnVectorAnalyzer : public edm::EDAnalyzer {
   public:
      explicit GenericOwnVectorAnalyzer(const edm::ParameterSet&);
      ~GenericOwnVectorAnalyzer();

      static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);


   private:
      virtual void beginJob() ;
      virtual void analyze(const edm::Event&, const edm::EventSetup&);
      virtual void endJob() ;

      virtual void beginRun(edm::Run const&, edm::EventSetup const&);
      virtual void endRun(edm::Run const&, edm::EventSetup const&);
      virtual void beginLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&);
      virtual void endLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&);

      std::string objectOfInterest;

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

template <class T>
GenericOwnVectorAnalyzer<T>::GenericOwnVectorAnalyzer(const edm::ParameterSet& iConfig)

{
  objectOfInterest = iConfig.getUntrackedParameter<std::string>("interestingCollection");
}

template <class T>
GenericOwnVectorAnalyzer<T>::~GenericOwnVectorAnalyzer()
{
 
   // do anything here that needs to be done at desctruction time
   // (e.g. close files, deallocate resources etc.)

}


//
// member functions
//

// ------------ method called for each event  ------------
template <class T>
void
GenericOwnVectorAnalyzer<T>::analyze(const edm::Event& iEvent, const edm::EventSetup& iSetup)
{
   edm::Handle<edm::OwnVector<reco::Candidate,edm::ClonePolicy<reco::Candidate> > > objects;
   iEvent.getByLabel(objectOfInterest, objects);
   //for (edm::View<reco::Candidate>::const_iterator obj = objects->begin(); obj != objects->end(); obj++) {
   for (auto& obj : *objects) {
       //std::cout << "pt: " << (*obj).pt() << std::endl;
    const T* castObj = static_cast<const T*>(&obj);
    std::cout << "pt: " << castObj->pt() << " eta: " << castObj->eta() << " phi: " << castObj->phi() << std::endl;
    //std::cout << "bTag: " << jet->bDiscriminator("default") << std::endl;
   }
   
}


// ------------ method called once each job just before starting event loop  ------------
template <class T>
void 
GenericOwnVectorAnalyzer<T>::beginJob()
{
}

// ------------ method called once each job just after ending the event loop  ------------
template <class T>
void 
GenericOwnVectorAnalyzer<T>::endJob() 
{
}

// ------------ method called when starting to processes a run  ------------
template <class T>
void 
GenericOwnVectorAnalyzer<T>::beginRun(edm::Run const&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a run  ------------
template <class T>
void 
GenericOwnVectorAnalyzer<T>::endRun(edm::Run const&, edm::EventSetup const&)
{
}

// ------------ method called when starting to processes a luminosity block  ------------
template <class T>
void 
GenericOwnVectorAnalyzer<T>::beginLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a luminosity block  ------------
template <class T>
void 
GenericOwnVectorAnalyzer<T>::endLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&)
{
}

// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
template <class T>
void
GenericOwnVectorAnalyzer<T>::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);
}

//define this as a plug-in
typedef GenericOwnVectorAnalyzer<pat::Jet> JetOwnVectorSimpleAnalyzer;
typedef GenericOwnVectorAnalyzer<pat::Jet> CandOwnVectorSimpleAnalyzer;
DEFINE_FWK_MODULE(CandOwnVectorSimpleAnalyzer);
DEFINE_FWK_MODULE(JetOwnVectorSimpleAnalyzer);
