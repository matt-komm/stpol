// -*- C++ -*-
//
// Package:    TransferMatrixCreator
// Class:      TransferMatrixCreator
// 
/**\class TransferMatrixCreator TransferMatrixCreator.cc SingleTopPolarization/TransferMatrixCreator/src/TransferMatrixCreator.cc

 Description: [one line class summary]

 Implementation:
     [Notes on implementation]
*/
//
// Original Author:  
//         Created:  R okt   26 13:37:20 EEST 2012
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

#include "FWCore/ServiceRegistry/interface/Service.h"
#include "CommonTools/UtilAlgos/interface/TFileService.h"
#include <TMath.h>

#include "TH2.h"
//
// class declaration
//

class TransferMatrixCreator : public edm::EDAnalyzer {
   public:
      explicit TransferMatrixCreator(const edm::ParameterSet&);
      ~TransferMatrixCreator();

      static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);


   private:
      virtual void beginJob() ;
      virtual void analyze(const edm::Event&, const edm::EventSetup&);
      virtual void endJob() ;

      virtual void beginRun(edm::Run const&, edm::EventSetup const&);
      virtual void endRun(edm::Run const&, edm::EventSetup const&);
      virtual void beginLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&);
      virtual void endLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&);

      // ----------member data ---------------------------
      edm::InputTag src_;
      edm::InputTag trueSrc_;
      TH2D * matrix;

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
TransferMatrixCreator::TransferMatrixCreator(const edm::ParameterSet& iConfig) :
   src_( iConfig.getParameter<edm::InputTag>( "src" ) ),
   trueSrc_( iConfig.getParameter<edm::InputTag>( "trueSrc" ) )
{
   //now do what ever initialization is needed   
}


TransferMatrixCreator::~TransferMatrixCreator()
{
 
   // do anything here that needs to be done at desctruction time
   // (e.g. close files, deallocate resources etc.)

}


//
// member functions
//

// ------------ method called for each event  ------------
void
TransferMatrixCreator::analyze(const edm::Event& iEvent, const edm::EventSetup& iSetup)
{
   using namespace edm;

   double cosThetaTrue = TMath::QuietNaN();
   double cosThetaReco = TMath::QuietNaN();

   Handle<double> cosTheta;
   iEvent.getByLabel( src_, cosTheta );
   Handle<double> trueCosTheta;
   
   iEvent.getByLabel( trueSrc_, trueCosTheta );
   //std::cout << "matrix" << *cosTheta << " "<< *trueCosTheta<<std::endl;
   cosThetaTrue = *trueCosTheta;
   cosThetaReco = *cosTheta;
   matrix->Fill( *cosTheta, *trueCosTheta );

}


// ------------ method called once each job just before starting event loop  ------------
void 
TransferMatrixCreator::beginJob()
{
   edm::Service<TFileService> fs;
   matrix = fs->make<TH2D>( "matrix"  , "Transfer matrix", 50,  -1., 1., 50, -1., 1. );
}

// ------------ method called once each job just after ending the event loop  ------------
void 
TransferMatrixCreator::endJob() 
{
}

// ------------ method called when starting to processes a run  ------------
void 
TransferMatrixCreator::beginRun(edm::Run const&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a run  ------------
void 
TransferMatrixCreator::endRun(edm::Run const&, edm::EventSetup const&)
{
}

// ------------ method called when starting to processes a luminosity block  ------------
void 
TransferMatrixCreator::beginLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a luminosity block  ------------
void 
TransferMatrixCreator::endLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&)
{
}

// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void
TransferMatrixCreator::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(TransferMatrixCreator);
