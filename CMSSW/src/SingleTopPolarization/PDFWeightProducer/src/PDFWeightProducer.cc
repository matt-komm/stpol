// -*- C++ -*-
//
// Package:    PDFWeightProducer
// Class:      PDFWeightProducer
// 
/**\class PDFWeightProducer PDFWeightProducer.cc SingleTopPolarization/PDFWeightProducer/src/PDFWeightProducer.cc

 Description: [one line class summary]

 Implementation:
     Weights to be combined as described in http://www.hep.ucl.ac.uk/pdf4lhc/PDF4LHC_practical_guide.pdf
*/
//
// Original Author:  Joosep Pata
//         Created:  Tue Mar 11 15:19:14 EET 2014
// $Id$
//
//


// system include files
#include <memory>
#include <string>

// user include files
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/EDProducer.h"

#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include <SimDataFormats/GeneratorProducts/interface/GenEventInfoProduct.h>
#include "DataFormats/HepMCCandidate/interface/GenParticle.h"

//FIXME: import proper LHAPDF headers
namespace LHAPDF
{
    void initPDFSet(int nset, const std::string &filename, int member = 0);
    int numberPDF(int nset);
    void usePDFMember(int nset, int member);
    double xfx(int nset, double x, double Q, int fl);
    double getXmin(int nset, int member);
    double getXmax(int nset, int member);
    double getQ2min(int nset, int member);
    double getQ2max(int nset, int member);
    void extrapolate(bool extrapolate = true);
    int	numberPDF();
    void setPDFPath (const std::string &path);
    std::string pdfsetsPath();
    std::string pdfsetsIndexPath();
}

class PDFWeightProducer : public edm::EDProducer {
   public:
      explicit PDFWeightProducer(const edm::ParameterSet&);
      ~PDFWeightProducer();

      static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);

   private:
      virtual void beginJob() ;
      virtual void produce(edm::Event&, const edm::EventSetup&);
      virtual void endJob() ;
      
      virtual void beginRun(edm::Run&, edm::EventSetup const&);
      virtual void endRun(edm::Run&, edm::EventSetup const&);
      virtual void beginLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&);
      virtual void endLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&);
      
      const edm::InputTag genWeightSrc;
      const edm::InputTag genParticlesSrc;
      const std::vector<std::string> PDFSets;
    
      std::map<std::string, float> pdf_vars;
      std::map<std::string, std::vector<float>> pdf_weights;
      std::vector<std::string> PDFnames;

      const bool do_powheg_topmass_fix;
};

PDFWeightProducer::PDFWeightProducer(const edm::ParameterSet& iConfig) :
    genWeightSrc("generator"),
    genParticlesSrc("genParticles"),
    PDFSets(iConfig.getParameter<std::vector<std::string>>("PDFSets")),
    do_powheg_topmass_fix(iConfig.getParameter<bool>("doPowhegTopMassFix"))
{
    LHAPDF::setPDFPath("/home/andres/single_top/stpol_current/stpol/src/step2/pdfsets");
    for( unsigned int i = 0; i < PDFSets.size(); i++ ) {
        
        // make names of PDF sets to be saved
        std::string name = PDFSets[i];
        size_t pos = name.find_first_not_of("ZXCVBNMASDFGHJKLQWERTYUIOPabcdefghijklmnopqrstuvwxyz1234567890");
        std::map<std::string, int> map_name;
        while (pos!=std::string::npos){
            name = name.erase(pos, 1);
            pos = name.find_first_not_of("ZXCVBNMASDFGHJKLQWERTYUIOPabcdefghijklmnopqrstuvwxyz1234567890");
        }
        if( map_name.count(name) == 0 ) {
            map_name[name]=0;
            PDFnames.push_back(name);
        }
        else {
            map_name[name]++;
            std::ostringstream ostr;
            ostr << name << "xxx" << map_name[name];
            PDFnames.push_back(ostr.str());
        }
        std::cout << LHAPDF::pdfsetsPath() << std::endl;
        std::cout << LHAPDF::pdfsetsIndexPath() << std::endl;
        std::cout << "Initializing PDF set " << i << std::endl;
        LHAPDF::setPDFPath("/home/andres/single_top/stpol_current/stpol/src/step2/pdfsets");
        std::cout << LHAPDF::pdfsetsPath() << std::endl;
        std::cout << LHAPDF::pdfsetsIndexPath() << std::endl;
        LHAPDF::initPDFSet(i+1, PDFSets[i]);

        pdf_vars[std::string("pdf_w0"+PDFnames[i])] = 0.0;
        pdf_vars[std::string("pdf_n"+PDFnames[i])] = 0.0;
        
        std::cout << "Getting the number of PDF points in set" << std::endl;
        int nPDFSet = LHAPDF::numberPDF(i+1);
        pdf_weights[std::string("pdf_weights_"+PDFnames[i])] = std::vector<float>(nPDFSet);
        const char* weight_vec_name = std::string("weights" + PDFnames[i]).c_str();
        std::cout << "weights for " << PDFnames[i] << " as " << weight_vec_name;
        
        produces<int>(std::string("n"+PDFnames[i]));
        produces<float>(std::string("w0"+PDFnames[i]));

        produces<std::vector<float>>(std::string("weights"+PDFnames[i]));
    }
    produces<float>("scalePDF");
    produces<float>("x1");
    produces<float>("x2");
    produces<int>("id1");
    produces<int>("id2");
}


PDFWeightProducer::~PDFWeightProducer()
{
}


// ------------ method called to produce the data  ------------
void
PDFWeightProducer::produce(edm::Event& iEvent, const edm::EventSetup& iSetup)
{
	edm::Handle<GenEventInfoProduct> genprod;
	iEvent.getByLabel(genWeightSrc, genprod);

	float pdf_scalePDF = genprod->pdf()->scalePDF;
	float pdf_x1 = genprod->pdf()->x.first;
	float pdf_x2 = genprod->pdf()->x.second;
	int pdf_id1 = genprod->pdf()->id.first;
	int pdf_id2 = genprod->pdf()->id.second;
    
    // Ad-hoc fix for POWHEG
    // POWHEEG stores generator info wrongly, need to get top mass to multiply
    if (do_powheg_topmass_fix) {
        edm::Handle<reco::GenParticleCollection> genParticles;
        if (!iEvent.getByLabel(genParticlesSrc, genParticles)) {
            throw 1;
        }

        //get gen-level top
        unsigned int gensize = genParticles->size();
        double mtop = 0.0;
        for(unsigned int i = 0; i<gensize; ++i) {
            const reco::GenParticle& part = (*genParticles)[i];
            int status = part.status();
            if (status!=3) continue;
            int id = part.pdgId();
            if (abs(id) != 6) continue;
            mtop = part.mass();
            break;
        }
        if (mtop <= 0.0) {
            throw std::string("top mass was incorrect");
        }
        pdf_scalePDF = sqrt(mtop * mtop + pdf_scalePDF * pdf_scalePDF);
    }
    
    //std::cout << "PDFSets.size() = " << PDFSets.size() << std::endl;
    for( unsigned int i = 0; i < PDFSets.size(); i++ ) {
        int InitNr = i+1;
        
        // calculate the PDF weights
        LHAPDF::usePDFMember(InitNr, 0);
        double	xpdf1 = LHAPDF::xfx(
            InitNr,
            pdf_x1,//pdf_vars["pdf_x1"],
            pdf_scalePDF,//pdf_vars["pdf_scalePDF"],
            pdf_id1
        );
        double	xpdf2 = LHAPDF::xfx(
            InitNr,
            pdf_x2,//pdf_vars["pdf_x2"],
            pdf_scalePDF,//pdf_vars["pdf_scalePDF"],
            pdf_id2
        );
        double w0 = xpdf1 * xpdf2;
        int	nPDFSet = LHAPDF::numberPDF(InitNr);

        /*
        std::vector<float>& weights = branch_vars.vars_vfloat[std::string("pdf_weights_"+PDFnames[i])];
        

        for (int p = 1; p <= nPDFSet; p++)
        {
            LHAPDF::usePDFMember(InitNr, p);
            double xpdf1_new = LHAPDF::xfx(InitNr, branch_vars.vars_float["pdf_x1"], branch_vars.vars_float["pdf_scalePDF"], branch_vars.vars_int["pdf_id1"]);
            double xpdf2_new = LHAPDF::xfx(InitNr, branch_vars.vars_float["pdf_x2"], branch_vars.vars_float["pdf_scalePDF"], branch_vars.vars_int["pdf_id2"]);
            double pweight = xpdf1_new * xpdf2_new / w0;
            weights[p-1] = (float)(pweight);
        }
        
        // save weights
        branch_vars.vars_float[std::string("pdf_n_"+PDFnames[i])] = nPDFSet;
        branch_vars.vars_float[std::string("pdf_w0_"+PDFnames[i])] = w0;
        */

        const std::string weight_name("pdf_weights_"+PDFnames[i]);
        std::vector<float>& weights = pdf_weights[weight_name];
        //initialize to 0
        for (auto& e : weights) {
            e = 0.0;
        }

        for (int p = 1; p <= nPDFSet; p++)
        {
            LHAPDF::usePDFMember(InitNr, p);
            double xpdf1_new = LHAPDF::xfx(
                InitNr,
                pdf_x1,//pdf_vars["pdf_x1"],
                pdf_scalePDF,//pdf_vars["pdf_scalePDF"],
                pdf_id1
            );
            double xpdf2_new = LHAPDF::xfx(
                InitNr,
                pdf_x2,//pdf_vars["pdf_x2"],
                pdf_scalePDF,//pdf_vars["pdf_scalePDF"],
                pdf_id2
            );
            double pweight = xpdf1_new * xpdf2_new / w0;
            weights[p-1] = (float)(pweight);
        }
        pdf_vars[std::string("pdf_n"+PDFnames[i])] = nPDFSet;
        iEvent.put(std::auto_ptr<int>(new int(nPDFSet)), std::string("n"+PDFnames[i]));
        pdf_vars[std::string("pdf_w0"+PDFnames[i])] = w0;
        iEvent.put(std::auto_ptr<float>(new float(w0)), std::string("w0"+PDFnames[i]));
        const char* weight_vec_name = std::string("weights" +PDFnames[i]).c_str();
        iEvent.put(
            std::auto_ptr<std::vector<float>>(new std::vector<float>(weights)),
            "weights" + PDFnames[i]
        );
    }

    iEvent.put(std::auto_ptr<float>(new float(pdf_scalePDF)), "scalePDF");
    iEvent.put(std::auto_ptr<float>(new float(pdf_x1)), "x1");
    iEvent.put(std::auto_ptr<float>(new float(pdf_x2)), "x2");
    iEvent.put(std::auto_ptr<int>(new int(pdf_id1)), "id1");
    iEvent.put(std::auto_ptr<int>(new int(pdf_id2)), "id2");
}

// ------------ method called once each job just before starting event loop  ------------
void 
PDFWeightProducer::beginJob()
{
}

// ------------ method called once each job just after ending the event loop  ------------
void 
PDFWeightProducer::endJob() {
}

// ------------ method called when starting to processes a run  ------------
void 
PDFWeightProducer::beginRun(edm::Run&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a run  ------------
void 
PDFWeightProducer::endRun(edm::Run&, edm::EventSetup const&)
{
}

// ------------ method called when starting to processes a luminosity block  ------------
void 
PDFWeightProducer::beginLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a luminosity block  ------------
void 
PDFWeightProducer::endLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&)
{
}

// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void
PDFWeightProducer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(PDFWeightProducer);
