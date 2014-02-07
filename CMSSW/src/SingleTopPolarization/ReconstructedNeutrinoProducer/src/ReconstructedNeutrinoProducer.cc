// -*- C++ -*-
//
// Package:    ReconstructedNeutrinoProducer
// Class:      ReconstructedNeutrinoProducer
// 
/**\class ReconstructedNeutrinoProducer ReconstructedNeutrinoProducer.cc SingleTopPolarization/ReconstructedNeutrinoProducer/src/ReconstructedNeutrinoProducer.cc

 Description: Reconstructs the neutrino 4-momentum in the decay W->lepton, neutrino using the W mass constraint.

 Implementation:
    The z-momentum ambiguity can be solved in various ways, here the rescaling of the W mass or solving for new (p_nu, p_nu_y) using the on-shell constraint is used.
*/
//
// Original Author:  
//         Created:  Wed Sep 26 16:21:03 EEST 2012
// $Id$
//
//


// system include files
#include <memory>
#include <array>
#include <algorithm>
#include <cmath>

// user include files
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/EDProducer.h"

#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"

#include <DataFormats/PatCandidates/interface/Muon.h>
#include <DataFormats/Candidate/interface/Candidate.h> 
#include <DataFormats/RecoCandidate/interface/RecoCandidate.h>
#include <DataFormats/Candidate/interface/CompositeCandidate.h>

#include "FWCore/MessageLogger/interface/MessageLogger.h"

#include "FWCore/Utilities/interface/InputTag.h"

#include "CommonTools/UtilAlgos/interface/StringCutEventSelector.h"

//Cubic equation solver
#include <gsl/gsl_poly.h>
#include <gsl/gsl_complex.h>


template <const int solStrategy>
class ReconstructedNeutrinoProducer : public edm::EDProducer {
   public:
      explicit ReconstructedNeutrinoProducer(const edm::ParameterSet&);
      ~ReconstructedNeutrinoProducer();

      static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);
      static const long double mW;


   private:
      virtual void beginJob() ;
      virtual void produce(edm::Event&, const edm::EventSetup&);
      virtual void endJob() ;
      
      virtual void beginRun(edm::Run&, edm::EventSetup const&);
      virtual void endRun(edm::Run&, edm::EventSetup const&);
      virtual void beginLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&);
      virtual void endLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&);


      //float p_Nu_z(const reco::Candidate& chLepton, const reco::Candidate& met);
      //float p_Nu_z_complex_cubic(const reco::Candidate& chLepton, const reco::Candidate& met);

      const reco::CompositeCandidate::LorentzVector nuMomentum(const reco::Candidate& chLepton, const reco::Candidate& met, edm::Event& iEvent);
      const reco::CompositeCandidate::LorentzVector nuMomentum_complex_cubic(const reco::Candidate& chLepton, const reco::Candidate& met, double& Delta_);
      float p_Nu_z_mW_rescale(const reco::Candidate& chLepton, const reco::Candidate& met);
      float p_Nu_z(const reco::Candidate& chLepton, const reco::Candidate& met);

      edm::InputTag leptonSrc;
      edm::InputTag metSrc;
      const std::string outName;

      // ----------member data ---------------------------
};

template <const int solStrategy>
const long double ReconstructedNeutrinoProducer<solStrategy>::mW = 80.399;
//
// constants, enums and typedefs
//


//
// static data member definitions
//

//
// constructors and destructor
//
template <const int solStrategy>
ReconstructedNeutrinoProducer<solStrategy>::ReconstructedNeutrinoProducer(const edm::ParameterSet& iConfig)
: outName("")
{
  leptonSrc = iConfig.getParameter<edm::InputTag>("leptonSrc");
  metSrc = iConfig.getParameter<edm::InputTag>("metSrc");

  produces<std::vector<reco::CompositeCandidate> >(outName);
  produces<double>("Delta");
  produces<int>("solType");
  
}


template <const int solStrategy>
ReconstructedNeutrinoProducer<solStrategy>::~ReconstructedNeutrinoProducer()
{
 
   // do anything here that needs to be done at desctruction time
   // (e.g. close files, deallocate resources etc.)

}

template <const int solStrategy>
float ReconstructedNeutrinoProducer<solStrategy>::p_Nu_z(const reco::Candidate& chLepton, const reco::Candidate& met) {

  const auto& lp4 = chLepton.p4();
  const auto& metp4 = met.p4();
  
  float Lambda = std::pow(ReconstructedNeutrinoProducer<solStrategy>::mW, 2) / 2 + lp4.px()*metp4.px() + lp4.py()*metp4.py();
  LogDebug("p_Nu_z() MET kinematics") << "MET: px (" << metp4.Px() << ") py (" << metp4.Py() << ") pt (" << metp4.Pt() << ")";
  LogDebug("p_Nu_z() lepton kinematics") << "lepton: px (" << lp4.Px() << ") py (" << lp4.Py() << ") pz (" << lp4.Pz() << ") E (" << lp4.E() << ")";
  float Delta = std::pow(lp4.E(), 2) * (std::pow(Lambda, 2) - std::pow(lp4.Pt()*metp4.Pt(), 2) );
  float p_nu_z = TMath::QuietNaN();

  if(Delta>0.0) { //Real roots
    float r = TMath::Sqrt(Delta);
    float A = (Lambda*lp4.Pz() + r)/ std::pow(lp4.Pt(), 2);
    float B = (Lambda*lp4.Pz() - r)/ std::pow(lp4.Pt(), 2);
 
    //Choose root with minimal absolute value
    if (fabs(A) < fabs(B)) {
        p_nu_z = A;
    }
    else {
        p_nu_z = B;
    }
  }
  else { //Negative discriminant, complex roots (MET resolution effect)
    LogDebug("p_Nu_z():complex") << "Delta is negative, complex roots";
    p_nu_z = TMath::QuietNaN();
  }
  return p_nu_z;
}

template <const int solStrategy>
float ReconstructedNeutrinoProducer<solStrategy>::p_Nu_z_mW_rescale(const reco::Candidate& chLepton, const reco::Candidate& met) {
  const auto& lp4 = chLepton.p4();
  const auto& metp4 = met.p4();

  float sk1 = lp4.Pt()*metp4.Pt();
  float sk2 = metp4.Px()*lp4.Px() + metp4.Py()*lp4.Py();
  float mW_new = TMath::Sqrt(2*(sk1-sk2));
  LogDebug("p_Nu_z():complex") << "Choosing new mW value to make Delta==0: mW_new=" << mW_new;
  float Lambda_new = std::pow(mW_new, 2) / 2.0 + sk2;
  //float Delta_new = (std::pow(Lambda_new, 2) - std::pow(sk1, 2))*std::pow(lp4.E(), 2);
  float p_nu_z = (Lambda_new*lp4.Pz())/std::pow(lp4.Pt(), 2);
  LogDebug("p_Nu_z():complex") << "p_nu_z with mW rescaling: " << p_nu_z;
  return p_nu_z;
}

template <const int solStrategy>
const reco::CompositeCandidate::LorentzVector ReconstructedNeutrinoProducer<solStrategy>::nuMomentum_complex_cubic(const reco::Candidate& chLepton, const reco::Candidate& met, double& Delta_) {
  LogDebug("p_Nu_z_complex_cubic()") << "Solving complex root problem with cubic equation";
  /*
   * 
        double EquationA = 1;
        double EquationB = -3 * pylep * mW / (ptlep);
        double EquationC = mW * mW * (2 * pylep * pylep) / (ptlep * ptlep) + mW * mW - 4 * pxlep * pxlep * pxlep * metpx / (ptlep * ptlep) - 4 * pxlep * pxlep * pylep * metpy / (ptlep * ptlep);
        double EquationD = 4 * pxlep * pxlep * mW * metpy / (ptlep) - pylep * mW * mW * mW / ptlep;
   * */

  long double lepPx = chLepton.p4().Px();
  long double lepPy = chLepton.p4().Py();
  long double lepPt = chLepton.p4().Pt();
  long double metPx = met.p4().Px();
  long double metPy = met.p4().Py();
  long double metPt = met.p4().Pt();
  const long double & mW = ReconstructedNeutrinoProducer<solStrategy>::mW;
 
  long double b = -3.0*lepPy*mW / lepPt;
  //long double c = 2.0*std::pow(mW*lepPy, (long double)2) / std::pow(lepPt, (long double)2) + std::pow(mW, (long double)2) - 
  //(long double)4.0* std::pow(lepPx, (long double)3)*metPx/std::pow(lepPt, (long double)2) - (long double)4.0*std::pow(lepPx, (long double)2)*lepPy*metPy/std::pow(lepPt, (long double)2);
  long double c = (std::pow(mW, 2.0) * (lepPx*lepPx + 3*lepPy*lepPy) - 4.0*std::pow(lepPx, 2.0) * (metPx*lepPx + metPy*lepPy)) / std::pow(lepPt, 2.0); 
  long double d = (4.0*mW*metPy*std::pow(lepPx, 2.0) - lepPy*std::pow(mW, 3.0))/lepPt;
  //long double d = (long double)(4.0)*std::pow(lepPx, (long double)2.0)*metPy*mW / lepPt - lepPy*std::pow(mW, (long double)3.0) / lepPt;

  const gsl_complex cnan{{TMath::QuietNaN(), TMath::QuietNaN()}};
  std::array<gsl_complex, 3> solsA{{cnan, cnan, cnan}};
  std::array<gsl_complex, 3> solsB{{cnan, cnan, cnan}};
  int nSolsA = gsl_poly_complex_solve_cubic(b, c, d, &(solsA[0]), &(solsA[1]), &(solsA[2]));
  int nSolsB = gsl_poly_complex_solve_cubic(-b, c, -d, &(solsB[0]), &(solsB[1]), &(solsB[2]));
#define COMP(A) GSL_REAL(A) << " " << GSL_IMAG(A)
  LogDebug("p_Nu_z_complex_cubic()") << "Cubic equation x**3 + " << b << " x**2 + " << c << " x**1 + " << d << " = 0 has " << nSolsA << " roots: " << COMP(solsA[0]) << " | " << COMP(solsA[1]) << " | " << COMP(solsA[2]);
  LogDebug("p_Nu_z_complex_cubic()") << "Cubic equation x**3 + " << -b << " x**2 + " << c << " x**1 + " << -d << " = 0 has " << nSolsB << " roots: " << COMP(solsB[0]) << " | " << COMP(solsB[1]) << " | " << COMP(solsB[2]);

  //eqSign is -1 for x**3+bx**2+cx**1+d==0
  //eqSign is +1 for x**3-bx**2+cx**1+d==0
  auto nuMomenta = [&b, &c, &d, &mW, &lepPx, &lepPy, &lepPt](const gsl_complex& _sol, double* _px, double* _py, const double & eqSign) {
      //double p_x = (solutions[i] * solutions[i] - mW * mW) / (4 * pxlep);
      //double p_y = ( mW * mW * pylep + 2 * pxlep * pylep * p_x - mW * ptlep * solutions[i]) / (2 * pxlep * pxlep);
      long double sol = (long double)(GSL_REAL(_sol));
      LogDebug("p_Nu_z_complex_cubic():nuMomenta") << "eqSign = " << eqSign;
      LogDebug("p_Nu_z_complex_cubic():nuMomenta") << "Constraint = " << (double)(std::pow(sol, (long double)3.0) - eqSign*b*std::pow(sol, (long double)2.0) + c*std::pow(sol, (long double)1.0) - eqSign*d);
      long double px = (sol*sol - std::pow(mW, 2.0)) / (4.0*lepPx);
      long double py = (std::pow(mW, 2.0)*lepPy + 2.0*lepPx*lepPy*px + eqSign*mW*lepPt*sol) / (2.0 * std::pow(lepPx, 2.0));
      *(_px) = (double)px;
      *(_py) = (double)py;
      LogDebug("p_Nu_z_complex_cubic():nuMomenta") << "New momentum corresponding to solution (" << COMP(_sol) << "): " << px << " " << py; 
      //return;
  };

  auto Delta2 = [&metPx, &metPy](double& _px, double& _py) {
      double D = std::pow(_px-metPx, 2) + std::pow(_py-metPy, 2);
      LogDebug("p_Nu_z_complex_cubic():Delta2") << "Delta2(" << _px << ", " << _py << ") = " << D;
      return (double)D;
  };

  std::vector<std::array<double, 3> > newMomenta;

  auto calcNewMomenta = [&nuMomenta, &Delta2](std::vector<std::array<double, 3> > & outVect, const gsl_complex & c, const double & eqSign) {
      if (fabs(GSL_IMAG(c)) > 0.000001) return;
      double px = TMath::QuietNaN();
      double py = TMath::QuietNaN();
      nuMomenta(c, &px, &py, eqSign);
      double D = Delta2(px, py);

      const std::array<double, 3> arr{{px, py, D}};
      outVect.push_back(arr);
  };

  for(auto& s : solsA) {
      calcNewMomenta(newMomenta, s, -1.0);
  }
  for(auto& s : solsB) {
      calcNewMomenta(newMomenta, s, 1.0);
  }

  auto compare = [](const std::array<double, 3> & a, const std::array<double, 3> & b) {
      return bool(a[2]<b[2]); 
  };

  std::sort(newMomenta.begin(), newMomenta.end(), compare);

  for (auto& arr : newMomenta) {
      LogDebug("p_Nu_z_complex_cubic()") << "sorted p_nu_x, p_nu_y: " << arr[0] << " " << arr[1] << " -> D = " << arr[2];
  }
  LogDebug("p_Nu_z_complex_cubic()") << "Best guess for new (p_nu_x, p_nu_y) is (" << newMomenta[0][0] << ", " << newMomenta[0][1] << ") with old MET (" << metPx << ", " << metPy << ")";
  
  double& newPx = newMomenta[0][0];
  double& newPy = newMomenta[0][1];
  double newPt = TMath::Sqrt(newPx*newPx+newPy*newPy);
  Delta_ = newMomenta[0][2];

  double Lambda_new = std::pow(mW, 2.0) / 2.0 + newPx*lepPx + newPy*lepPy;
  LogDebug("p_Nu_z_complex_cubic()") << "New discriminant is " << std::pow(Lambda_new, 2.0) - std::pow(lepPt*newPt, 2.0);
  double p_nu_z = Lambda_new * chLepton.p4().Pz() / std::pow(lepPt, 2.0);

  reco::CompositeCandidate::LorentzVector nuVec;
  nuVec.SetPx(newPx);
  nuVec.SetPy(newPy);
  nuVec.SetPz(p_nu_z);
  nuVec.SetE(TMath::Sqrt(nuVec.Px()*nuVec.Px() + nuVec.Py()*nuVec.Py() + nuVec.Pz()*nuVec.Pz()));

 // reco::CompositeCandidate::LorentzVector nuVec2 = reco::CompositeCandidate::LorentzVector(nuVec);
 // nuVec2.SetPz(-nuVec2.Pz());
 // LogDebug("p_Nu_z_complex_cubic()") << "eta1: " << nuVec.eta() << " eta2: " << nuVec2.eta();

  return (const reco::CompositeCandidate::LorentzVector)nuVec;
}

template <const int solStrategy>
const reco::CompositeCandidate::LorentzVector ReconstructedNeutrinoProducer<solStrategy>::nuMomentum(const reco::Candidate& chLepton, const reco::Candidate& met, edm::Event& iEvent) {
  const double& nan = TMath::QuietNaN();
  reco::CompositeCandidate::LorentzVector nuVec(nan, nan, nan, nan);
  double Delta = 0;
  int whichSol = -1;

 // float p_nu_z = p_Nu_z(chLepton, met);
 // if (p_nu_z==p_nu_z) { //real root
 //   nuVec.SetPx(met.p4().Px());
 //   nuVec.SetPy(met.p4().Py());
 //   nuVec.SetPz(p_nu_z);
 //   nuVec.SetE(TMath::Sqrt(nuVec.Px()*nuVec.Px() + nuVec.Py()*nuVec.Py() + nuVec.Pz()*nuVec.Pz()));
 //   whichSol = 0;
 // } else { //Complex root
 //   nuVec = nuMomentum_complex_cubic(chLepton, met, Delta);
 //   whichSol = 1;
 // }
 //
  
  //Always use complex solution
  if(solStrategy == 2) {
    nuVec = nuMomentum_complex_cubic(chLepton, met, Delta);
    whichSol = 2;
  }

  //Use real+complex solution
  else if(solStrategy==1 || solStrategy==0) {
 
    float p_nu_z = p_Nu_z(chLepton, met);
  
    if (p_nu_z==p_nu_z) { //real root
      nuVec.SetPx(met.p4().Px());
      nuVec.SetPy(met.p4().Py());
      nuVec.SetPz(p_nu_z);
      nuVec.SetE(TMath::Sqrt(nuVec.Px()*nuVec.Px() + nuVec.Py()*nuVec.Py() + nuVec.Pz()*nuVec.Pz()));
      whichSol = 0;
    } else { //Complex root
      if (solStrategy==0) { //mW rescaling
        edm::LogError("nuMomentum()") << "solStrategy==0 is not implemented!";
        assert(true);
      }
      else if(solStrategy == 1) { //Cubic equation
        nuVec = nuMomentum_complex_cubic(chLepton, met, Delta);
        whichSol = 1;
      }
    }
  }
  iEvent.put(std::auto_ptr<double>(new double(Delta)), "Delta");
  iEvent.put(std::auto_ptr<int>(new int(whichSol)), "solType");
  LogDebug("nuMomentum()") << "Finished nu momentum calculation using algo " << whichSol;

  return nuVec;
}


// ------------ method called to produce the data  ------------
template <const int solStrategy>
void
ReconstructedNeutrinoProducer<solStrategy>::produce(edm::Event& iEvent, const edm::EventSetup& iSetup)
{
   using namespace edm;

   Handle<View<reco::Candidate> > leptons;
   Handle<View<reco::Candidate> > mets;

   iEvent.getByLabel(leptonSrc, leptons);
   iEvent.getByLabel(metSrc, mets);


   std::auto_ptr<double> mtW(new double(0));

   std::auto_ptr<std::vector<reco::CompositeCandidate> > outNeutrinoColl(new std::vector<reco::CompositeCandidate>);
   reco::CompositeCandidate *nu = new reco::CompositeCandidate();
   reco::CompositeCandidate::LorentzVector nuVec;

   if(leptons->size()!=1 || mets->size()!=1) { //Need exactly 1 lepton and 1 MET
    edm::LogError("produce()") << "Event does not have correct final state for neutrino: nLeptons " << leptons->size() << " nMETs " << mets->size();
   }
   else {
    LogDebug("produce()") << "Event has correct final state for neutrino";

    const reco::Candidate& lepton(leptons->at(0));
    const reco::Candidate& MET(mets->at(0));

    nuVec = nuMomentum(lepton, MET, iEvent);
   }

   nu->setP4(nuVec);
   outNeutrinoColl->push_back(*nu);
   LogDebug("produce()") << "neutrino: pt (" << nu->pt() << ") eta (" << nu->eta() << ") phi (" << nu->phi() << ") et (" << nu->et() << ")";
   delete nu;

   iEvent.put(outNeutrinoColl, outName);

/* This is an event example
   //Read 'ExampleData' from the Event
   Handle<ExampleData> pIn;
   iEvent.getByLabel("example",pIn);

   //Use the ExampleData to create an ExampleData2 which 
   // is put into the Event
   std::auto_ptr<ExampleData2> pOut(new ExampleData2(*pIn));
   iEvent.put(pOut);
*/

/* this is an EventSetup example
   //Read SetupData from the SetupRecord in the EventSetup
   ESHandle<SetupData> pSetup;
   iSetup.get<SetupRecord>().get(pSetup);
*/
 
}

// ------------ method called once each job just before starting event loop  ------------
template <const int solStrategy>
void 
ReconstructedNeutrinoProducer<solStrategy>::beginJob()
{
}

// ------------ method called once each job just after ending the event loop  ------------
template <const int solStrategy>
void 
ReconstructedNeutrinoProducer<solStrategy>::endJob() {
}

// ------------ method called when starting to processes a run  ------------
template <const int solStrategy>
void 
ReconstructedNeutrinoProducer<solStrategy>::beginRun(edm::Run&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a run  ------------
template <const int solStrategy>
void 
ReconstructedNeutrinoProducer<solStrategy>::endRun(edm::Run&, edm::EventSetup const&)
{
}

// ------------ method called when starting to processes a luminosity block  ------------
template <const int solStrategy>
void 
ReconstructedNeutrinoProducer<solStrategy>::beginLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a luminosity block  ------------
template <const int solStrategy>
void 
ReconstructedNeutrinoProducer<solStrategy>::endLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&)
{
}

// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
template <const int solStrategy>
void
ReconstructedNeutrinoProducer<solStrategy>::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);
}

//define this as a plug-in

typedef ReconstructedNeutrinoProducer<1> ClassicReconstructedNeutrinoProducer;
DEFINE_FWK_MODULE(ClassicReconstructedNeutrinoProducer);
