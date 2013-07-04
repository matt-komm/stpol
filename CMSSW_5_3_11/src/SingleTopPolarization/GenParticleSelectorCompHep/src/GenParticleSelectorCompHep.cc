// -*- C++ -*-
//
// Package:    GenParticleSelectorCompHep
// Class:      GenParticleSelectorCompHep
// 
/**\class GenParticleSelectorCompHep GenParticleSelectorCompHep.cc SingleTopPolarization/GenParticleSelectorCompHep/src/GenParticleSelectorCompHep.cc

 Description: [one line class summary]

 Implementation:
     [Notes on implementation]
*/
//
// Original Author:  Andres Tiko
//         Created:  N apr    4 11:47:22 EEST 2013
// $Id$
//
//


// system include files
#include <memory>
#include <TMath.h>

// user include files
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/EDProducer.h"

#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "DataFormats/HepMCCandidate/interface/GenParticle.h"

#include "DataFormats/PatCandidates/interface/Jet.h"

using namespace edm;
using namespace std;
using namespace reco;

//
// class declaration
//

class GenParticleSelectorCompHep : public edm::EDProducer {
   public:
      explicit GenParticleSelectorCompHep(const edm::ParameterSet&);
      ~GenParticleSelectorCompHep();

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
      int count_mu;
      int count_antimu;
      int count_b;
      int count_nu;
      int count_events;
      int count_other;
      int count_stuff;
     
      bool has_mu;
      bool has_nu;
      bool has_b;
      bool has_lj;
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
GenParticleSelectorCompHep::GenParticleSelectorCompHep(const edm::ParameterSet& iConfig)
{
   //produces<std::vector<GenParticle>>("trueTop");
   produces<std::vector<GenParticle>>("trueLightJet");
   produces<std::vector<GenParticle>>("trueBJet");
   produces<std::vector<GenParticle>>("trueLepton");
   produces<std::vector<GenParticle>>("trueNeutrino");
   produces<int>("trueLeptonPdgId");
   //register your products
/* Examples
   produces<ExampleData2>();

   //if do put with a label
   produces<ExampleData2>("label");
 
   //if you want to put into the Run
   produces<ExampleData2,InRun>();
*/
   //now do what ever other initialization is needed
   /*count_t = 0;
   count_other = 0;
   
   count_over3 = 0;
   count_diff = 0;
   for(size_t i = 0; i < 200; ++ i){
      for(size_t j = 0; j < 200; ++ j){
         fstateMothers[i][j] = 0;
         fstateSiblings[i][j] = 0;
      }
   }*/
   count_events = 0;
   count_mu = 0;
   count_antimu = 0;
   count_other = 0;
   count_stuff = 0;
  
}


GenParticleSelectorCompHep::~GenParticleSelectorCompHep()
{
 
   // do anything here that needs to be done at desctruction time
   // (e.g. close files, deallocate resources etc.)

}


//
// member functions
//

// ------------ method called to produce the data  ------------
void
GenParticleSelectorCompHep::produce(edm::Event& iEvent, const edm::EventSetup& iSetup)
{
   //using namespace edm;
   //count_siblings = 0;
   //which_sibling = 0;
   //s1_mother1 = s1_mother2 = s2_mother1 = s2_mother2 = 0;
   Handle<GenParticleCollection> genParticles;
   iEvent.getByLabel("genParticles", genParticles);
   count_events++;
   count_nu = 0;
   //count_mu = 0;
   //count_antimu = 0;

   //std::auto_ptr<std::vector<GenParticle> > outTops(new std::vector<GenParticle>());
   std::auto_ptr<std::vector<GenParticle> > outLightJets(new std::vector<GenParticle>());
   std::auto_ptr<std::vector<GenParticle> > outBJets(new std::vector<GenParticle>());
   std::auto_ptr<std::vector<GenParticle> > outLeptons(new std::vector<GenParticle>());
   std::auto_ptr<std::vector<GenParticle> > outNeutrinos(new std::vector<GenParticle>());

   int trueLeptonPdgId = TMath::QuietNaN();
   //GenParticle* lightJet;
   GenParticle* lightJet;
   GenParticle* bJet;
   GenParticle* lepton;
   GenParticle* neutrino;   
   GenParticle *lj1, *lj2;
   GenParticle *x;
   const GenParticle * dau;
   int which_light = 0;

   for(size_t i = 0; i < genParticles->size(); ++ i) {
      has_mu = false;
      has_nu = false;
      has_b = false;
      has_lj = false;
      const GenParticle & p = (*genParticles)[i];
      int id = p.pdgId();
      int st = p.status();  
      const GenParticle * mom;// = p.mother();
      double pt = p.pt(), eta = p.eta(), phi = p.phi(), mass = p.mass();
      double vx = p.vx(), vy = p.vy(), vz = p.vz();
      int charge = p.charge();
      int n = p.numberOfDaughters();
      if((id == 13 || id == -13) && st ==3){
         cout << "P: " <<id << " " << st << endl;
         mom = (GenParticle*)p.mother(0);  //particle has 2 mothers with the same daughters, just select the first one
         for(size_t mi = 0; mi < mom->numberOfDaughters(); ++ mi){
               dau = (GenParticle*)mom->daughter(mi);
               if(dau->status()==3){
                  if(abs(dau->pdgId())==13){
                     has_mu = true;
                     lepton = const_cast<reco::GenParticle*>(dau);                     
                  }
                  else if(abs(dau->pdgId())==14){
                     has_nu = true;
                     neutrino = const_cast<reco::GenParticle*>(dau);
                  }
                  else if(abs(dau->pdgId())==5){
                     has_b = true;
                     bJet = const_cast<reco::GenParticle*>(dau);
                  }
                  else if(abs(dau->pdgId())<5){
                     if(!has_lj){
                        lj1 = const_cast<reco::GenParticle*>(dau);
                        which_light = 1;
                     }
                     else{
                        lj2 = const_cast<reco::GenParticle*>(dau);
                        if(abs(dau->pdgId())<lj1->pdgId())
                           which_light = 2;
                        else
                           which_light = 1;
                     }
                     has_lj = true;                
                  }
               } 
         }
         if(has_mu && has_nu && has_b){            
            if(lepton->pdgId()==13)
               count_antimu++;
            else if(lepton->pdgId()==-13)
               count_mu++;
            else{
               count_other++;
            }
            outLeptons->push_back(*lepton);
            outNeutrinos->push_back(*neutrino);
            outBJets->push_back(*bJet);
            if(which_light == 1){
               outLightJets->push_back(*lj1);
            }
            else if(which_light == 2){
               outLightJets->push_back(*lj2);
            }
         }
         else
            count_stuff++;         
     }
   }

   iEvent.put(outLeptons, "trueLepton");
   iEvent.put(outLightJets, "trueLightJet");
   iEvent.put(outBJets, "trueBJet");
   iEvent.put(outNeutrinos, "trueNeutrino");
   iEvent.put(std::auto_ptr<int>(new int(lepton->pdgId())), "trueLeptonPdgId");
 
}

// ------------ method called once each job just before starting event loop  ------------
void 
GenParticleSelectorCompHep::beginJob()
{
}

// ------------ method called once each job just after ending the event loop  ------------
void 
GenParticleSelectorCompHep::endJob() {
      cout << "Events "<< count_events << " " << count_mu << " " <<  count_antimu <<" " <<count_other <<" " <<count_stuff<<endl;
}

// ------------ method called when starting to processes a run  ------------
void 
GenParticleSelectorCompHep::beginRun(edm::Run&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a run  ------------
void 
GenParticleSelectorCompHep::endRun(edm::Run&, edm::EventSetup const&)
{
}

// ------------ method called when starting to processes a luminosity block  ------------
void 
GenParticleSelectorCompHep::beginLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a luminosity block  ------------
void 
GenParticleSelectorCompHep::endLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&)
{
}

// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void
GenParticleSelectorCompHep::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(GenParticleSelectorCompHep);
