// -*- C++ -*-
//
// Package:    ElectronLooseIDProducer
// Class:      ElectronLooseIDProducer
// 
/**\class ElectronLooseIDProducer ElectronLooseIDProducer.cc SingleTopPolarization/ElectronLooseIDProducer/src/ElectronLooseIDProducer.cc

 Description: [one line class summary]

 Implementation:
     [Notes on implementation]
*/
//
// Original Author:  Liis Rebane
//         Created:  Mon Jul 15 16:10:23 EEST 2013
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
#include <FWCore/Utilities/interface/InputTag.h>

//
// class declaration
//

class ElectronLooseIDProducer : public edm::EDProducer {
   public:
      explicit ElectronLooseIDProducer(const edm::ParameterSet&);
      ~ElectronLooseIDProducer();

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
ElectronLooseIDProducer::ElectronLooseIDProducer(const edm::ParameterSet& iConfig)
  : src(iConfig.getParameter<edm::InputTag>("src"))
{
  produces<std::vector<pat::Electron> >();

}


ElectronLooseIDProducer::~ElectronLooseIDProducer()
{
 
   // do anything here that needs to be done at desctruction time
   // (e.g. close files, deallocate resources etc.)

}


//
// member functions
//

// ------------ method called to produce the data  ------------
void
ElectronLooseIDProducer::produce(edm::Event& iEvent, const edm::EventSetup& iSetup)
{
   using namespace edm;
   Handle<View<pat::Electron>> els;
   iEvent.getByLabel(src, els);

   std::vector<pat::Electron> out;
   double looseID = 0;

   for (auto & el : *els){
     //Definition from   https://twiki.cern.ch/twiki/bin/view/CMS/EgammaCutBasedIdentification
     bool looseIDcut = (( fabs(el.superCluster()->eta()) < 1.479 && \
			  ( el.userFloat("dxy") < 0.04 && el.userFloat("dz") < 0.2 && \
			    el.hadronicOverEm() < 0.15 && el.sigmaIetaIeta() < 0.01 && \
			    fabs( el.deltaPhiSuperClusterTrackAtVtx() ) < 0.8 && \
			    fabs( el.deltaEtaSuperClusterTrackAtVtx() ) < 0.007)) || \
			( (fabs(el.superCluster()->eta()) > 1.479 && fabs(el.superCluster()->eta()) < 2.5) && \
			  ( el.userFloat("dxy") < 0.04 && el.userFloat("dz") < 0.2 && \
			    el.sigmaIetaIeta() < 0.03 && \
			    fabs( el.deltaPhiSuperClusterTrackAtVtx() ) < 0.7 && \
			    fabs( el.deltaEtaSuperClusterTrackAtVtx() ) < 0.01 )) \
			);

     pat::Electron elWithID(el);

     if( looseIDcut )
       looseID = 1;
     else
       looseID = 0;

     elWithID.addUserFloat("looseID", looseID);
     //     std::cout<<"loose ID = "<<elWithID.userFloat("looseID")<<std::endl;

     out.push_back(elWithID);
   }

   std::auto_ptr<std::vector<pat::Electron>> pOut(new std::vector<pat::Electron>(out));
   iEvent.put(pOut);
}

// ------------ method called once each job just before starting event loop  ------------
void 
ElectronLooseIDProducer::beginJob()
{
}

// ------------ method called once each job just after ending the event loop  ------------
void 
ElectronLooseIDProducer::endJob() {
}

// ------------ method called when starting to processes a run  ------------
void 
ElectronLooseIDProducer::beginRun(edm::Run&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a run  ------------
void 
ElectronLooseIDProducer::endRun(edm::Run&, edm::EventSetup const&)
{
}

// ------------ method called when starting to processes a luminosity block  ------------
void 
ElectronLooseIDProducer::beginLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a luminosity block  ------------
void 
ElectronLooseIDProducer::endLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&)
{
}

// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void
ElectronLooseIDProducer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(ElectronLooseIDProducer);
