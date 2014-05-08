// -*- C++ -*-
//
// Package:    ParticleComparer
// Class:      ParticleComparer
// 
/**\class ParticleComparer ParticleComparer.cc SingleTopPolarization/ParticleComparer/src/ParticleComparer.cc

 Description: [one line class summary]

 Implementation:
     [Notes on implementation]
*/
//
// Original Author:  
//         Created:  R okt   26 16:11:29 EEST 2012
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

#include <DataFormats/Candidate/interface/Candidate.h> 

#include "FWCore/ServiceRegistry/interface/Service.h"
#include "CommonTools/UtilAlgos/interface/TFileService.h"
#include "FWCore/Utilities/interface/InputTag.h"

#include "TH2.h"
//
// class declaration
//

class ParticleComparer : public edm::EDAnalyzer {
   public:
      explicit ParticleComparer(const edm::ParameterSet&);
      ~ParticleComparer();

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
      TH2D * matrixPt;
      TH2D * matrixEta;
      TH2D * matrixPhi;
      TH2D * matrixMass;
      edm::InputTag src_;
      edm::InputTag trueSrc_;
      const double maxMass;
      
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
ParticleComparer::ParticleComparer(const edm::ParameterSet& iConfig) :
   src_( iConfig.getParameter<edm::InputTag>( "src" ) ),
   trueSrc_( iConfig.getParameter<edm::InputTag>( "trueSrc" ) ),
   maxMass(iConfig.getUntrackedParameter<double>("maxMass"))
{
   //now do what ever initialization is needed

}


ParticleComparer::~ParticleComparer()
{
 
   // do anything here that needs to be done at desctruction time
   // (e.g. close files, deallocate resources etc.)

}


//
// member functions
//

// ------------ method called for each event  ------------
void
ParticleComparer::analyze(const edm::Event& iEvent, const edm::EventSetup& iSetup)
{
   using namespace edm;

   Handle<View<reco::Candidate> > particles;
   Handle<View<reco::Candidate> > trueParticles;
   iEvent.getByLabel(src_, particles);
   iEvent.getByLabel(trueSrc_, trueParticles);
   //if (tops->size() > 0 && jets->size() > 0 && leptons->size() > 0) {
   //if (tops->size()>1 || jets->size() > 1 || leptons->size() > 1) {
   //   LogError("produce()") << "Number of items in input collections is ambigous: tops " << tops->size() << " jets " << jets->size() << " leptons " << leptons->size();
    //}
    
    if (particles->size() == 1 && trueParticles->size() == 1){
       const reco::Candidate& particle = particles->at(0);
       const reco::Candidate& trueParticle = trueParticles->at(0);
       //std::cout << particle.eta() << " " << trueParticle.eta() <<std::endl;
       matrixPt->Fill( particle.pt(), trueParticle.pt() );
       matrixPhi->Fill( particle.phi(), trueParticle.phi() );
       matrixEta->Fill( particle.eta(), trueParticle.eta() );
       matrixMass->Fill( particle.mass(), trueParticle.mass() );
   }
}


// ------------ method called once each job just before starting event loop  ------------
void 
ParticleComparer::beginJob()
{
   edm::Service<TFileService> fs;
   matrixPt = fs->make<TH2D>( "matrixPt"  , "Transfer matrix Pt", 50,  0, 300, 50, 0, 300 );
   matrixPhi = fs->make<TH2D>( "matrixPhi"  , "Transfer matrix Phi", 50,  -2.5, 2.5, 50, -2.5, 2.5 );
   matrixEta = fs->make<TH2D>( "matrixEta"  , "Transfer matrix Eta", 50,  -6, 6, 50, -6, 6 );
   matrixMass = fs->make<TH2D>( "matrixMass"  , "Transfer matrix Mass", 50,  0, maxMass, 50, 0, maxMass );
}

// ------------ method called once each job just after ending the event loop  ------------
void 
ParticleComparer::endJob() 
{
}

// ------------ method called when starting to processes a run  ------------
void 
ParticleComparer::beginRun(edm::Run const&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a run  ------------
void 
ParticleComparer::endRun(edm::Run const&, edm::EventSetup const&)
{
}

// ------------ method called when starting to processes a luminosity block  ------------
void 
ParticleComparer::beginLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a luminosity block  ------------
void 
ParticleComparer::endLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&)
{
}

// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void
ParticleComparer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(ParticleComparer);
