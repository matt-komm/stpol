#include "pdf_weights.h"

void PDFWeights::initialize_branches() {
    branch_vars.vars_float["scalePDF"] = BranchVars::def_val;
    branch_vars.vars_float["x1"] = BranchVars::def_val;
    branch_vars.vars_float["x2"] = BranchVars::def_val;
    branch_vars.vars_float["id1"] = BranchVars::def_val;
    branch_vars.vars_float["id2"] = BranchVars::def_val;
}


PDFWeights::PDFWeights(const edm::ParameterSet& pars, BranchVars& _branch_vars) :
CutsBase(_branch_vars)
{
    PDFSets = pars.getParameter<std::vector<std::string>>("PDFSets");
    enabled = pars.getParameter<bool>("enabled");
    
    //LHAPDF cannot manage with more PDF sets
    if(PDFSets.size()>2)
        throw("Must specify at most 2 PDF sets");
    
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

        LHAPDF::initPDFSet(i+1, PDFSets[i]);
        branch_vars.vars_float[string("w0"+PDFnames[i])] = BranchVars::def_val;
        branch_vars.vars_float[string("n"+PDFnames[i])] = BranchVars::def_val;
        branch_vars.vars_vfloat[string("weights"+PDFnames[i])] = std::vector<float>();
        branch_vars.vars_vfloat[string("weights"+PDFnames[i])].clear();
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
    
    branch_vars.vars_float["scalePDF"] = get_collection<float>(event, scalePDFSrc, BranchVars::def_val);
    branch_vars.vars_float["x1"] = get_collection<float>(event, x1Src, BranchVars::def_val);
    branch_vars.vars_float["x2"] = get_collection<float>(event, x2Src, BranchVars::def_val);
    branch_vars.vars_int["id1"] = get_collection<int>(event, id1Src, BranchVars::def_val);
    branch_vars.vars_int["id2"] = get_collection<int>(event, id2Src, BranchVars::def_val);
    
    
    for( unsigned int i = 0; i < PDFSets.size(); i++ ) {
        
        int InitNr = i+1;
        
        // calculate the PDF weights
        std::auto_ptr < std::vector<double> > weights(new std::vector<double>());
        LHAPDF::usePDFMember(InitNr, 0);
        double	xpdf1	= LHAPDF::xfx(InitNr, branch_vars.vars_float["x1"], branch_vars.vars_float["scalePDF"], branch_vars.vars_int["id1"]);
        double	xpdf2	= LHAPDF::xfx(InitNr, branch_vars.vars_float["x2"], branch_vars.vars_float["scalePDF"], branch_vars.vars_int["id2"]);
        double	w0		= xpdf1 * xpdf2;
        int		nPDFSet = LHAPDF::numberPDF(InitNr);
        for (int p = 1; p <= nPDFSet; p++)
        {
            LHAPDF::usePDFMember(InitNr, p);
            double xpdf1_new	= LHAPDF::xfx(InitNr, branch_vars.vars_float["x1"], branch_vars.vars_float["scalePDF"], branch_vars.vars_int["id1"]);
            double xpdf2_new	= LHAPDF::xfx(InitNr, branch_vars.vars_float["x2"], branch_vars.vars_float["scalePDF"], branch_vars.vars_int["id2"]);
            double pweight		= xpdf1_new * xpdf2_new / w0;
            weights->push_back(pweight);
        }
        
        // save weights
        for (auto sf : (*weights)) {
            branch_vars.vars_vfloat[std::string("weights"+PDFnames[i])].push_back(float(sf));
        }
        branch_vars.vars_float[std::string("n"+PDFnames[i])] = nPDFSet;
        branch_vars.vars_float[std::string("w0"+PDFnames[i])] = w0;
    }
    post_process();
    return true;
}
