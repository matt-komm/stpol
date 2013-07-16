// -*- C++ -*-
//
// Package:    GenWeightAnalyzer
// Class:      GenWeightAnalyzer
// 
/**\class GenWeightAnalyzer GenWeightAnalyzer.cc SingleTopPolarization/GenWeightAnalyzer/src/GenWeightAnalyzer.cc

 Description: [one line class summary]

 Implementation:
     [Notes on implementation]
*/
//
// Original Author:  Joosep Pata
//         Created:  Wed Jul 10 17:25:36 EEST 2013
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
#include <SimDataFormats/GeneratorProducts/interface/GenEventInfoProduct.h>

class GenWeightAnalyzer : public edm::EDAnalyzer {
   public:
      explicit GenWeightAnalyzer(const edm::ParameterSet&);
      ~GenWeightAnalyzer();

      static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);


   private:
      virtual void beginJob() ;
      virtual void analyze(const edm::Event&, const edm::EventSetup&);
      virtual void endJob() ;

      virtual void beginRun(edm::Run const&, edm::EventSetup const&);
      virtual void endRun(edm::Run const&, edm::EventSetup const&);
      virtual void beginLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&);
      virtual void endLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&);

    const edm::InputTag genWeightSrc;
    TH1F* hist_weight;
    edm::Service<TFileService> fs;
};

GenWeightAnalyzer::GenWeightAnalyzer(const edm::ParameterSet& iConfig)
: genWeightSrc(edm::InputTag("generator"))
{
    hist_weight = fs->make<TH1F>("gen_weight" , "gen_weight", 500,  0, 2.0);
}


GenWeightAnalyzer::~GenWeightAnalyzer()
{
}

void
GenWeightAnalyzer::analyze(const edm::Event& iEvent, const edm::EventSetup& iSetup)
{

    edm::Handle<GenEventInfoProduct> genEventInfo;
    iEvent.getByLabel(genWeightSrc, genEventInfo);
    if (genEventInfo.isValid())
        hist_weight->Fill(genEventInfo->weight());
}

void 
GenWeightAnalyzer::beginJob()
{
}

void 
GenWeightAnalyzer::endJob() 
{
}

void 
GenWeightAnalyzer::beginRun(edm::Run const&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a run  ------------
void 
GenWeightAnalyzer::endRun(edm::Run const&, edm::EventSetup const&)
{
}

// ------------ method called when starting to processes a luminosity block  ------------
void 
GenWeightAnalyzer::beginLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a luminosity block  ------------
void 
GenWeightAnalyzer::endLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&)
{
}

// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void
GenWeightAnalyzer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(GenWeightAnalyzer);
