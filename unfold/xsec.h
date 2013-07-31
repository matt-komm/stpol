#ifndef XSEC_H
#define XSEC_H

#include <map>
#include <TString.h>

using namespace std;

// Link:
// https://github.com/HEP-KBFI/stpol/blob/master/plots/common/cross_sections.py

Float_t get_xsec(TString process)
{
	if(process.Contains("TToBMuNu")) process = "T_t_ToLeptons"; // FIXME
	
	if(process.Contains("TToLeptons_t-channel")) process = "T_t_ToLeptons";
	if(process.Contains("Tbar_t_mass")) process = "Tbar_t_ToLeptons";
	if(process.Contains("Tbar_t_scale")) process = "Tbar_t_ToLeptons";
        
	if(process.Contains("TTJets_mass")) process = "TTJets";
	if(process.Contains("TTJets_scale")) process = "TTJets";
	if(process.Contains("TTJets_matching")) process = "TTJets";

	
	map <TString, Float_t>xsec;
	xsec["T_t"] = 56.4;
	xsec["Tbar_t"] = 30.7;
	xsec["T_t_ToLeptons"] = 0.326*56.4;
	xsec["Tbar_t_ToLeptons"] = 0.326*30.7;

	xsec["T_s"] = 3.79;
	xsec["Tbar_s"] = 1.76;
	xsec["T_tW"] = 11.1;
	xsec["Tbar_tW"] = 11.1;

	xsec["TTJets"] = 234.0;
	xsec["TTJets_SemiLept"] = (0.676*0.326*2) * 234.0;
	xsec["TTJets_FullLept"] = (0.326*0.326) * 234.0;

	// exclusive sample branching ratios, same as PREP
	Float_t WJets_lo_nnlo_scale_factor = 37509.0/30400.0;
	xsec["W1Jets_exclusive"] = 5400.0 * WJets_lo_nnlo_scale_factor;
	xsec["W2Jets_exclusive"] = 1750.0 * WJets_lo_nnlo_scale_factor;
	xsec["W3Jets_exclusive"] = 519.0 * WJets_lo_nnlo_scale_factor;
	xsec["W4Jets_exclusive"] = 214.0 * WJets_lo_nnlo_scale_factor;
	
	// Diboson
	xsec["DYJets"] = 3503.71;
	xsec["WW"] = 54.838;
	xsec["WZ"] = 33.21;
	xsec["ZZ"] = 8.059;

	//xsec["QCDMu"] = 134680;
	//xsec["QCDShape"] = 0.18408;
	xsec["QCDShape"] = 0.912881608;
	
	// DATA
	xsec["SingleMuAB"] = 1;
	xsec["SingleMuC"] = 1;
	xsec["SingleMuD"] = 1;

	return xsec[process];
}

#endif
