// -*- C++ -*-
//
// Package:    LeptonIsolationProducer<T>
// Class:      LeptonIsolationProducer<T>
//
/**\class LeptonIsolationProducer<T> LeptonIsolationProducer<T>.cc SingleTopPolarization/LeptonIsolationProducer<T>/src/LeptonIsolationProducer<T>.cc
 
 Description: Adds the delta beta corrected and rho corrected relative isolations to the leptons
 
 Implementation:
 [Notes on implementation]
 */
//
// Original Author:
//         Created:  Tue Sep 25 09:10:09 EEST 2012
// $Id$
//
//


// system include files
#include <memory>

// user include files
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/EDProducer.h"

#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"

#include "FWCore/Utilities/interface/InputTag.h"

//PAT
#include <DataFormats/PatCandidates/interface/Muon.h>
#include <DataFormats/PatCandidates/interface/Electron.h>

//Electron effective area
#include <EGamma/EGammaAnalysisTools/interface/ElectronEffectiveArea.h>



//
// class declaration
//
template <typename T>
class LeptonIsolationProducer : public edm::EDProducer {
public:
    explicit LeptonIsolationProducer(const edm::ParameterSet&);
    ~LeptonIsolationProducer();
    
    static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);
    
private:
    virtual void beginJob() ;
    virtual void produce(edm::Event&, const edm::EventSetup&);
    virtual void endJob() ;
    
    virtual void beginRun(edm::Run&, edm::EventSetup const&);
    virtual void endRun(edm::Run&, edm::EventSetup const&);
    virtual void beginLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&);
    virtual void endLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&);
    
    double effectiveArea(const reco::Candidate& lepton);
    void addPtEtaCorr(reco::Candidate& lepton);
    
    const edm::InputTag leptonSource;
    const edm::InputTag rhoSource;
    
    const double dR;
    
    
    // ----------member data ---------------------------
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
template <typename T>
LeptonIsolationProducer<T>::LeptonIsolationProducer(const edm::ParameterSet& iConfig)
: leptonSource(iConfig.getParameter<edm::InputTag>("leptonSrc"))
, rhoSource(iConfig.getParameter<edm::InputTag>("rhoSrc"))
, dR(iConfig.getParameter<double>("dR"))
{
    produces<std::vector<T> >();
    
    
    //now do what ever other initialization is needed
    
}


template <typename T>
LeptonIsolationProducer<T>::~LeptonIsolationProducer()
{
    
    // do anything here that needs to be done at desctruction time
    // (e.g. close files, deallocate resources etc.)
    
}


//
// member functions
//


//Generic effective area (spherical approximation)
template <typename T>
double LeptonIsolationProducer<T>::effectiveArea(const reco::Candidate& lepton) {
    LogDebug("effectiveArea()") << "Calculating generic effective area";
    return TMath::Pi()*pow(dR, 2);
}

// Muon EA source info: https://indico.cern.ch/getFile.py/access?contribId=1&resId=0&materialId=slides&confId=188494 (slide 9, last column (dR<0.4))
template <>
double LeptonIsolationProducer<pat::Muon>::effectiveArea(const reco::Candidate& lepton) {
    LogDebug("effectiveArea()") << "Calculating muon effective area";
    const double eta = fabs(lepton.eta());
    if (eta < 1.0) return 0.674;
    if (eta < 1.5) return 0.565;
    if (eta < 2.0) return 0.442;
    if (eta < 2.2) return 0.515;
    if (eta < 2.3) return 0.821;
    if (eta < 2.4) return 0.66;
    else return TMath::QuietNaN(); //TODO: what is going on here?
}

// Electron EA source info: https://twiki.cern.ch/twiki/bin/view/CMS/EgammaEARhoCorrection
template <>
double LeptonIsolationProducer<pat::Electron>::effectiveArea(const reco::Candidate& lepton) {
    LogDebug("effectiveArea()") << "Calculating electron effective area";
    
    const pat::Electron& _lepton = (const pat::Electron&)lepton;
    //const double eta = fabs(_lepton.superCluster()->eta());
    const double eta = _lepton.userFloat("etaCorr");
    
    return ElectronEffectiveArea::GetElectronEffectiveArea(ElectronEffectiveArea::ElectronEffectiveAreaType::kEleGammaAndNeutralHadronIso03,
                                                           eta, ElectronEffectiveArea::ElectronEffectiveAreaTarget::kEleEAData2012);
    
}

template <>
void
LeptonIsolationProducer<pat::Electron>::addPtEtaCorr(reco::Candidate& lepton) {
    pat::Electron& ele = (pat::Electron&)lepton;
    ele.addUserFloat("ptCorr", ele.ecalDrivenMomentum().Pt());
    ele.addUserFloat("etaCorr", ele.superCluster()->eta());
}

template <>
void
LeptonIsolationProducer<pat::Muon>::addPtEtaCorr(reco::Candidate& lepton) {
    pat::Muon& mu = (pat::Muon&)lepton;
    mu.addUserFloat("ptCorr", mu.pt());
    mu.addUserFloat("etaCorr", mu.eta());
}

template <typename T>
void
LeptonIsolationProducer<T>::produce(edm::Event& iEvent, const edm::EventSetup& iSetup)
{
    using namespace edm;
    
    Handle<View<reco::Candidate> > leptons;
    Handle<double> rho;
    
    iEvent.getByLabel(leptonSource,leptons);
    iEvent.getByLabel(rhoSource,rho);
    assert(leptons.isValid()); 
    assert(rho.isValid()); 

    std::auto_ptr<std::vector<T> > outLeptons(new std::vector<T>());
    for (auto& lepton : *leptons) {

        //We assume the lepton is of type T and make a copy
        const T* elem = static_cast<const T*>(&lepton);
        outLeptons->push_back(T(*elem));
    }
    
    for (auto& lepton : *outLeptons) {
        //Set the correted pt and eta
        addPtEtaCorr(lepton);
        
        //Calculate the delta-beta corrected relative isolation
        float dbc_iso = (lepton.chargedHadronIso() + std::max(0., lepton.neutralHadronIso() + lepton.photonIso() - 0.5*lepton.puChargedHadronIso()))/lepton.userFloat("ptCorr");
        LogDebug("produce") << "dbcIso=" << dbc_iso << " chHad=" << lepton.chargedHadronIso() << " nHad=" << lepton.neutralHadronIso() << " ph=" << lepton.photonIso() << " puChHad=" << lepton.puChargedHadronIso() << " pt=" << lepton.userFloat("ptCorr");
        //Calculate the rho-corrected relative isolation
        double ea = effectiveArea(lepton);
        float rc_iso = (lepton.chargedHadronIso() + std::max(0., lepton.neutralHadronIso() + lepton.photonIso() - ea*(*rho)))/lepton.userFloat("ptCorr");
        LogDebug("produce") << "rcIso=" << rc_iso << " ea=" << ea << " rho=" << *rho;
        
        //Calculate the uncorrected relative isolation
        float uncorr_iso = (lepton.chargedHadronIso() + std::max((float)0.0, lepton.neutralHadronIso() + lepton.photonIso()))/lepton.et();
        
        lepton.addUserFloat("deltaBetaCorrRelIso", dbc_iso);
        lepton.addUserFloat("rhoCorrRelIso", rc_iso);
        lepton.addUserFloat("unCorrRelIso", uncorr_iso);
    }
    iEvent.put(outLeptons);
}

// ------------ method called once each job just before starting event loop  ------------
template <typename T>
void
LeptonIsolationProducer<T>::beginJob()
{
}

// ------------ method called once each job just after ending the event loop  ------------
template <typename T>
void
LeptonIsolationProducer<T>::endJob() {
}

// ------------ method called when starting to processes a run  ------------
template <typename T>
void
LeptonIsolationProducer<T>::beginRun(edm::Run&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a run  ------------
template <typename T>
void
LeptonIsolationProducer<T>::endRun(edm::Run&, edm::EventSetup const&)
{
}

// ------------ method called when starting to processes a luminosity block  ------------
template <typename T>
void
LeptonIsolationProducer<T>::beginLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a luminosity block  ------------
template <typename T>
void
LeptonIsolationProducer<T>::endLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&)
{
}

// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
template <typename T>
void
LeptonIsolationProducer<T>::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
    //The following says we do not know what parameters are allowed so do no validation
    // Please change this to state exactly what you do use, even if it is no parameters
    edm::ParameterSetDescription desc;
    desc.setUnknown();
    descriptions.addDefault(desc);
}

//define this as a plug-in
typedef LeptonIsolationProducer<pat::Muon> MuonIsolationProducer;
typedef LeptonIsolationProducer<pat::Electron> ElectronIsolationProducer;
DEFINE_FWK_MODULE(MuonIsolationProducer);
DEFINE_FWK_MODULE(ElectronIsolationProducer);
