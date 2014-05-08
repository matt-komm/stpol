// -*- C++ -*-
//
// Package:    GenParticleSelector
// Class:      GenParticleSelector
// 
/**\class GenParticleSelector GenParticleSelector.cc SingleTopPolarization/GenParticleSelector/src/GenParticleSelector.cc

 Description: [one line class summary]

 Implementation:
     [Notes on implementation]
*/
//
// Original Author:  
//         Created:  R okt   19 18:21:41 EEST 2012
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
#include "FWCore/MessageLogger/interface/MessageLogger.h"

using namespace edm;
using namespace std;
using namespace reco;

//
// class declaration
//

class GenParticleSelector : public edm::EDProducer {
   public:
      explicit GenParticleSelector(const edm::ParameterSet&);
      ~GenParticleSelector();

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
      int count_t, count_other, count_events, count_over3, count_diff, count_siblings, count_nu;
      int mother1, mother2;
      int s1_mother1, s1_mother2, s2_mother1, s2_mother2;
      int sibling1, sibling2;
      int which_sibling;
      int fstateMothers[200][200];
      int fstateSiblings[200][200];
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
GenParticleSelector::GenParticleSelector(const edm::ParameterSet& iConfig)
{
   produces<std::vector<GenParticle>>("trueTop");
   produces<std::vector<GenParticle>>("trueLightJet");
   produces<std::vector<GenParticle>>("trueLepton");
   produces<std::vector<GenParticle>>("trueNeutrino");
   produces<int>("trueLeptonPdgId");

   count_t = 0;
   count_other = 0;
   count_events = 0;
   count_over3 = 0;
   count_diff = 0;
   for(size_t i = 0; i < 200; ++ i){
      for(size_t j = 0; j < 200; ++ j){
         fstateMothers[i][j] = 0;
         fstateSiblings[i][j] = 0;
      }
   }
}


GenParticleSelector::~GenParticleSelector()
{
 
   // do anything here that needs to be done at desctruction time
   // (e.g. close files, deallocate resources etc.)

}


//
// member functions
//

// ------------ method called to produce the data  ------------
void
GenParticleSelector::produce(edm::Event& iEvent, const edm::EventSetup& iSetup)
{
   LogDebug("") << "GenParticleSelector";
   count_siblings = 0;
   which_sibling = 0;
   s1_mother1 = s1_mother2 = s2_mother1 = s2_mother2 = 0;
   Handle<GenParticleCollection> genParticles;
   iEvent.getByLabel("genParticles", genParticles);
   count_events++;

   std::auto_ptr<std::vector<GenParticle> > outTops(new std::vector<GenParticle>());
   std::auto_ptr<std::vector<GenParticle> > outLightJets(new std::vector<GenParticle>());
   std::auto_ptr<std::vector<GenParticle> > outLeptons(new std::vector<GenParticle>());
   std::auto_ptr<std::vector<GenParticle> > outNeutrinos(new std::vector<GenParticle>());

   int trueLeptonPdgId = TMath::QuietNaN();
   GenParticle* lightJet;
   
   for(size_t i = 0; i < genParticles->size(); ++ i) {
     const GenParticle & p = (*genParticles)[i];
     int id = p.pdgId();
     int st = p.status();  
     const Candidate * mom;// = p.mother();
     double pt = p.pt(), eta = p.eta(), phi = p.phi(), mass = p.mass();
     double vx = p.vx(), vy = p.vy(), vz = p.vz();
     int charge = p.charge();
     int n = p.numberOfDaughters();

     if(abs(id) == 6){ //t-quark
        const GenParticle& top = p;
        outTops->push_back(top);
        count_t++;
        //cout << id << " " << st << " " << pt << " " << eta << " " << n << endl;
        for(size_t mi = 0; mi < p.numberOfMothers(); ++ mi){
          mom = p.mother(mi);
          if (mi==0)
            mother1 = mom->pdgId();
          else{
            if (mom->pdgId() > mother1){
               mother2 = mom->pdgId();
            } else {
               mother2 = mother1;
               mother1 = mom->pdgId();
            }
          }
        }

        int index1 = mother1;
        int index2 = mother2;
        if(index1 < 0)
           index1 += 200;
        if(index2 < 0)
           index2 += 200;
        fstateMothers[index1][index2]++;
        for(int j = 0; j < n; ++ j) {
          const GenParticle* d = (GenParticle*)p.daughter( j );
          int dauId = d->pdgId();
          int n2 = d->numberOfDaughters();
          if (abs(dauId) == 24){ //W-boson
            for(int j2 = 0; j2 < n2; ++ j2) {
               const GenParticle* d2 = (GenParticle*)d->daughter( j2 );
               int dau2Id = d2->pdgId();
               if(abs(dau2Id) == 13 || abs(dau2Id) == 11 || abs(dau2Id) == 15){  //muon or electron or tau
                  trueLeptonPdgId = dau2Id;
                  outLeptons->push_back(*d2);                  
               }
               else if(abs(dau2Id) == 14 || abs(dau2Id) == 12 || abs(dau2Id) == 16){  //neutrino
                  outNeutrinos->push_back(*d2);                  
               }
   
             }
          }
        }
     }
     if(p.numberOfMothers() > 2 && st==3)
         count_over3++;
     if(p.numberOfMothers() >= 2 && abs(id) != 6 && st==3){
         int x, y;
         count_other++;
         for(size_t mi = 0; mi < p.numberOfMothers(); ++ mi){
            mom = p.mother(mi);
            //cout << mom->pdgId() << endl;
            if(mi==0)
               x = mom->pdgId();
            if(mi==1){
               if(mom->pdgId() > x)
                  y = mom->pdgId();
               else{
                  y = x;
                  x = mom->pdgId();
               }
            }
                        
        }
        if(which_sibling==0){
          s1_mother1 = x;
          s1_mother2 = y;
          sibling1 = id;
          lightJet = const_cast<reco::GenParticle*>(&p);
          //lightJet* = (const_cast<const reco::GenParticle*>(&p);
        }
        else if(which_sibling==1){
          s2_mother1 = x;
          s2_mother2 = y;
          sibling2 = id;
          if(abs(sibling2) < abs(sibling1))
             lightJet = const_cast<reco::GenParticle*>(&p);
        }else{
          count_diff++;
        }
         

         which_sibling++;
     }
   }

   

   if(!(mother1 == s1_mother1 && s1_mother1 == s2_mother1 && mother2 == s1_mother2 && s1_mother2 == s2_mother2)){
      count_diff++;
   }
   if(sibling1 < 0)
           sibling1 += 200;
     if(sibling2 < 0)
           sibling2 += 200;
     if(sibling1 > sibling2)
         fstateSiblings[sibling1][sibling2]++;
     else
         fstateSiblings[sibling2][sibling1]++;
   
   iEvent.put(outTops, "trueTop");
   iEvent.put(outLeptons, "trueLepton");
   outLightJets->push_back(*lightJet);
   //cout << "NoLightJets " << outLightJets->size() << endl;
   iEvent.put(outLightJets, "trueLightJet");
   iEvent.put(outNeutrinos, "trueNeutrino");
   iEvent.put(std::auto_ptr<int>(new int(trueLeptonPdgId)), "trueLeptonPdgId");  
 
}

// ------------ method called once each job just before starting event loop  ------------
void 
GenParticleSelector::beginJob()
{
}

// ------------ method called once each job just after ending the event loop  ------------
void 
GenParticleSelector::endJob() {
     //cout << "a " << count_t << " " <<count_other << " "<< count_events << endl;
}

// ------------ method called when starting to processes a run  ------------
void 
GenParticleSelector::beginRun(edm::Run&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a run  ------------
void 
GenParticleSelector::endRun(edm::Run&, edm::EventSetup const&)
{
          cout << count_t << " " <<count_other << " "<< count_events << " " <<count_over3 << " " << count_diff << endl;
          cout << "fstateMothers" << endl;
          for(size_t i = 0; i < 200; ++ i){
            for(size_t j = 0; j < 200; ++ j){
               if(fstateMothers[i][j] > 0){
                  int i1 = i;
                  int i2 = j;
                  if(i1 >= 100)
                     i1 -= 200;
                  if(i2 >= 100)
                     i2 -= 200;
                  cout << i1 << " " << i2 << " " << fstateMothers[i][j] <<endl;
               }
            }
          }
          cout << "fstateSiblings" << endl;
          for(size_t i = 0; i < 200; ++ i){
            for(size_t j = 0; j < 200; ++ j){
               if(fstateSiblings[i][j] > 0){
                  int i1 = i;
                  int i2 = j;
                  if(i1 >= 100)
                     i1 -= 200;
                  if(i2 >= 100)
                     i2 -= 200;
                  cout << i1 << " " << i2 << " " << fstateSiblings[i][j] <<endl;
               }
            }
          }
}

// ------------ method called when starting to processes a luminosity block  ------------
void 
GenParticleSelector::beginLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a luminosity block  ------------
void 
GenParticleSelector::endLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&)
{           
}

// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void
GenParticleSelector::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(GenParticleSelector);
