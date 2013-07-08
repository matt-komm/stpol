// -*- C++ -*-
//
// Package:    GenericViewTreemakerAnalyzer
// Class:      GenericViewTreemakerAnalyzer
// 
/**\class GenericViewTreemakerAnalyzerGenericViewTreemakerAnalyzer GenericViewTreemakerAnalyzer.cc SingleTopPolarization/GenericViewTreemakerAnalyzer/src/GenericViewTreemakerAnalyzer.cc

 Description: This class produces a TTree, the branches of which are the specified components of given collections

 Implementation:
     This class is implemented using the StringObjectFunction to allow generic
     object properties to be outputted to the TTree. All configuration is done
     via the python interface. The first template argument T is a collection
     type object which must be present in the file. A typical value for T
     is edm::View<reco::Candidate> or reco::CandidateCollection (aka OwnVector).

     The objects in the collection are treated as instances of the class C, meaning
     that T::value_type must be a base type of C. A typical value for C is
     pat::Jet if you wish to access the jet properties of an object.
*/
//
// Original Author: Joosep Pata
//         Created:  Fri Sep 21 11:28:31 EEST 2012
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

//Required for reco::Candidate
#include <DataFormats/Candidate/interface/Candidate.h> 

//Required for StringObjectFunction
#include <CommonTools/Utils/interface/StringObjectFunction.h>

//Required for TFileService
#include "FWCore/ServiceRegistry/interface/Service.h"
#include "CommonTools/UtilAlgos/interface/TFileService.h"

//PAT
#include <DataFormats/PatCandidates/interface/Jet.h>
#include <DataFormats/PatCandidates/interface/Muon.h>
#include <DataFormats/PatCandidates/interface/Electron.h>

//OwnVector
#include <DataFormats/Common/interface/OwnVector.h>

#include "CommonTools/UtilAlgos/interface/SingleObjectSelector.h"
#include "CommonTools/UtilAlgos/interface/StringCutObjectSelector.h"

#include "TTree.h"

//for ITOA
#include <sstream>

#include "FWCore/MessageLogger/interface/MessageLogger.h"


//
// class declaration
//

#define ITOA(A) (static_cast<std::ostringstream*>(&(std::ostringstream()<<A) )->str())
#define D_NAN (std::numeric_limits<double>::quiet_NaN())

template <typename T, typename C>
class GenericViewTreemakerAnalyzer : public edm::EDAnalyzer {
   public:
      explicit GenericViewTreemakerAnalyzer(const edm::ParameterSet&);
      ~GenericViewTreemakerAnalyzer();

      static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);


   private:
      virtual void beginJob() ;
      virtual void analyze(const edm::Event&, const edm::EventSetup&);
      virtual void endJob() ;

      virtual void beginRun(edm::Run const&, edm::EventSetup const&);
      virtual void endRun(edm::Run const&, edm::EventSetup const&);
      virtual void beginLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&);
      virtual void endLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&);

      /*
      This is a map that stores as the key the name of an object collection,
      such as 'selectedPatMuons' and as value the variables to get from that
      collection. The variables are stored as another map, where the key is the
      name of that variable that will end up in the TTree and the value is a
      StringObjectFunction that allows the variable to be extracted from the
      collection.
      */
      std::map<std::string, std::map<std::string, StringObjectFunction<C>* > > quantities;

      //All the branch variables
      std::map<std::string, std::map<std::string, std::vector<double*> > > treeValues;

      //Maximum number of elements per collection
      std::map<std::string, int> maxElems;

      edm::Service<TFileService> fs;

      TTree* outTree;

      bool makeTree;
      std::string treeName;
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
template <typename T, typename C>
GenericViewTreemakerAnalyzer<T, C>::GenericViewTreemakerAnalyzer(const edm::ParameterSet& iConfig)
{

  makeTree = iConfig.getUntrackedParameter<bool>("makeTree", true);
  treeName = iConfig.getUntrackedParameter<std::string>("treeName", "eventTree");

  if(makeTree) {
    outTree = fs->make<TTree>(treeName.c_str(), treeName.c_str());
  } else {
    outTree = fs->getObject<TTree>(treeName.c_str());
  }

  auto collectionsPSets = iConfig.getUntrackedParameter<std::vector<edm::ParameterSet>>("collections");
  for (auto& colPSet : collectionsPSets) {

    //The name of the collection to analyze
    const auto& collection = colPSet.template getUntrackedParameter<edm::InputTag>("collection");
    const auto& collectionName = collection.encode();
    //The maximum number of elements from a collection to write down
    maxElems[collectionName] = colPSet.template getUntrackedParameter<int>("maxElems");

    //The vector of variables to get from the collections
    const auto& varPSets = colPSet.template getUntrackedParameter<std::vector<edm::ParameterSet>>("variables");

    for (auto& varPSet : varPSets) {

      //The name of the variable in the output TTree
      const auto& tag = varPSet.template getUntrackedParameter<std::string>("tag");

      //The expression to evaluate on an element of the collection
      const auto& expr = varPSet.template getUntrackedParameter<std::string>("expr");

      StringObjectFunction<C>* t = new StringObjectFunction<C>(expr, false);
      quantities[collectionName][tag] = t;
      for(int i=0;i<maxElems[collectionName];i++) {
        double* d = new double(D_NAN);
        treeValues[collectionName][tag].push_back(d);
        const std::string brName = collection.instance() + "_" + collection.label() + "_" + ITOA(i) + "_" + tag;
        outTree->Branch(brName.c_str(), d);
      }
    }
  }  
}


template <typename T, typename C>
GenericViewTreemakerAnalyzer<T, C>::~GenericViewTreemakerAnalyzer()
{
  for(auto& collectionVarMap : quantities) {
    auto& varMap = collectionVarMap.second;
    for (auto& var : varMap) {
      delete var.second;
    }
  }


  for(auto& colLevel : treeValues) {
    for (auto& varLevel : colLevel.second) {
      for (auto& d : varLevel.second) {
        delete d;
      }
    }
  }

}


//
// member functions
//

// ------------ method called for each event  ------------
template <typename T, typename C>
void
GenericViewTreemakerAnalyzer<T, C>::analyze(const edm::Event& iEvent, const edm::EventSetup& iSetup)
{
  //std::cout << "Begin processing event" << std::endl;

  using namespace edm;

  Handle<T> objects;

  //Initialize all branch variables
  for (auto& cols : treeValues) {
    for (auto& value : cols.second) {
      //std::cout << cols.first << " " << value.first << " " << value.second.size() << std::endl;
      for(auto& v : value.second) {
        *v = D_NAN;
      }
    }
  }

  for (auto& collection : quantities) {
    auto& collectionName = collection.first;
    iEvent.getByLabel(edm::InputTag(collectionName), objects);

    auto& varMap = collection.second;

    //std::cout << "col " << collectionName << " " << objects->size() << std::endl;

    int i = 0; //count the objects of the collection of interest
    if(objects.isValid() ) {
      for (auto& obj : *objects) {
        //std::cout << "obj ";
        for (auto& var : varMap) {
          auto& tag = var.first;
          //std::cout << "var(" << tag << ") ";
          auto& varParser = *(var.second);
          //const double value = varParser((pat::Jet)(obj));
          const C* pObj = static_cast<const C*>(&obj);
          if (pObj == 0) {
            std::cout << "Could not cast" << std::endl;
          }
          const double&& value = varParser(*pObj);
          //std::cout << value << " ";
          //std::cout << collectionName << "[" << i << "] " << tag << " " << value << std::endl;
          if (i<maxElems[collectionName]) {
            *(treeValues[collectionName][tag][i]) = value;
          } else {
            break;
          }
        }
        //std::cout << std::endl;
        i++;
      }
    } else { //
      LogDebug("produce()") << "Collection " << collectionName << " does not exist in event";
    }
  }

  /*
  for (auto& cols : treeValues) {
    std::cout << cols.first << " ";
    for (auto& value : cols.second) {
      std::cout << value.first << " ";
      for(auto& v : value.second) {
        std::cout << *v << " ";
      }
    }
    std::cout << std::endl;
  }
  */
  
  outTree->Fill();
  //std::cout << "Done processing event" << std::endl;
}


// ------------ method called once each job just before starting event loop  ------------
template <typename T, typename C>
void 
GenericViewTreemakerAnalyzer<T, C>::beginJob()
{
}

// ------------ method called once each job just after ending the event loop  ------------
template <typename T, typename C>
void 
GenericViewTreemakerAnalyzer<T, C>::endJob() 
{
}

// ------------ method called when starting to processes a run  ------------
template <typename T, typename C>
void 
GenericViewTreemakerAnalyzer<T, C>::beginRun(edm::Run const&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a run  ------------
template <typename T, typename C>
void 
GenericViewTreemakerAnalyzer<T, C>::endRun(edm::Run const&, edm::EventSetup const&)
{
}

// ------------ method called when starting to processes a luminosity block  ------------
template <typename T, typename C>
void 
GenericViewTreemakerAnalyzer<T, C>::beginLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a luminosity block  ------------
template <typename T, typename C>
void 
GenericViewTreemakerAnalyzer<T, C>::endLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&)
{
}

// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
template <typename T, typename C>
void
GenericViewTreemakerAnalyzer<T, C>::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);
}

// typedef SingleObjectSelector<edm::View<pat::Jet>,
// StringCutObjectSelector< pat::Jet>,
// edm::OwnVector<pat::Jet, edm::ClonePolicy<pat::Jet>> > JetViewSelector;

//typedef SingleObjectSelector< edm::View<pat::Jet>, StringCutObjectSelector<pat::Jet, true>, edm::OwnVector<pat::Jet, edm::ClonePolicy<pat::Jet>> > JetViewSelector;

typedef GenericViewTreemakerAnalyzer<edm::View<reco::Candidate>, reco::Candidate> CandViewTreemakerAnalyzer;
typedef GenericViewTreemakerAnalyzer<edm::View<reco::Candidate>, reco::CompositeCandidate> CompositeCandViewTreemakerAnalyzer;
typedef GenericViewTreemakerAnalyzer<edm::View<reco::Candidate>, pat::Jet> JetCandViewTreemakerAnalyzer;
typedef GenericViewTreemakerAnalyzer<reco::CandidateCollection, pat::Jet> JetCandOwnVectorTreemakerAnalyzer;
typedef GenericViewTreemakerAnalyzer<reco::CandidateCollection, pat::Muon> MuonCandOwnVectorTreemakerAnalyzer;
typedef GenericViewTreemakerAnalyzer<edm::View<reco::Candidate>, pat::Muon> MuonCandViewTreemakerAnalyzer;
typedef GenericViewTreemakerAnalyzer<edm::View<reco::Candidate>, pat::Electron> ElectronCandViewTreemakerAnalyzer;
//typedef GenericViewTreemakerAnalyzer<edm::OwnVector<pat::Jet, edm::ClonePolicy<pat::Jet>>> JetVectorTreemakerAnalyzer;

//define this as a plug-in
DEFINE_FWK_MODULE(CandViewTreemakerAnalyzer);
DEFINE_FWK_MODULE(CompositeCandViewTreemakerAnalyzer);
DEFINE_FWK_MODULE(JetCandViewTreemakerAnalyzer);
DEFINE_FWK_MODULE(JetCandOwnVectorTreemakerAnalyzer);
DEFINE_FWK_MODULE(MuonCandOwnVectorTreemakerAnalyzer);
DEFINE_FWK_MODULE(MuonCandViewTreemakerAnalyzer);
DEFINE_FWK_MODULE(ElectronCandViewTreemakerAnalyzer);
//DEFINE_FWK_MODULE(JetVectorTreemakerAnalyzer);
//DEFINE_FWK_MODULE(JetViewSelector);

