//#include <TROOT.h>

void allplots(const char* fName = "TMVA.root") {
	gROOT->ProcessLine(Form(".x correlations.C(\"%s\")", fName));
	gROOT->ProcessLine(Form(".x mvas.C(\"%s\",3)", fName));
	gROOT->ProcessLine(Form(".x mvaeffs.C+(\"%s\")", fName ));
	gROOT->ProcessLine(Form(".x efficiencies.C(\"%s\")", fName));
	std::cout << "All done!" << std::endl;
	return;
}
