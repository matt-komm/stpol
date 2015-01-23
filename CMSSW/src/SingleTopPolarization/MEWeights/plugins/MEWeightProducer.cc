
#include "FWCore/Framework/interface/ESHandle.h"
#include "FWCore/Utilities/interface/InputTag.h"
#include "DataFormats/Common/interface/Handle.h"
#include "FWCore/Framework/interface/EDProducer.h"

#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"

#include "FWCore/MessageLogger/interface/MessageLogger.h"

#include "TMath.h"

#include "SimDataFormats/GeneratorProducts/interface/GenEventInfoProduct.h"
#include "SimDataFormats/GeneratorProducts/interface/LHEEventProduct.h"

#include "LHAPDF/LHAPDF.h"

#include <iostream>
#include <string>

class MEWeightProducer: public edm::EDProducer
{
    private:
    
        std::string _pdfsetFile;
    public:
        MEWeightProducer(const edm::ParameterSet& config):
            _pdfsetFile("cteq6m.LHpdf")
        {
            produces<double>("meWeightUp");
            produces<double>("meWeightDown");
            produces<double>("pdfNominal");
            produces<double>("pdfUp");
            produces<double>("pdfDown");
            produces<double>("alphasNominal");
            produces<double>("alphasUp");
            produces<double>("alphasDown");

            if (config.exists("pdfsetFile"))
            {
                _pdfsetFile=config.getParameter<std::string>("pdfsetFile");
                edm::LogWarning("MEWeightProducer")<<"default pdfset changed to '"<<_pdfsetFile.c_str()<<"'";
            }

            LHAPDF::initPDFSet(_pdfsetFile);
            LHAPDF::usePDFMember(1,0);
        }
        
        static void fillDescriptions(edm::ConfigurationDescriptions&)
        {
        }
        
        
        
        void produce(edm::Event& iEvent, const edm::EventSetup& iSetup)
        {
            using namespace edm;
            using namespace std;

            edm::Handle<GenEventInfoProduct> genInfo;
            iEvent.getByLabel("generator", genInfo); 
            const GenEventInfoProduct& genEventInfo = *(genInfo.product());
            const gen::PdfInfo* pdf = genEventInfo.pdf();

            edm::Handle<LHEEventProduct> lheevent;
            iEvent.getByLabel("source", lheevent);
            
            double factorization_scale = lheevent->hepeup().SCALUP;

            double Q_scale = genEventInfo.qScale();

            int id1=pdf->id.first;
            int id2=pdf->id.second;
            double x1=pdf->x.first;
            double x2=pdf->x.second;

            double alpha = LHAPDF::alphasPDF(Q_scale);
            double alpha_down = LHAPDF::alphasPDF(Q_scale*0.5);
            double alpha_up = LHAPDF::alphasPDF(Q_scale*2.);

            double pdf1 = LHAPDF::xfx(1,  x1, factorization_scale,  id1);
            double pdf2 = LHAPDF::xfx(1,  x2, factorization_scale,  id2);
            double pdf1_up = LHAPDF::xfx(1,  x1, factorization_scale*2.,  id1);
            double pdf2_up = LHAPDF::xfx(1,  x2, factorization_scale*2.,  id2);
            double pdf1_down = LHAPDF::xfx(1,  x1, factorization_scale*.5,  id1);
            double pdf2_down = LHAPDF::xfx(1,  x2, factorization_scale*.5,  id2);

            double me_weight_up = pdf1_up/pdf1*pdf2_up/pdf2;
            double me_weight_down = pdf1_down/pdf1*pdf2_down/pdf2; 
            
            /*
            cout<<"id: "<<id1<<","<<id2<<endl;
            cout<<"x: "<<x1<<","<<x2<<endl;
            cout<<"scales: "<<Q_scale<<", "<<factorization_scale<<endl;
            cout<<"me weights: "<<me_weight_up<<", "<<me_weight_down<<endl;
            cout<<"pdf1: "<<pdf1<<","<<pdf1_up<<","<<pdf1_down<<endl;
            cout<<"pdf2: "<<pdf2<<","<<pdf2_up<<","<<pdf2_down<<endl;
            cout<<"alpha_s: "<<alpha<<","<<alpha_up<<","<<alpha_down<<endl;
            */

            iEvent.put(auto_ptr<double>(new double(me_weight_up)),"meWeightUp");
            iEvent.put(auto_ptr<double>(new double(me_weight_down)),"meWeightDown");
            
            
            iEvent.put(auto_ptr<double>(new double(pdf1*pdf2)),"pdfNominal");
            iEvent.put(auto_ptr<double>(new double(pdf1_up*pdf2_up)),"pdfUp");
            iEvent.put(auto_ptr<double>(new double(pdf1_down*pdf2_down)),"pdfDown");
            iEvent.put(auto_ptr<double>(new double(alpha)),"alphasNominal");
            iEvent.put(auto_ptr<double>(new double(alpha_up)),"alphasUp");
            iEvent.put(auto_ptr<double>(new double(alpha_down)),"alphasDown");

        }
};

DEFINE_FWK_MODULE(MEWeightProducer);
