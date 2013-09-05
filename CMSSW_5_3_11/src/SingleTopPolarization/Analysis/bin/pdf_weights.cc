#include "pdf_weights.h"
#include <SimDataFormats/GeneratorProducts/interface/GenEventInfoProduct.h>
#include "DataFormats/HepMCCandidate/interface/GenParticle.h"

void PDFWeights::initialize_branches() {
    branch_vars.vars_float["pdf_scalePDF"] = BranchVars::def_val;
    branch_vars.vars_float["pdf_x1"] = BranchVars::def_val;
    branch_vars.vars_float["pdf_x2"] = BranchVars::def_val;
    branch_vars.vars_int["pdf_id1"] = BranchVars::def_val;
    branch_vars.vars_int["pdf_id2"] = BranchVars::def_val;
}


PDFWeights::PDFWeights(const edm::ParameterSet& pars, BranchVars& _branch_vars) :
CutsBase(_branch_vars)
{
    PDFSets = pars.getParameter<std::vector<std::string>>("PDFSets");
    enabled = pars.getParameter<bool>("enabled");
    generatorName = pars.getParameter<std::string>("generatorName");
    ////LHAPDF cannot manage with more PDF sets
    //if(PDFSets.size()>2)
    //    throw("Must specify at most 2 PDF sets");
    
    std::map<string,int> map_name;

    for( unsigned int i = 0; i < PDFSets.size(); i++ ) {
        
        // make names of PDF sets to be saved
        string name = PDFSets[i];
        size_t pos = name.find_first_not_of("ZXCVBNMASDFGHJKLQWERTYUIOPabcdefghijklmnopqrstuvwxyz1234567890");
        if (pos!=std::string::npos) name = name.substr(0,pos);
        if( map_name.count(name) == 0 ) {
            map_name[name]=0;
            PDFnames.push_back(name);
        }
        else {
            map_name[name]++;
            ostringstream ostr;
            ostr << name << "xxx" << map_name[name];
            PDFnames.push_back(ostr.str());
        }
        std::cout << "Initializing PDF set " << i << std::endl;
        LHAPDF::initPDFSet(i+1, PDFSets[i]);
        branch_vars.vars_float[string("pdf_w0_"+PDFnames[i])] = BranchVars::def_val;
        branch_vars.vars_float[string("pdf_n_"+PDFnames[i])] = BranchVars::def_val;
        std::cout << "Getting the number of PDF points in set" << std::endl;
        int nPDFSet = LHAPDF::numberPDF(i+1);
        branch_vars.vars_vfloat[std::string("pdf_weights_"+PDFnames[i])] = std::vector<float>(nPDFSet);
    }
    initialize_branches();
    
    scalePDFSrc = pars.getParameter<edm::InputTag>("scalePDFSrc");
    x1Src = pars.getParameter<edm::InputTag>("x1Src");
    x2Src = pars.getParameter<edm::InputTag>("x2Src");
    id1Src = pars.getParameter<edm::InputTag>("id1Src");
    id2Src = pars.getParameter<edm::InputTag>("id2Src");
    
}

bool PDFWeights::process(const edm::EventBase& event) {
    pre_process();

	edm::Handle<GenEventInfoProduct> genprod;
    edm::InputTag genWeightSrc1("generator");
    edm::InputTag genParticlesSrc("genParticles");
	event.getByLabel(genWeightSrc1, genprod);

	branch_vars.vars_float["pdf_scalePDF"] = genprod->pdf()->scalePDF;
	branch_vars.vars_float["pdf_x1"] = genprod->pdf()->x.first;
	branch_vars.vars_float["pdf_x2"] = genprod->pdf()->x.second;
	branch_vars.vars_int["pdf_id1"] = genprod->pdf()->id.first;
	branch_vars.vars_int["pdf_id2"] = genprod->pdf()->id.second;
    
    // Ad-hoc fix for POWHEG
    if (generatorName.compare("powheg")==0) {
        edm::Handle<reco::GenParticleCollection> genParticles;
        if (!event.getByLabel(genParticlesSrc, genParticles)) {
            //edm::LogError("PDFWeightProducer") << ">>> genParticles  not found: " << genParticlesSrc.encode() << " !!!";
            return false;
        }
        unsigned int gensize = genParticles->size();
        double mtop = 0.;
        for(unsigned int i = 0; i<gensize; ++i) {
            const reco::GenParticle& part = (*genParticles)[i];
            int status = part.status();
            if (status!=3) continue;
            int id = part.pdgId();
            if (abs(id) != 6) continue;
            mtop = part.mass();
            //cout << "found top with mass " << mtop << endl;
            break;
        }
        branch_vars.vars_float["pdf_scalePDF"] = sqrt(mtop*mtop+branch_vars.vars_float["pdf_scalePDF"]*branch_vars.vars_float["pdf_scalePDF"]);
    }



    for( unsigned int i = 0; i < PDFSets.size(); i++ ) {
        int InitNr = i+1;
        
        // calculate the PDF weights
        LHAPDF::usePDFMember(InitNr, 0);
        double	xpdf1 = LHAPDF::xfx(
            InitNr,
            branch_vars.vars_float["pdf_x1"],
            branch_vars.vars_float["pdf_scalePDF"],
            branch_vars.vars_int["pdf_id1"]
        );
        double	xpdf2 = LHAPDF::xfx(
            InitNr, branch_vars.vars_float["pdf_x2"],
            branch_vars.vars_float["pdf_scalePDF"],
            branch_vars.vars_int["pdf_id2"]
        );
        double	w0		= xpdf1 * xpdf2;
        int		nPDFSet = LHAPDF::numberPDF(InitNr);
        std::vector<float>& weights = branch_vars.vars_vfloat[std::string("pdf_weights_"+PDFnames[i])]; 
        for (auto& e : weights)
            e = 0.0;

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
    }
    post_process();
    return true;
}

