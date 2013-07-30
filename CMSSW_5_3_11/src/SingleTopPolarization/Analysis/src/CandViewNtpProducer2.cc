/* \class CandViewNtpProducer
 * 
 * Configurable Candidate ntuple creator
 *
 * \author: Luca Lista, INFN
 *
 */
#include "FWCore/Framework/interface/MakerMacros.h"
#include "SingleTopPolarization/Analysis/interface/NtpProducer2.h"
#include "DataFormats/Candidate/interface/Candidate.h"

typedef NtpProducer2<reco::CandidateView> CandViewNtpProducer2;

DEFINE_FWK_MODULE( CandViewNtpProducer2 );

