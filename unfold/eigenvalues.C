#include <TH1F.h>
#include <TCanvas.h>
#include <TVector.h>
#include <TMatrix.h>
#include <TFile.h>

#include "binnings.h"
#include "utils.hpp"

void eigenvalues()
{
	// dummy canvas
	TCanvas *c1 = new TCanvas("canvas","canvas");

	// Read in covariance matrix
	TFile *f = new TFile("cov.root");
	TH2F *hcov = (TH2F*)f->Get("covariance");
	
	// Output file
	TFile *fo = new TFile("histos/eigenhistos.root","RECREATE");

	// FIXME Fixed number for pseudoexperiments
	Int_t nbkgs = 3;

	vector<TString> names;
	vector<TH1F*> histos;
	vector<Float_t> scales;
	vector<Float_t> uncs;
	read_fitres(names,scales,uncs);
	
	typedef TMatrixT<double>	TMatrixD;
	TMatrixD covmatrix(nbkgs,nbkgs);
	
	TFile *f2 = new TFile("histos/pseudo_data.root");

	Float_t sum_nonrot = 0;
	for(int i = 0; i < nbkgs ; i++) {
		TString name = names.at(i+1);
		TH1F *tmp = (TH1F*)f2->Get(var_y+"__"+name);
		sum_nonrot += tmp->Integral();
		cout << name << " " << tmp->Integral() << endl;
		histos.push_back((TH1F*)tmp);
	}
	cout << "Sum nonrotated: " << sum_nonrot << endl;
	
	TH1F *bkg_nominal = (TH1F*)histos[0]->Clone("bkg_nominal");
	bkg_nominal->Reset();
	bkg_nominal->SetTitle("bkg_nominal");
	for(int i = 0; i < nbkgs ; i++) {
		TH1F *histo = (TH1F*)histos[i];
		bkg_nominal->Add(histo);
	}

	
	// Skip first entry for beta_signal
	for(int i = 0; i < nbkgs ; i++) {
		//TString name = hcov->GetXaxis()->GetBinLabel(i+2);
		//cout << name << endl;
		//cout << names.at(i+1) << endl;
		for(int j = 0; j < nbkgs; j++) {
			covmatrix[i][j] = hcov->GetBinContent(i+2,j+2);
                        covmatrix[i][j] *= scales.at(i+1)*scales.at(j+1);
		}
	}

	TVectorD eigenvalues(nbkgs);
	TMatrixD eigenvectors = covmatrix.EigenVectors(eigenvalues);
	
	cout << "Eigenvalues: " << endl;
	for(int i = 0; i < nbkgs; i++)
		cout << eigenvalues[i] << endl;

	//eigenvalues.Print();
	
	cout << "Eigenvectors: " << endl;
	for(int i = 0; i < nbkgs; i++)
	{
		cout << "( ";
		for(int j = 0; j < nbkgs; j++)
		{
			cout << eigenvectors[j][i] << ", ";
		}
		cout << " )" << endl;
	}

	//eigenvectors.Print();

	// Unit vector
	TVectorD unitvec(nbkgs);
	for(int i = 0; i < nbkgs; i++)
		unitvec[i] = 1;
	
	// Inverted eigenvectors
	TMatrixD inv_eigenvectors(eigenvectors);
	inv_eigenvectors.Invert();

	unitvec *= inv_eigenvectors;
	TVectorD scale_vector(unitvec);

	//scale_vector.Print();

	// Apply scale factors to eigenvectors
	for(int i = 0; i < nbkgs; i++)
	{
		for(int j = 0; j < nbkgs; j++)
		{
			eigenvectors[i][j] *= scale_vector[j];
		}
	}

	// New eigenvectors
	//eigenvectors.Print();

	vector<Float_t> bgrelerrors;
	vector<Float_t> bgabserrors;

	TH1F *bkg_rotated = (TH1F*)histos[0]->Clone("bkg_rotated");
	bkg_rotated->Reset();
	bkg_rotated->SetTitle("bkg_rotated");

	Float_t sum_rot = 0;
	// Rotate backgrounds
	for(int i = 0; i < nbkgs; i++)
	{
		TH1F *histo = (TH1F*)histos[i]->Clone();
		histo->Reset();

		// Add up eigenhistos
		for(int j = 0; j < nbkgs; j++)
		{
			// First index: row, element of vector
			// Second index: column, index of vector
			histo->Add(histos[j], eigenvectors(j,i));
		}
		sum_rot += histo->Integral();
		bkg_rotated->Add(histo);
		cout << "eigenhisto" << i << " " << histo->Integral() << endl;
		bgrelerrors.push_back(sqrt(eigenvalues[i]) / histo->Integral());
		bgabserrors.push_back(sqrt(eigenvalues[i]));
	}
	cout << "Sum rotated: " << sum_rot << endl;

	cout << "Relative errors: " << endl;
	for(int i = 0; i < nbkgs; i++)
	{
		cout << bgrelerrors[i] << endl;
	}

	fo->cd();
	bkg_nominal->Write();
	bkg_rotated->Write();
	fo->Close();

	f->Close();



}

int main()
{
	eigenvalues();
}
