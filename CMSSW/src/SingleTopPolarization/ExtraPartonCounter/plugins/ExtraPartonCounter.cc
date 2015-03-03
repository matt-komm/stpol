// system include files
#include <memory>

// user include files

#include "FWCore/Framework/interface/ESHandle.h"
#include "FWCore/Utilities/interface/InputTag.h"
#include "DataFormats/Common/interface/Handle.h"
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/EDProducer.h"

#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/ServiceRegistry/interface/Service.h"
#include "DataFormats/HepMCCandidate/interface/GenParticle.h"

//
// class declaration
//

class ExtraPartonCounter : public edm::EDProducer{
   public:
      explicit ExtraPartonCounter(const edm::ParameterSet&);
      ~ExtraPartonCounter();

      static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);


   private:


      virtual void beginJob() ;
      virtual void produce(edm::Event&, const edm::EventSetup&);
      virtual void endJob() ;

      virtual void beginRun(edm::Run const&, edm::EventSetup const&);
      virtual void endRun(edm::Run const&, edm::EventSetup const&);
      virtual void beginLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&);
      virtual void endLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&);


 };

//
// constructors and destructor
//
ExtraPartonCounter::ExtraPartonCounter(const edm::ParameterSet& iConfig)
{
  produces<std::vector<double> >("nExtraPartons");
}


ExtraPartonCounter::~ExtraPartonCounter()
{
 
 
}

void
ExtraPartonCounter::produce(edm::Event& iEvent, const edm::EventSetup& iSetup)
{
  using namespace edm;
  using namespace std;
  using namespace reco;
  
  
  
  std::auto_ptr<std::vector<double>>  nExtraPartons(new std::vector<double>(1));
  
 
  
  edm::Handle<GenParticleCollection> genPart;
  iEvent.getByLabel("genParticles", genPart);
  

    for(size_t i = 0; i < genPart->size(); ++ i) 
    {
    
        const GenParticle & p = (*genPart)[i];
        if ( p.status() == 3 && (fabs(p.pdgId())<6 || (p.pdgId())==21)) 
        { 
            bool is_final= true;
            bool is_extra = true;
            for(size_t j=0; j < p.numberOfDaughters(); j++)
            {
                 if(p.daughter(j)->status()==3)
                 {
                    is_final=false;
                    break;
                 }
            }
            for(size_t j=0; j < p.numberOfMothers(); j++)
            {
                if ((fabs(p.mother(j)->pdgId())==6) ||  (fabs(p.mother(j)->pdgId())==24))
                {
                    is_extra=false;
                    break;
                }
            }
            
            if (is_final && is_extra)
            {
                ++(*nExtraPartons)[0];
            }
        }
    }
  iEvent.put(nExtraPartons, "nExtraPartons");
}

// ------------ method called once each job just before starting event loop  ------------
void 
ExtraPartonCounter::beginJob()
{
}

// ------------ method called once each job just after ending the event loop  ------------
void 
ExtraPartonCounter::endJob() 
{
}

// ------------ method called when starting to processes a run  ------------
void 
ExtraPartonCounter::beginRun(edm::Run const&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a run  ------------
void 
ExtraPartonCounter::endRun(edm::Run const&, edm::EventSetup const&)
{
}

// ------------ method called when starting to processes a luminosity block  ------------
void 
ExtraPartonCounter::beginLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a luminosity block  ------------
void 
ExtraPartonCounter::endLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&)
{
}

// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void
ExtraPartonCounter::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(ExtraPartonCounter);
