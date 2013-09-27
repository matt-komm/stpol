#include "cuts_base.h"

#ifndef PDF_WEIGHTS_H
#define PDF_WEIGHTS_H

using namespace std;

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
}

class PDFWeights : public CutsBase {
public:
    bool enabled;
    edm::InputTag scalePDFSrc;
    edm::InputTag x1Src;
    edm::InputTag x2Src;
    edm::InputTag id1Src;
    edm::InputTag id2Src;
    
    float scalePDF;
    float x1,x2;
    int id1,id2;
    
    std::vector<std::string> PDFSets;
    std::vector<std::string> PDFnames;
    std::string generatorName;

    void initialize_branches();
    PDFWeights(const edm::ParameterSet& pars, BranchVars& _branch_vars);
    bool process(const edm::EventBase& event);
};

#endif


