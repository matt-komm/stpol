// -*- C++ -*-
//
// Package:    PDFweightsProducer
// Class:      PDFweightsProducer
// 
/**\class PDFweightsProducer PDFweightsProducer.cc SingleTopPolarization/PDFweightsProducer/src/PDFweightsProducer.cc

 Description: [one line class summary]

 Implementation:
     [Notes on implementation]
*/
//
// Original Author:  Mait Muntel
//         Created:  Wed Mar 13 11:20:00 EET 2013
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
#include "FWCore/MessageLogger/interface/MessageLogger.h"
#include "TMath.h"
#include <vector>
#include <map>
#include "FWCore/Framework/interface/ESHandle.h"
#include "DataFormats/HepMCCandidate/interface/PdfInfo.h"
#include "SimDataFormats/GeneratorProducts/interface/GenEventInfoProduct.h"

#include "FWCore/ParameterSet/interface/FileInPath.h"
#include "DataFormats/Math/interface/LorentzVector.h"
#include <iostream>
#include <fstream>
#include <sstream>

using namespace std;
//
// class declaration
//

class PDFweightsProducer : public edm::EDProducer {
   public:
      explicit PDFweightsProducer(const edm::ParameterSet&);
      ~PDFweightsProducer();

      static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);

   private:
      virtual void beginJob() ;
      virtual void produce(edm::Event&, const edm::EventSetup&);
      virtual void endJob() ;
      
      virtual void beginRun(edm::Run&, edm::EventSetup const&);
      virtual void endRun(edm::Run&, edm::EventSetup const&);
      virtual void beginLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&);
      virtual void endLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&);

      // ----------member data ---------------------------
	
	float	scalePDF;
	float	x1,x2;
	int		id1,id2;
	
	std::vector<std::string>	PDFSets;
	std::vector<std::string>	PDFnames;

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
PDFweightsProducer::PDFweightsProducer(const edm::ParameterSet& iConfig)
{
	produces<float>(string("scalePDF"));
	produces<float>(string("x1"));
	produces<float>(string("x2"));
	produces<int>(string("id1"));
	produces<int>(string("id2"));
	
}


PDFweightsProducer::~PDFweightsProducer()
{
 
   // do anything here that needs to be done at desctruction time
   // (e.g. close files, deallocate resources etc.)

}


//
// member functions
//

// ------------ method called to produce the data  ------------
void
PDFweightsProducer::produce(edm::Event& iEvent, const edm::EventSetup& iSetup)
{
	using namespace edm;
	
	// get the parton flavour, momentum fraction and energy scale
	edm::Handle<GenEventInfoProduct> genprod;
	iEvent.getByLabel("generator",genprod);

	scalePDF=	genprod->pdf()->scalePDF;
	x1		=	genprod->pdf()->x.first;
	x2		=	genprod->pdf()->x.second;
	id1		=	genprod->pdf()->id.first;
	id2		=	genprod->pdf()->id.second;

    iEvent.put(std::auto_ptr<float>(new float(scalePDF)), string("scalePDF"));
	iEvent.put(std::auto_ptr<float>(new float(x1)), string("x1"));
	iEvent.put(std::auto_ptr<float>(new float(x2)), string("x2"));
	iEvent.put(std::auto_ptr<int>(new int(id1)), string("id1"));
	iEvent.put(std::auto_ptr<int>(new int(id2)), string("id2"));
}

// ------------ method called once each job just before starting event loop  ------------
void 
PDFweightsProducer::beginJob()
{
}

// ------------ method called once each job just after ending the event loop  ------------
void 
PDFweightsProducer::endJob() {
}

// ------------ method called when starting to processes a run  ------------
void 
PDFweightsProducer::beginRun(edm::Run&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a run  ------------
void 
PDFweightsProducer::endRun(edm::Run&, edm::EventSetup const&)
{
}

// ------------ method called when starting to processes a luminosity block  ------------
void 
PDFweightsProducer::beginLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a luminosity block  ------------
void 
PDFweightsProducer::endLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&)
{
}

// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void
PDFweightsProducer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(PDFweightsProducer);
