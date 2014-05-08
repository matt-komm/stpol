#include <memory>
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/EDProducer.h"
#include <CommonTools/UtilAlgos/interface/ObjectSelector.h>
#include <CommonTools/UtilAlgos/interface/SortCollectionSelector.h>
#include <DataFormats/RecoCandidate/interface/RecoCandidate.h>
#include <DataFormats/Candidate/interface/CompositeCandidate.h>
#include <cmath>
#include "FWCore/Framework/interface/MakerMacros.h"

template<typename T>
struct GreaterByAbsEta {
  typedef T first_argument_type;
  typedef T second_argument_type;
  
  bool operator()( const T & t1, const T & t2 ) const {
    return std::fabs(t1.eta())>std::fabs(t2.eta());
  }
};
typedef ObjectSelector<SortCollectionSelector<reco::CandidateView, GreaterByAbsEta<reco::Candidate> > > LargestAbsEtaCandViewProducer;
DEFINE_FWK_MODULE(LargestAbsEtaCandViewProducer);

