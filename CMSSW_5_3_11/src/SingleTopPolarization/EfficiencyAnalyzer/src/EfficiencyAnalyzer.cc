// -*- C++ -*-
//
// Package:    EfficiencyAnalyzer
// Class:      EfficiencyAnalyzer
// 
/**\class EfficiencyAnalyzer EfficiencyAnalyzer.cc test/EfficiencyAnalyzer/src/EfficiencyAnalyzer.cc

 Description: [one line class summary]

 Implementation:
     [Notes on implementation]
*/
//
// Original Author:  
//         Created:  Tue Sep 11 21:15:04 EEST 2012
// $Id$
//
//


// system include files
#include <memory>

// user include files
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/EDAnalyzer.h"

#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/LuminosityBlock.h"
#include "FWCore/Framework/interface/MakerMacros.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"

//Required for accessing the lumi-block counters
#include "DataFormats/Common/interface/MergeableCounter.h"

//Required for TFileService
#include "FWCore/ServiceRegistry/interface/Service.h"
#include "CommonTools/UtilAlgos/interface/TFileService.h"


typedef std::map<std::string, unsigned long> str_ulong_map;

//
// class declaration
//

class EfficiencyAnalyzer : public edm::EDAnalyzer {
   public:
      explicit EfficiencyAnalyzer(const edm::ParameterSet&);
      ~EfficiencyAnalyzer();

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
      edm::Service<TFileService> fs;

      unsigned long processedEventCounter;
      unsigned long passedEventCounter;
      std::map <std::string, unsigned long> countMap;
      std::vector <std::string> trackedCounters;

      std::map<std::string, std::vector<std::string>> histogrammableCounterNames;

      std::map<std::string, TH1I*> histograms;

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
EfficiencyAnalyzer::EfficiencyAnalyzer(const edm::ParameterSet& iConfig)

{
    processedEventCounter = 0;
    passedEventCounter = 0;
    std::vector<std::string> histogrammableCounters = iConfig.getUntrackedParameter<std::vector<std::string>>("histogrammableCounters");

    for(std::string& s : histogrammableCounters)
    {
        histogrammableCounterNames[s] = iConfig.getUntrackedParameter<std::vector<std::string>>(s);
        for(std::string& hn : histogrammableCounterNames[s]) {
            trackedCounters.push_back(hn);
        }
        const char* histName = s.c_str();
        histograms[s] = fs->make<TH1I>(histName, histName, histogrammableCounterNames[s].size(), 0, histogrammableCounterNames[s].size() - 1);
    }

    for(const std::string& s : trackedCounters)
    {
        countMap[s] = (unsigned long)0;
    }

}


EfficiencyAnalyzer::~EfficiencyAnalyzer()
{
  /*for (auto& elem : histograms) {
    delete elem.second;
  }*/
   // do anything here that needs to be done at desctruction time
   // (e.g. close files, deallocate resources etc.)

}


//
// member functions
//

// ------------ method called for each event  ------------
void
EfficiencyAnalyzer::analyze(const edm::Event& iEvent, const edm::EventSetup& iSetup)
{
   using namespace edm;



#ifdef THIS_IS_AN_EVENT_EXAMPLE
   Handle<ExampleData> pIn;
   iEvent.getByLabel("example",pIn);
#endif
   
#ifdef THIS_IS_AN_EVENTSETUP_EXAMPLE
   ESHandle<SetupData> pSetup;
   iSetup.get<SetupRecord>().get(pSetup);
#endif
}


// ------------ method called once each job just before starting event loop  ------------
void 
EfficiencyAnalyzer::beginJob()
{
}

// ------------ method called once each job just after ending the event loop  ------------
void 
EfficiencyAnalyzer::endJob() 
{
    for(const std::string& s : trackedCounters)
    {
        std::cout << s << " = " << countMap[s] << std::endl;
    }

    for(auto it = histogrammableCounterNames.begin(); it != histogrammableCounterNames.end(); ++it) {
        TH1I* hist = histograms[it->first];
        
        std::vector<std::string>* histBins = &(it->second);
        int i = 1;
        for(std::string& s : *(histBins))
        {
            hist->AddBinContent(i, countMap[s]);
            hist->GetXaxis()->SetBinLabel(i, s.c_str());
            i++;
        }

    }
}

// ------------ method called when starting to processes a run  ------------
void 
EfficiencyAnalyzer::beginRun(edm::Run const&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a run  ------------
void 
EfficiencyAnalyzer::endRun(edm::Run const&, edm::EventSetup const&)
{
}

// ------------ method called when starting to processes a luminosity block  ------------
void 
EfficiencyAnalyzer::beginLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a luminosity block  ------------
void 
EfficiencyAnalyzer::endLuminosityBlock(const edm::LuminosityBlock& lumi, edm::EventSetup const&)
{
    edm::Handle<edm::MergeableCounter> counter;

    for(const std::string& s : trackedCounters)
    {
        lumi.getByLabel(s, counter);
        if(counter.isValid()) {
          countMap[s] += (unsigned long)(counter->value);
        }
    }
}

// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void
EfficiencyAnalyzer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(EfficiencyAnalyzer);
