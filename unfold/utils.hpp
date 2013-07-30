#ifndef UTILS_HPP
#define UTILS_HPP
#include "TH2F.h"
#include "TMath.h"

#include <cstdlib>
#include <iostream>
#include <fstream>

using namespace std;

void read_fitres(TString fresult, vector<TString> &names, vector<Float_t> &scales, vector<Float_t> &uncs)
{
        TString name;
        Float_t scale, unc;
        
	cout << "reading fit results: " << fresult << endl;

        ifstream ifs;
        ifs.open("fitresults/"+fresult+".txt");
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

void fill_nooverflow_1d(TH1* h, double val, double weight)
{
	if(val > h->GetXaxis()->GetXmax()) val = h->GetXaxis()->GetXmax()-0.00001;
	if(val < h->GetXaxis()->GetXmin()) val = h->GetXaxis()->GetXmin()+0.00001; 
	h->Fill(val, weight);
}

void fill_nooverflow_2d(TH2* h, double valx, double valy, double weight)
{
	const double xmax = h->GetXaxis()->GetXmax();
	const double xmin = h->GetXaxis()->GetXmin();
	const double ymax = h->GetYaxis()->GetXmax();
	const double ymin = h->GetYaxis()->GetXmin();

	if(valx > xmax) valx =xmax-0.00001;
	if(valx < xmin) valx = xmin+0.00001; 

	if(valy > ymax) valy = ymax-0.00001;
	if(valy < ymin) valy = ymin+0.00001; 
  
	h->Fill(valx, valy, weight);
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

Double_t asymmetry(TH1F *hist)
{	
	// Underflow and overflow should not be filled
	//cout << hist->GetBinContent(0) << endl;
	//cout << hist->GetBinContent(hist->GetNbinsX()+1) << endl;

	Int_t bin_zero =  hist->FindBin(0.0);
	Int_t bin_last =  hist->GetXaxis()->GetNbins();
	//cout << "zero bin: " << bin_zero << endl;
	//cout << "last bin: " << bin_last << endl;

	Int_t integral_plus = hist->Integral(bin_zero,bin_last);
	Int_t integral_minus = hist->Integral(1,bin_zero-1);
	Int_t integral = hist->Integral(1,bin_last);
	Double_t asym = (integral_plus-integral_minus)/(Double_t)integral;
	//cout << "integral+:" << integral_plus << endl;
	//cout << "integral-:" << integral_minus << endl;
	//cout << "integral:" << integral << endl;
	//cout << "asymmetry: " << asym << " +- " << error_naive(integral_plus , integral_minus) << endl;
	return asym;
}
#endif
