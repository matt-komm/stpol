// -*- C++ -*-
//
// Package:    BTagSystematicsWeightProducer
// Class:      BTagSystematicsWeightProducer
//
/**\class BTagSystematicsWeightProducer BTagSystematicsWeightProducer.cc SingleTopPolarization/BTagSystematicsWeightProducer/src/BTagSystematicsWeightProducer.cc
 
 Description: Produces the b-tag reweight from the b-tagging efficiency and the scale factor, along with the up/down variation of this weight.
 
 Implementation:

 Follows the ideas from "Trigger with the b-tagging fragment in the analysis" by A. Popov
 https://twiki.cern.ch/twiki/bin/viewauth/CMS/BTagWeight
 
 */
//
// Original Author:  Joosep Pata
//         Created:  Fri Dec 21 16:47:11 EET 2012
// $Id$
//
//


// system include files
#include <memory>
#include <algorithm>

// user include files
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/EDProducer.h"

#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"
#include "FWCore/ParameterSet/interface/FileInPath.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"

#include "FWCore/MessageLogger/interface/MessageLogger.h"
#include "DataFormats/PatCandidates/interface/Jet.h"
#include <TFormula.h>
#include <TMath.h>
#include <TH2D.h>
#include <TFile.h>
#include <string.h>

#include "SingleTopPolarization/Analysis/interface/debug_util.h"


//
// class declaration
//

typedef std::vector<std::vector<unsigned int>> Combinations;

class BTagSystematicsWeightProducer : public edm::EDProducer {
public:
    enum Flavour {
        b,c,l
    };
    enum BTagAlgo {
        CSVM,
        TCHPT
    };
    explicit BTagSystematicsWeightProducer(const edm::ParameterSet&);
    ~BTagSystematicsWeightProducer();
    
    static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);
    
private:
    virtual void beginJob() ;
    virtual void produce(edm::Event&, const edm::EventSetup&);
    virtual void endJob() ;
    
    virtual void beginRun(edm::Run&, edm::EventSetup const&);
    virtual void endRun(edm::Run&, edm::EventSetup const&);
    virtual void beginLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&);
    virtual void endLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&);
    
    
    void combinations(const unsigned int n, const unsigned int k, Combinations& combs);
    
    //const std::unique_ptr<std::map<BTagSystematicsWeightProducer::Flavour, double>> effs_in2J;
    //const std::unique_ptr<std::map<BTagSystematicsWeightProducer::Flavour, double>> effs_in3J;
    const edm::InputTag jetSrc;
    const edm::InputTag nJetSrc, nTagSrc;
    Combinations combs;
    double scaleFactor(BTagSystematicsWeightProducer::Flavour flavour, BTagSystematicsWeightProducer::BTagAlgo algo, double pt, double eta, double& sfUp, double& sfDown);
    double piecewise(double x, const std::vector<double>& bin_low, const std::vector<double>& bin_val);
   
    //Hard-coded look-up tables for the errors of the SFb for various algos
    static const std::vector<double> SFb_ptBins;
    static const std::vector<double> SFb_CSVM_Err;
    static const std::vector<double> SFb_TCHPT_Err;
    
    std::map<BTagSystematicsWeightProducer::Flavour, TH2D*> effHists_2J;
    std::map<BTagSystematicsWeightProducer::Flavour, TH2D*> effHists_3J;
    edm::FileInPath effFileB;
    edm::FileInPath effFileC;
    edm::FileInPath effFileL;
    TFile* effTFileB;
    TFile* effTFileC;
    TFile* effTFileL;

    BTagSystematicsWeightProducer::BTagAlgo bTagAlgo;
};


const std::vector<double> BTagSystematicsWeightProducer::SFb_ptBins ({
    20,
    30,
    40,
    50,
    60,
    70,
    80,
    100,
    120,
    160,
    210,
    260,
    320,
    400,
    500,
    600,
    800
});

//https://twiki.cern.ch/twiki/pub/CMS/BtagPOG/SFb-pt_payload_Moriond13.txt
const std::vector<double> BTagSystematicsWeightProducer::SFb_CSVM_Err ({
    0.0554504,
    0.0209663,
    0.0207019,
    0.0230073,
    0.0208719,
    0.0200453,
    0.0264232,
    0.0240102,
    0.0229375,
    0.0184615,
    0.0216242,
    0.0248119,
    0.0465748,
    0.0474666,
    0.0718173,
    0.0717567
});

//bin-by-bin(pt) variation for TCHPT for QCD-derived scale factors
const std::vector<double> BTagSystematicsWeightProducer::SFb_TCHPT_Err ({
    0.0725549,
    0.0275189,
    0.0279695,
    0.028065,
    0.0270752,
    0.0254934,
    0.0262087,
    0.0230919,
    0.0294829,
    0.0226487,
    0.0272755,
    0.0303747,
    0.051223,
    0.0542895,
    0.0589887,
    0.0584216
});


//bin_low must be sorted ascending, contains the lower values of bins.
//The final bin_low contains the upper value of the last bin.
//bin_val must contain bin_low.size()-1 values.
double BTagSystematicsWeightProducer::piecewise(double x, const std::vector<double>& bin_low, const std::vector<double>& bin_val)
{
    assert(bin_low.size() == bin_val.size()+1);
    assert(bin_low.size() > 0);
    if (x<bin_low[0]) {
        LogDebug("piecewise") << "underflow: " << x << "<" << bin_low[0];
        return TMath::QuietNaN();
    }
    for(unsigned int i=1;i<bin_low.size();i++) {
        if(bin_low[i] > x)
            return bin_val[i-1];
    }
    if(x == bin_low[bin_low.size()-1])
        return bin_val[bin_val.size()-1];
    
    LogDebug("piecewise") << "overflow: " << x << ">" << bin_low[bin_low.size()-1];
    return TMath::QuietNaN();
}

double BTagSystematicsWeightProducer::scaleFactor(BTagSystematicsWeightProducer::Flavour flavour, BTagSystematicsWeightProducer::BTagAlgo algo, double pt, double eta_, double& sfUp, double& sfDown) {
    double sf = 0.0;
    double eta = fabs(eta_);
    bool ptOverFlow = false;
    bool ptUnderFlow = false;
    bool etaOverFlow = false;
    
    if (pt>800.0){
        pt=800.0;
        ptOverFlow = true;
    }
    if (pt<20.0) {
        pt=20.0;
        ptUnderFlow = true;
    }
    if (fabs(eta)>2.4) {
        etaOverFlow = true;
    }
    
    if(etaOverFlow) {
        edm::LogInfo("scaleFactor") << "eta overflow: " << eta << ">" << "2.4, setting scale factors to 1";
        sf = 1.0;
        sfUp = 1.0;
        sfDown = 1.0;
        return sf;
    }
    
    auto SFerr = [&sf, &sfUp, &sfDown] (double sfErr) {
        sfUp = sf + sfErr;
        sfDown = sf - sfErr;
    };
    
    //https://twiki.cern.ch/twiki/pub/CMS/BtagPOG/SFb-pt_payload_Moriond13.txt
    auto sfB_CSVM = [&pt] () {
        double x = pt;
        return 0.726981*((1.+(0.253238*x))/(1.+(0.188389*x)));
    };
    
    //Tagger: TCHPT within 20 < pt < 800 GeV, abs(eta) < 2.4, x = pt
    auto sfB_TCHPT = [&pt] () {
        double x = pt;
        return 0.305208*((1.+(0.595166*x))/(1.+(0.186968*x)));
    };
    
    //https://twiki.cern.ch/twiki/pub/CMS/BtagPOG/SFlightFuncs_Moriond2013.C
    //Data period ABCD
    auto sfL_CSVM = [&eta, &pt, &sfUp, &sfDown] () {
        double x = pt;
        if(eta >= 0.0 && eta < 0.8) {
            sfDown = ((0.972746+(0.00104424*x))+(-2.36081e-06*(x*x)))+(1.53438e-09*(x*(x*x)));
            sfUp = ((1.15201+(0.00292575*x))+(-7.41497e-06*(x*x)))+(5.0512e-09*(x*(x*x)));
            return ((1.06238+(0.00198635*x))+(-4.89082e-06*(x*x)))+(3.29312e-09*(x*(x*x)));
        }
        else if(eta >= 0.8 && eta < 1.6) {
            sfDown = ((0.9836+(0.000649761*x))+(-1.59773e-06*(x*x)))+(1.14324e-09*(x*(x*x)));
            sfUp = ((1.17735+(0.00156533*x))+(-4.32257e-06*(x*x)))+(3.18197e-09*(x*(x*x)));
            return ((1.08048+(0.00110831*x))+(-2.96189e-06*(x*x)))+(2.16266e-09*(x*(x*x)));
        }
        else if(eta >= 1.6 && eta < 2.4) {
            sfDown = ((1.00616+(0.000358884*x))+(-1.23768e-06*(x*x)))+(6.86678e-10*(x*(x*x)));
            sfUp = ((1.17671+(0.0010147*x))+(-3.66269e-06*(x*x)))+(2.88425e-09*(x*(x*x)));
            return ((1.09145+(0.000687171*x))+(-2.45054e-06*(x*x)))+(1.7844e-09*(x*(x*x)));
        }
        else { //jet eta overflow
            sfUp = TMath::QuietNaN();
            sfDown = TMath::QuietNaN();
            return TMath::QuietNaN();
        }
    };
    auto sfL_TCHPT = [&eta, &pt, &sfUp, &sfDown] () {
        double x = pt;
        
        //Data period ABCD
        if(eta >= 0.0 && eta < 2.4) {
            sfDown = ((0.988346+(0.000914722*x))+(-2.37077e-06*(x*x)))+(1.72082e-09*(x*(x*x)));
            sfUp = ((1.34691+(0.00181637*x))+(-4.64484e-06*(x*x)))+(3.27122e-09*(x*(x*x)));
            return ((1.1676+(0.00136673*x))+(-3.51053e-06*(x*x)))+(2.4966e-09*(x*(x*x)));
        } else { //jet eta overflow
            sfUp = TMath::QuietNaN();
            sfDown = TMath::QuietNaN();
            return TMath::QuietNaN();
        }
    };
    
    if( flavour == BTagSystematicsWeightProducer::b ) {
        if( algo == BTagSystematicsWeightProducer::CSVM ) {
            sf = sfB_CSVM();
            //double sfErr = 0;
            double sfErr = piecewise(pt, SFb_ptBins, SFb_CSVM_Err);
            if(ptOverFlow || ptUnderFlow)
                sfErr = 2*sfErr;
            SFerr(sfErr);
        } else if(algo == BTagSystematicsWeightProducer::TCHPT) {
            sf = sfB_TCHPT();
            double sfErr = piecewise(pt, BTagSystematicsWeightProducer::SFb_ptBins, BTagSystematicsWeightProducer::SFb_TCHPT_Err);
            if(ptOverFlow || ptUnderFlow)
                sfErr = 2*sfErr;
            SFerr(sfErr);
        } else {
            throw cms::Exception("scaleFactor") << "algo " << algo << " not implemented";
        }
    }
    //for c use the b SF but increase unc. by a factor of 2
    else if( flavour==BTagSystematicsWeightProducer::c ) {
        if(algo == BTagSystematicsWeightProducer::CSVM) {
            sf = sfB_CSVM();
            double sfErr = piecewise(pt, BTagSystematicsWeightProducer::SFb_ptBins, BTagSystematicsWeightProducer::SFb_CSVM_Err);
            sfErr = 2*sfErr;
            if(ptOverFlow || ptUnderFlow)
                sfErr = 2*sfErr;
            SFerr(sfErr);
            
        } else if(algo == BTagSystematicsWeightProducer::TCHPT) {
            sf = sfB_TCHPT();
            double sfErr = piecewise(pt, BTagSystematicsWeightProducer::SFb_ptBins, BTagSystematicsWeightProducer::SFb_TCHPT_Err);
            sfErr = 2*sfErr;
            if(ptOverFlow || ptUnderFlow)
                sfErr = 2*sfErr;
            SFerr(sfErr);
        } else {
            throw cms::Exception("scaleFactor") << "algo " << algo << " not implemented";
        }
    }
    else if( flavour==BTagSystematicsWeightProducer::l) {
        if(algo == BTagSystematicsWeightProducer::CSVM)
            sf = sfL_CSVM();
        else if(algo == BTagSystematicsWeightProducer::TCHPT)
            sf = sfL_TCHPT();
        else
            throw cms::Exception("scaleFactor") << "algo " << algo << " not implemented";
    }
    else {
        throw cms::Exception("scaleFactor") << "Unrecognized jet flavour for scaleFactor():" << flavour;
    }
    LogDebug("scaleFactor") << "\t\tsf=" << sf;
    return sf;
}

BTagSystematicsWeightProducer::BTagSystematicsWeightProducer(const edm::ParameterSet& iConfig)
: jetSrc(iConfig.getParameter<edm::InputTag>("src"))
, nJetSrc(iConfig.getParameter<edm::InputTag>("nJetSrc"))
, nTagSrc(iConfig.getParameter<edm::InputTag>("nTagSrc"))
, effFileB(iConfig.getParameter<edm::FileInPath>("efficiencyFileB"))
, effFileC(iConfig.getParameter<edm::FileInPath>("efficiencyFileC"))
, effFileL(iConfig.getParameter<edm::FileInPath>("efficiencyFileL"))
{
    const std::string algo = iConfig.getParameter<std::string>("algo");
    if(algo.compare("CSVM") == 0) {
        bTagAlgo = BTagSystematicsWeightProducer::CSVM;
    } else if(algo.compare("TCHPT") == 0) {
        bTagAlgo = BTagSystematicsWeightProducer::TCHPT;
    } else {
        throw cms::Exception("scaleFactor") << "algo " << algo << " not implemented";
    }

    edm::LogInfo("constructor") << "Using efficency files: b=" << effFileB.fullPath()
        << " c=" << effFileC.fullPath() << " l=" << effFileL.fullPath();
    effTFileB = new TFile(effFileB.fullPath().c_str());
    effTFileC = new TFile(effFileC.fullPath().c_str());
    effTFileL = new TFile(effFileL.fullPath().c_str());
    
    effHists_2J[BTagSystematicsWeightProducer::b] = (TH2D*)effTFileB->Get("2J/eff_b");
    effHists_2J[BTagSystematicsWeightProducer::c] = (TH2D*)effTFileC->Get("2J/eff_c");
    effHists_2J[BTagSystematicsWeightProducer::l] = (TH2D*)effTFileL->Get("2J/eff_l");
    
    effHists_3J[BTagSystematicsWeightProducer::b] = (TH2D*)effTFileB->Get("3J/eff_b");
    effHists_3J[BTagSystematicsWeightProducer::c] = (TH2D*)effTFileC->Get("3J/eff_c");
    effHists_3J[BTagSystematicsWeightProducer::l] = (TH2D*)effTFileL->Get("3J/eff_l");
    
    produces<float>("bTagWeight");
    produces<float>("bTagWeightSystBCUp");
    produces<float>("bTagWeightSystBCDown");
    produces<float>("bTagWeightSystLUp");
    produces<float>("bTagWeightSystLDown");

    produces<std::vector<float>>("scaleFactors");
}

/*
 Produces the vector of k-length combinations of integers from the set of integers [0,n-1].
 For example, combinations(3, 2, out) produces a vector of vectors with the following elements
 (
 (0,1)
 (0,2)
 (1,2)
 )
 */
void BTagSystematicsWeightProducer::combinations(const unsigned int n, const unsigned int k, Combinations& combs) {
    std::vector<bool> v(n);
    std::fill(v.begin()+v.size()-k, v.end(), true);
    do {
        std::vector<unsigned int> comb;
        for(unsigned int i=0;i<v.size();i++) {
            if(v[i])
                comb.push_back(i);
        }
        combs.push_back(comb);
    }
    while(std::next_permutation(v.begin(), v.end()));
    std::reverse(combs.begin(), combs.end());
}


BTagSystematicsWeightProducer::~BTagSystematicsWeightProducer()
{
}


//
// member functions
//

// ------------ method called to produce the data  ------------
void
BTagSystematicsWeightProducer::produce(edm::Event& iEvent, const edm::EventSetup& iSetup)
{

    std::vector<float> scale_factors;
    double P_mc = 0.0;
    double P_data = 0.0;
    double P_data_bcUp = 0.0;
    double P_data_bcDown = 0.0;
    double P_data_lUp = 0.0;
    double P_data_lDown = 0.0;

    using namespace edm;
    Handle<View<reco::Candidate> > jetsIn;
    iEvent.getByLabel(jetSrc, jetsIn);
  
    unsigned int nJets_ev=0;
    unsigned int nTags_ev=0;

    Handle<int> nJetsIn;
    iEvent.getByLabel(nJetSrc, nJetsIn);
    Handle<int> nTagsIn;
    iEvent.getByLabel(nTagSrc, nTagsIn);

    nJets_ev = *nJetsIn;
    nTags_ev = *nTagsIn;
    
    //Precalculate the tagging combinations
    combs.clear();
    combinations(nJets_ev, nTags_ev, combs);

    LogDebug("produce") << "This event has " << jetsIn->size() << " jets";
    if (nJets_ev >jetsIn->size()) {
        LogInfo("produce") << "Requested jet selection: " << nJets_ev << " jets of which " << nTags_ev <<
            " are to be b-tagged, but event has " << jetsIn->size() << " jets: not enough jets!" << " Skipping event.";
        return;
        //throw cms::Exception("produce") << "Not enough jets in event for b-tag reweighting: " << jetsIn->size() << "<" << nJets;
    }
    else if (nJets_ev<jetsIn->size()) {
        LogInfo("produce") << "Requested jet selection: " << nJets_ev << " jets of which " << nTags_ev <<
            " are to be b-tagged, but event has " << jetsIn->size() << " jets: truncating collection!"; 
    }
    LogDebug("produce") << "nJets=" << nJets_ev << " nTags=" << nTags_ev;
    
    //Make a list of the pointers to the first nJets jets
    std::vector<const reco::Candidate *> jets;
    for (unsigned int i=0;i<nJets_ev;i++) {
        jets.push_back(&(jetsIn->at(i)));
    }
    
    LogDebug("produce") << "Looping over " << combs.size() << " combinations";

    for(std::vector<unsigned int>& comb : combs) {
        LogDebug("combLoop") << "\tConsidering the following jets as b-tagged: " << vec_to_str<unsigned int>(comb);

        unsigned int jetIdx = 0;


        //prob. that this comb passed b-tagging in mc/data
        double p_mc = 1.0;
        double p_data = 1.0;
        
        double p_data_bcUp = 1.0;
        double p_data_bcDown = 1.0;
        double p_data_lUp = 1.0;
        double p_data_lDown = 1.0;
        
        LogDebug("combLoop") << "\tLooping over " << jets.size() << " jets";
        for (const auto* pjet_ : jets) {
            //const auto& jet_ = *pjet_;
            const pat::Jet& jet = static_cast<const pat::Jet&>(*pjet_);
            
            bool inComb = std::find(comb.begin(), comb.end(), jetIdx) != comb.end();
            LogDebug("jetLoop") << "\tConsidering jet with index " << jetIdx;

            if(inComb) LogDebug("jetLoop") << "\t\tJet " << jetIdx << " is in b-tag combination, using b-tag probability";
            else LogDebug("jetLoop") << "\t\tJet " << jetIdx << " is NOT in b-tag combination, using mistag probability";
            
           
            //Calculates the probability of this jet to pass-btagging in data and mc.
            //p_data and p_mc are modified on the fly.
            auto prob = [&, &p_mc, &p_data, inComb, jet, this] (BTagSystematicsWeightProducer::Flavour flavour) {
                LogDebug("jetLoop") << "\t\tprob(): flavour=" << flavour;
                
                //Returns x if _inComb==true, (1-x) otherwise
                //That means that if the jet is considered as a b-tag, the probability associated with b-tagging
                //is the measured flavour/sample-dependent probability of a jet to be b-tagged (eff_flavour).
                //Otherwise, the probability of NOT b-tagging is 1-eff_flavour. 
                auto eff = [] (double x, bool _inComb) -> double {
                    return _inComb ? x : 1.0 - x;
                };
                
                //The probability associated with a jet is eff if the jet is in the combination of b-tagged jets, (1-eff) otherwise
                double eff_val = TMath::QuietNaN();

                auto get_hist_eff = [&jet] (TH2D* hist) {
                    return hist->GetBinContent(hist->FindBin(jet.pt(), std::fabs(jet.eta()))); 
                };

                if (nJets_ev==2) {
                    eff_val = get_hist_eff(effHists_2J[flavour]);
                    LogDebug("jetLoop") << "2J eff = " << eff_val;
                    //eff_val = (*effs_in2J)[flavour];
                }
                else if (nJets_ev>2) {
                    eff_val = get_hist_eff(effHists_3J[flavour]);
                    LogDebug("jetLoop") << "2+J eff = " << eff_val;
                    //eff_val = (*effs_in3J)[flavour];
                }
                else {
                    edm::LogInfo("jetLoop") << "Don't know what efficiency to take for NJ=" << nJets_ev;
                }
                LogDebug("jetLoop") << "\t\teff_val=" << eff_val;
                //double e = eff(eff_val, inComb);
                
                //per-event jet probabilities multiply
                p_mc = p_mc * eff(eff_val, inComb);
                
                //Calculate the pt, eta and flavour dependent scale factors, including the flavour-dependent variations.
                double sfUp, sfDown;
                double sf = scaleFactor(flavour, BTagSystematicsWeightProducer::bTagAlgo, jet.pt(), jet.eta(), sfUp, sfDown);
                scale_factors.push_back(sf); 
                //if (inComb) LogDebug("jetLoop") << "\t\tpass b-tagging e_tag=" << e << " sf=" << sf << " sfUp=" << sfUp << " sfDown=" << sfDown;
                //else LogDebug("jetLoop") << "\t\tfail b-tagging e_mistag=" << e << " sf=" << sf << " sfUp=" << sfUp << " sfDown=" << sfDown;

                p_data = p_data * eff(sf * eff_val, inComb); 
                LogDebug("jetLoop") << "\t\tp_mc=" << p_mc << " p_data=" << p_data;
                if( flavour == BTagSystematicsWeightProducer::b || flavour == BTagSystematicsWeightProducer::c ) {
                    p_data_lUp = p_data_lUp * eff(sf * eff_val, inComb); 
                    p_data_lDown = p_data_lDown * eff(sf * eff_val, inComb); 
                    p_data_bcUp = p_data_bcUp * eff(sfUp * eff_val, inComb); 
                    p_data_bcDown = p_data_bcDown * eff(sfDown * eff_val, inComb); 
                    LogDebug("jetLoop") << "\t\tp_data_bcUp=" << p_data_bcUp << " p_data_bcDown=" << p_data_bcDown;
                }
                else if(flavour == BTagSystematicsWeightProducer::l) {
                    p_data_lUp = p_data_lUp * eff(sfUp * eff_val, inComb);
                    p_data_lDown = p_data_lDown * eff(sfDown * eff_val, inComb); 
                    p_data_bcUp = p_data_bcUp * eff(sf * eff_val, inComb);
                    p_data_bcDown = p_data_bcDown * eff(sf * eff_val, inComb); 
                    LogDebug("jetLoop") << "\t\tp_data_lUp=" << p_data_lUp << " p_data_lDown=" << p_data_lDown;
                }
            };
            
            if(abs(jet.partonFlavour()) == 5) { //b-jet
                prob(BTagSystematicsWeightProducer::b); //multiply the probability corresponding to the b-jet
                LogDebug("jetLoop") << "\t\tflavour is b-jet";
            }
            else if(abs(jet.partonFlavour())==4) { //c-jet
                prob(BTagSystematicsWeightProducer::c);
                LogDebug("jetLoop") << "\t\tflavour is c-jet";
            }
            else if(abs(jet.partonFlavour())!=4 && abs(jet.partonFlavour())!=5) { //light jet, hermetic definition
                prob(BTagSystematicsWeightProducer::l);
                LogDebug("jetLoop") << "\t\tflavour is l-jet";
            }
            else {
                throw cms::Exception("produce") << "Jet flavour not handled!";
            }
            LogDebug("jetLoop") << "\t\tJet " << "pt=" << jet.pt() << " eta=" << jet.eta()
            << "flavour=" << jet.partonFlavour() << " p_mc=" << p_mc << " p_data=" << p_data;    
            
            jetIdx++;
        }
        
        LogDebug("combLoop") <<
            "\tcombination probs p_mc=" << p_mc << " p_data=" << p_data
            << " p_data_bcUp=" << p_data_bcUp  << " p_data_bcDown=" << p_data_bcDown
            << " p_data_lUp=" << p_data_lUp  << " p_data_lDown=" << p_data_lDown;
        //Probabilities of different combinations add
        P_mc += p_mc;
        P_data += p_data;
        
        
        P_data_bcUp += p_data_bcUp;
        P_data_bcDown += p_data_bcDown;
        P_data_lUp += p_data_lUp;
        P_data_lDown += p_data_lDown;
        
    }
    LogDebug("produce") << "event prob P_mc=" << P_mc << " P_data=" << P_data << " P_data_bcUp=" << P_data_bcUp << " P_data_bcDown=" << P_data_bcDown << " P_data_lUp=" << P_data_lUp << " P_data_lDown=" << P_data_lDown;
    
    double w = P_data/P_mc;
    double w_bcUp = P_data_bcUp/P_mc;
    double w_bcDown = P_data_bcDown/P_mc;
    double w_lUp = P_data_lUp/P_mc;
    double w_lDown = P_data_lDown/P_mc;
    LogDebug("produce") << "event weights w=" << w << " w_bcUp=" << w_bcUp << " w_bcDown=" << w_bcDown << " w_lUp=" << w_lUp << " w_lDown=" << w_lDown;
    
    iEvent.put(std::auto_ptr<float>(new float(w)), "bTagWeight");
    iEvent.put(std::auto_ptr<float>(new float(w_bcUp)), "bTagWeightSystBCUp");
    iEvent.put(std::auto_ptr<float>(new float(w_bcDown)), "bTagWeightSystBCDown");
    iEvent.put(std::auto_ptr<float>(new float(w_lUp)), "bTagWeightSystLUp");
    iEvent.put(std::auto_ptr<float>(new float(w_lDown)), "bTagWeightSystLDown");
    iEvent.put(std::auto_ptr<std::vector<float>>(new std::vector<float>(scale_factors)), "scaleFactors");
    
    
}

// ------------ method called once each job just before starting event loop  ------------
void
BTagSystematicsWeightProducer::beginJob()
{
}

// ------------ method called once each job just after ending the event loop  ------------
void
BTagSystematicsWeightProducer::endJob() {
}

// ------------ method called when starting to processes a run  ------------
void
BTagSystematicsWeightProducer::beginRun(edm::Run&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a run  ------------
void
BTagSystematicsWeightProducer::endRun(edm::Run&, edm::EventSetup const&)
{
}

// ------------ method called when starting to processes a luminosity block  ------------
void
BTagSystematicsWeightProducer::beginLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a luminosity block  ------------
void
BTagSystematicsWeightProducer::endLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&)
{
}

// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void
BTagSystematicsWeightProducer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
    //The following says we do not know what parameters are allowed so do no validation
    // Please change this to state exactly what you do use, even if it is no parameters
    edm::ParameterSetDescription desc;
    desc.setUnknown();
    descriptions.addDefault(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(BTagSystematicsWeightProducer);
