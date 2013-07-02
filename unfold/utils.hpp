#ifndef UTILS_HPP
#define UTILS_HPP
#include "TH2F.h"
#include "TMath.h"

#include <cstdlib>
#include <iostream>
#include <fstream>

using namespace std;

void read_fitres(vector<TString> &names, vector<Float_t> &scales, vector<Float_t> &uncs)
{
        TString name;
        Float_t scale, unc;
        
        ifstream ifs;
        ifs.open("results.txt");
        if(!ifs.good()) {
                cout << "Could not open fit results file!" << endl;
                exit(1);
        }
        while (ifs >> name >> scale >> unc) {
                names.push_back(name);
                scales.push_back(scale);
                uncs.push_back(unc);
        } 
        ifs.close();
        
}

Float_t error_naive(Float_t plus, Float_t minus)
{
	return 2/TMath::Power(plus+minus,2)*TMath::Sqrt(minus*plus*plus+plus*minus*minus);
}

Float_t error_unfold(TH2F* errmat, TH1F* unf)
{
	Int_t bin_zero =  unf->FindBin(0.0);
	Int_t bin_last =  unf->GetXaxis()->GetNbins();

	Float_t integral_plus = unf->Integral(bin_zero,bin_last);
	Float_t integral_minus = unf->Integral(1,bin_zero-1);
	Float_t integral = unf->Integral(1,bin_last);

	// Derivatives
	Float_t dadn_plus = 2*integral_minus/TMath::Power(integral,2);
	Float_t dadn_minus = -2*integral_plus/TMath::Power(integral,2);

	TH1F vec("vec","vec",bin_last, 0, bin_last);
	TH2F corr("corr","corr",bin_last, 0, bin_last, bin_last, 0, bin_last);
	TH1F vecT("vecT","vecT",bin_last, 0, bin_last);

	for(Int_t i = 1; i <= bin_last; i++)
	{
		if(i<bin_zero)
			vec.SetBinContent(i-1,dadn_minus);
		if(i>=bin_zero)
			vec.SetBinContent(i-1,dadn_plus);

		vecT.SetBinContent(i-1,0);

		for(Int_t j = 1; j <= bin_last; j++)
		{
			corr.SetBinContent(i-1,j-1,errmat->GetBinContent(i,j));
		}
	}

	//

	for(Int_t i = 0; i < bin_last; i++)
		for(Int_t j = 0; j < bin_last; j++)
			vecT.SetBinContent(i, vecT.GetBinContent(i) + corr.GetBinContent(i,j)*vec.GetBinContent(j));

	Float_t error = 0;

	for(Int_t i = 0; i < bin_last; i++)
		error += vecT.GetBinContent(i)*vec.GetBinContent(i);
	
	error = TMath::Sqrt(error);

	return error;
}

Float_t asymmetry(TH1F *hist)
{
	Int_t bin_zero =  hist->FindBin(0.0);
	Int_t bin_last =  hist->GetXaxis()->GetNbins();
	//cout << "zero bin: " << bin_zero << endl;
	//cout << "last bin: " << bin_last << endl;

	Float_t integral_plus = hist->Integral(bin_zero,bin_last);
	Float_t integral_minus = hist->Integral(1,bin_zero-1);
	Float_t integral = hist->Integral(1,bin_last);
	Float_t asym = (integral_plus-integral_minus)/integral;
	//cout << "integral+:" << integral_plus << endl;
	//cout << "integral-:" << integral_minus << endl;
	//cout << "integral:" << integral << endl;
	//cout << "asymmetry: " << asym << " +- " << error_naive(integral_plus , integral_minus) << endl;
	return asym;
}
#endif
