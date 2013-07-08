#include <memory>
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/EDProducer.h"
#include <CommonTools/UtilAlgos/interface/ObjectSelector.h>
#include <CommonTools/UtilAlgos/interface/SortCollectionSelector.h>
#include <DataFormats/Candidate/interface/CompositeCandidate.h>
#include <DataFormats/Candidate/interface/Candidate.h>
#include <cmath>
#include "FWCore/Framework/interface/MakerMacros.h"
#include <DataFormats/PatCandidates/interface/Jet.h>
#include "CommonTools/UtilAlgos/interface/SelectionAdderTrait.h"
#include "CommonTools/UtilAlgos/interface/StoreContainerTrait.h"
#include "CommonTools/UtilAlgos/interface/ParameterAdapter.h"

class SortRecoCandCollectionSelectorWithBTag;
struct GreaterByCSVDiscriminator {
	  typedef reco::Candidate first_argument_type;
	  typedef reco::Candidate second_argument_type;

	  std::string bDiscriminator;

	  bool operator()( const reco::Candidate & t1, const reco::Candidate & t2 ) const {
	    return ((const pat::Jet&)t1).bDiscriminator(bDiscriminator) > ((const pat::Jet&)t2).bDiscriminator(bDiscriminator);
	  }
};

template<typename InputCollection, typename Comparator, 
         typename OutputCollection = typename helper::SelectedOutputCollectionTrait<InputCollection>::type, 
         typename StoreContainer = typename helper::StoreContainerTrait<OutputCollection>::type,
         typename RefAdder = typename helper::SelectionAdderTrait<InputCollection, StoreContainer>::type>
class SortCollectionSelectorParametric {
public:
  typedef InputCollection collection;
private:
  typedef const typename InputCollection::value_type * reference;
  typedef std::pair<reference, size_t> pair;
  typedef StoreContainer container;
  typedef typename container::const_iterator const_iterator;

private:
  struct PairComparator {
    PairComparator(const Comparator & cmp) : cmp_(cmp) { }
    bool operator()(const pair & t1, const pair & t2) const {
      return cmp_(*t1.first, *t2.first);
    } 
    Comparator cmp_;
   };
  unsigned int maxNumber_;
  bool reverse;
  StoreContainer selected_;
  RefAdder addRef_;
 
protected:
  PairComparator compare_;
 
 public:
   SortCollectionSelectorParametric(const edm::ParameterSet & cfg) : 
     compare_(Comparator()),
     maxNumber_(cfg.template getParameter<unsigned int>("maxNumber")),
     reverse(cfg.template getParameter<bool>("reverse")) { }
   const_iterator begin() const { return selected_.begin(); }
   const_iterator end() const { return selected_.end(); }
   void select(const edm::Handle<InputCollection> & c, const edm::Event &, const edm::EventSetup&) {
     std::vector<pair> v;
     for(size_t idx = 0; idx < c->size(); ++ idx)
       v.push_back(std::make_pair(&(*c)[idx], idx));
     std::sort(v.begin(), v.end(), compare_);
     if(reverse) {
     	std::reverse(v.begin(), v.end());
     }
     selected_.clear();
     for(size_t i = 0; i < maxNumber_ && i < v.size(); ++i)
       addRef_(selected_, c, v[i].second);
   }
 };

class SortRecoCandCollectionSelectorWithBTag : public SortCollectionSelectorParametric<edm::View<reco::Candidate>, GreaterByCSVDiscriminator> {

public:
	SortRecoCandCollectionSelectorWithBTag(const edm::ParameterSet & cfg) 
	: SortCollectionSelectorParametric<edm::View<reco::Candidate>, GreaterByCSVDiscriminator>(cfg) {
		compare_.cmp_.bDiscriminator = cfg.getParameter<std::string>("bDiscriminator");
	}
};

typedef ObjectSelector< SortRecoCandCollectionSelectorWithBTag > LargestBDiscriminatorJetViewProducer;


DEFINE_FWK_MODULE(LargestBDiscriminatorJetViewProducer);

