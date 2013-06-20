#include "TCanvas.h"
#include "TH1F.h"
#include "TH2F.h"
#include "TFile.h"
#include "TRandom3.h"
#include "TUnfold.h"
#include "TUnfoldSys.h"
#include <TVector.h>
#include <TMatrix.h>
#include <TMath.h>
#include "TMinuit.h"
#include <iostream>

#include "utils.hpp"
#include "binnings.h"

using namespace std;

const double scaleBias = 1.0;

// Number of pseudo experiments
#define NPSEUDO 50000

TUnfoldSys* myUnfold1d_TUnfoldGlobalPointerForTMinuit;
TH1F* myUnfold1d_hdataGlobalPointerForTMinuit;

static void myUnfold1d_globalFunctionForMinuit(int &npar, double *gin, double &f, double *par, int iflag)
{
  const double logtau = par[0];
  const double scaleBias = par[1];
  myUnfold1d_TUnfoldGlobalPointerForTMinuit->DoUnfold(pow(10, logtau), myUnfold1d_hdataGlobalPointerForTMinuit, scaleBias);
  
  f = myUnfold1d_TUnfoldGlobalPointerForTMinuit->GetRhoAvg();
}



void minimizeRhoAverage(TUnfoldSys *unfold, TH1F *hdata, int nsteps, double log10min, double log10max)
{
  myUnfold1d_TUnfoldGlobalPointerForTMinuit = unfold;
  myUnfold1d_hdataGlobalPointerForTMinuit = hdata;
  
  // Instantiate Minuit for 2 parameters
  TMinuit minuit(2);
  minuit.SetFCN(myUnfold1d_globalFunctionForMinuit);
  minuit.SetPrintLevel(-1); // -1 no output, 1 output
 
  minuit.DefineParameter(0, "logtau", (log10min+log10max)/2, 1, log10min, log10max);
  minuit.DefineParameter(1, "scaleBias", scaleBias, 0, scaleBias, scaleBias);
  minuit.FixParameter(1);
  
  minuit.SetMaxIterations(100);
  minuit.Migrad();
  
  double bestlogtau = -1000;
  double bestlogtau_err = -1000; // error is meaningless because we don't have a likelihood, but method expects it
  minuit.GetParameter(0, bestlogtau, bestlogtau_err);
  unfold->DoUnfold(pow(10, bestlogtau), hdata, scaleBias); 
  
}

void unfold(TH1F *hrec, TH2F *hgenrec, TH1F *heff, TH1F *hgen, TFile *f)
{
	// only show errors
	// gErrorIgnoreLevel = kError;

	cout << "using TUnfold " << TUnfold_VERSION << endl;
	
	// dummy canvas
	TCanvas *c1 = new TCanvas("canvas","canvas");
	c1->Clear();
	
	TRandom3 random(0);

	TH1::SetDefaultSumw2(true);

	TFile *fo = new TFile("histos/unfolded.root","RECREATE");
	
	bool subtractData = true;
	//bool subtractData = false;

	// Background subtraction
	vector<TString> names;
	vector<Float_t> scales;
	vector<Float_t> uncs;
	vector<Float_t> preds;
	vector<TH1F*> bkghistos;
	TH1F *hsignal;

	vector<TH1F*> eigenhistos;
	vector<Float_t> eigenerrors;

	Int_t nbkgs = 0;
	Float_t sum_nonrot = 0;

	if(subtractData) {
		
		// Order of fit results must be the same as in covariance matrix:
		// first entry beta_signal, rest alphabetic
		cout << "reading fit results: " << endl;
		read_fitres(names,scales,uncs);
		
		nbkgs = names.size()-1;

		hsignal = (TH1F*)f->Get(var_y+"__tchan");
		// FIXME
//		hsignal->Scale(scales[0]);
		// Read in background histograms
		for(int i = 0; i < nbkgs ; i++) {
			TString name = names.at(i+1);
			TH1F *histo = (TH1F*)f->Get(var_y+"__"+name);
			
			// Scale histos
			// FIXME
//			histo->Scale(scales[i+1]);
			preds.push_back(histo->Integral());
			
			sum_nonrot += histo->Integral();
			bkghistos.push_back((TH1F*)histo);

		}
		cout << "background events: " << sum_nonrot << endl;
		
		// Decorrelate background templates
		// Read in covariance matrix
		TFile *fcov = new TFile("cov.root");
		TH2D *hcov = (TH2D*)fcov->Get("covariance");
		
		TMatrixD covmatrix(nbkgs,nbkgs);

		// Fill cov matrix, skip first entry with beta_signal
		for(int i = 0; i < nbkgs ; i++) {
			//TString name = hcov->GetXaxis()->GetBinLabel(i+2);
			//cout << name << endl;
			//cout << names.at(i+1) << endl;
			for(int j = 0; j < nbkgs; j++) {
				covmatrix[i][j] = hcov->GetBinContent(i+2,j+2);
				covmatrix[i][j] *= preds[i]*preds[j];
			}
		}

		fcov->Close();

		TVectorD eigenvalues(nbkgs);
		TMatrixD eigenvectors = covmatrix.EigenVectors(eigenvalues);
		
		// Unit vector
		TVectorD unitvec(nbkgs);
		for(int i = 0; i < nbkgs; i++) unitvec[i] = 1;
		
		// Inverted eigenvectors
		TMatrixD inv_eigenvectors(eigenvectors);
		inv_eigenvectors.Invert();

		unitvec *= inv_eigenvectors;
		// Scale vector to keep norm
		TVectorD scale_vector(unitvec);
		
		// Apply scale factors to eigenvectors
		for(int i = 0; i < nbkgs; i++)
		{
			for(int j = 0; j < nbkgs; j++)
			{
				eigenvectors[i][j] *= scale_vector[j];
			}
		}
		

		Float_t sum_rot = 0;
		// Rotate backgrounds
		for(int i = 0; i < nbkgs; i++)
		{
			TH1F *eigenhisto = (TH1F*)bkghistos[i]->Clone();
			eigenhisto->Reset();

			// Add up eigenhistos
			for(int j = 0; j < nbkgs; j++)
			{
				// First index: row, element of vector
				// Second index: column, index of vector
				eigenhisto->Add(bkghistos[j], eigenvectors(j,i));
			}
			eigenhistos.push_back((TH1F*)eigenhisto);
			sum_rot += eigenhisto->Integral();
			//cout << "eigenhisto" << i << " " << eigenhisto->Integral() << endl;
			eigenerrors.push_back(sqrt(eigenvalues[i]) / eigenhisto->Integral());
		}
		//cout << "background events rotated: " << sum_rot << endl;
	}

	// FIXME Current samples are normalized to one
	//Float_t expected = 2700; // Events expected in data: approx at 20/fb
	Float_t expected = 4617; // Events expected in data: approx at 20/fb
	if(!subtractData) hrec->Scale(expected/hrec->Integral());

	// Number of expected events
	if(subtractData)
		expected = (hrec->Integral() - sum_nonrot);
	else
		expected = hrec->Integral();

	// Scale generated and migration matrix to expected
	hgen->Scale(expected/hgen->Integral()); // for bias
	hgenrec->Scale(expected/hgenrec->Integral());
	
	TH1F *hgen_presel = (TH1F*)hgen->Clone("hgen_presel");

	// Fill overflow bins of mig. matrix with # nonselected events
	for(Int_t i = 1; i <= bin_x; i++) {
		Float_t bin_eff = heff->GetBinContent(i);
		hgen_presel->SetBinContent(i,hgen->GetBinContent(i)/bin_eff);
		Float_t nonsel = hgen_presel->GetBinContent(i)*(1-bin_eff);
		hgenrec->SetBinContent(i,0,nonsel);
	}
	
	// Calculate selection efficiency
	Float_t overflow = hgenrec->Integral(1,bin_x,0,0);
	Float_t sel_eff = hgenrec->Integral(1,bin_x,1,bin_y)/overflow;

	cout << "data events: " << hrec->Integral() << endl;
	cout << "expected signal events: " << expected << endl;
	cout << "matrix integral " << hgenrec->Integral() << endl;
	cout << "Unfolding: " + varname << endl;
		
	// Prepare unfolding
	//TUnfoldSys unfold(hgenrec,TUnfold::kHistMapOutputHoriz,TUnfold::kRegModeCurvature);
	TUnfoldSys unfold(hgenrec,TUnfold::kHistMapOutputHoriz,TUnfold::kRegModeNone);

	// set input distribution
	unfold.SetInput(hrec);
	
	// set bias dist
	// FIXME strange results since bias has peaks at zero
	unfold.SetBias(hgen);

	// subtract backgrounds
	if(subtractData) {
		for(int i = 0; i < nbkgs; i++)
		{
			// FIXME
			//unfold.SubtractBackground(eigenhistos[i],names[i+1],1.0, eigenerrors[i]);
			unfold.SubtractBackground(bkghistos[i],names[i+1],1.0, uncs[i]);
		}
	}


	// find minimal global correlation
	minimizeRhoAverage(&unfold, hrec, 1000, -6, 0);

	Float_t tau = unfold.GetTau();
	cout << "tau: " << tau << endl;

	Float_t corr;
	corr = unfold.DoUnfold(tau,hrec, scaleBias);

	cout << "global correlation: " << corr << endl;

	fo->cd();

	TH1F *hurec = new TH1F("unfolded","unfolded",bin_x,1,bin_x);
	unfold.GetOutput(hurec);

	cout << "selection eff: " << sel_eff << endl;
	cout << "reconstructed: " << expected << " unfolded: " << hurec->Integral() << endl;

	// rho, error matrix
	TH2D *hrhoij = new TH2D("correlation","correlation",bin_x,1,bin_x,bin_x,1,bin_x);
	unfold.GetRhoIJ(hrhoij);
	TH2D *hematrix = new TH2D("error","error",bin_x,1,bin_x,bin_x,1,bin_x);
	unfold.GetEmatrix(hematrix);
	// Add migration matrix stat. error
	//unfold.GetEmatrixSysUncorr(hematrix, 0, false); 


	// pseudo experiments
	TH1F *hPull[bin_x];
	TH1F *hBin[bin_x];
	TH1F hStatErr("staterr","staterr",1000,0.0,1.0);
	TH1F hasy("asymmetry","asymmetry",100,0.0,1.0);
	TH1F hasy_bias("asymmetry_bias","asymmetry_bias",100,-1.0,1.0);
	TH1F hasy_pull("asymmetry_pull","asymmetry_pull",100,-3.0,3.0);

	TString pull_name = "pull_";
	TString bin_name = "reldiff_";
	for(Int_t i=1; i <= bin_x; i++) {
		TString pname = pull_name;
		pname += i;
		TString bname = bin_name;
		bname += i;
		hPull[i-1] = new TH1F(pname,pname,60,-3.0,3.0);
		hBin[i-1] = new TH1F(bname,bname,100,-1.0,1.0);
	}
	
	// do PEs
	cout << "Dicing " << NPSEUDO << " pseudo events..." << endl;
	Float_t genasy = asymmetry(hgen_presel);
	TH1F *hpseudo = new TH1F("pseudo","pseudo", bin_y, list_y);
	for(Int_t p=1; p<=NPSEUDO; p++) {
		
		if(p%5000 == 0) cout << p << endl;
		
		hpseudo->Reset();
		if(subtractData) {
			for(int i = 0; i < nbkgs ; i++) {
				//TH1F *heigen = (TH1F*)eigenhistos[i];
				// FIXME
				TH1F *heigen = (TH1F*)bkghistos[i];
				TH1F *hclone = (TH1F*)heigen->Clone();
				
				//Float_t bla = random.Gaus(heigen->Integral(),eigenerrors[i]*heigen->Integral());
				Float_t bla = random.Gaus(heigen->Integral(),uncs[i]*heigen->Integral());
				if (bla < 0) { 
					//cout << eigenerrors[i] << " " << bla << endl;
					bla = 0;
				}
				int n = random.Poisson(bla);

				for(int ibin = 1; ibin <= bin_y; ibin++) {
					Float_t val = hclone->GetBinContent(ibin);
					Float_t err = hclone->GetBinError(ibin);
					hclone->SetBinContent(ibin, random.Gaus(val, err));
				}

				for(int j = 0; j < n; j++) {
					hpseudo->Fill(hclone->GetRandom());
				}
				delete hclone;
			}
			int n = random.Poisson(hsignal->Integral());
			TH1F *hclone = (TH1F*)hsignal->Clone();
			for(int ibin = 1; ibin <= bin_y; ibin++) {
					Float_t val = hclone->GetBinContent(ibin);
					Float_t err = hclone->GetBinError(ibin);
					hclone->SetBinContent(ibin, random.Gaus(val, err));
			}
			for(int j = 0; j < n; j++) {
				hpseudo->Fill(hclone->GetRandom());
			}
			delete hclone;
		} else {
			int n = random.Poisson(hrec->Integral());
			for(int j = 0; j < n; j++) {
				hpseudo->Fill(hrec->GetRandom());
			}
		}
		
		unfold.SetInput(hpseudo);

		unfold.DoUnfold(tau,hpseudo,scaleBias);
		TH1F *hupseudo = new TH1F("upseudo","pseudo unfolded",bin_x,1,bin_x);
		unfold.GetOutput(hupseudo);
		// Ematrix not containing all errors,
		// check http://root.cern.ch/root/html/TUnfoldSys.html
		//TH2D *hperr = unfold.GetEmatrix("perror","perror");
		TH2F *hperr = new TH2F("perror","perror",bin_x,1,bin_x,bin_x,1,bin_x);
		unfold.GetEmatrix(hperr);
		// Add migration matrix stat. error
		//unfold.GetEmatrixSysUncorr(hperr, 0, false); 
		
		// correct binning
		TH1F *hupseudo_rebin = new TH1F(var_y+"_pseudo",var_y+"_pseudo",bin_x,list_x);
		for(Int_t i = 1; i <= bin_x; i++) {
			hupseudo_rebin->SetBinContent(i,hupseudo->GetBinContent(i));
			hupseudo_rebin->SetBinError(i,hupseudo->GetBinError(i));
		}

		// Calculate asymmetry
		Float_t asy = asymmetry(hupseudo_rebin);
		hasy.Fill(asy);
		Float_t asy_diff = genasy - asy;
		hasy_bias.Fill(asy_diff/genasy);
		Float_t perror = error_unfold(hperr,hupseudo_rebin);
		hStatErr.Fill(perror);
		hasy_pull.Fill(asy_diff/perror);

		// pull, rel. diff.
		for(Int_t k=1; k<=bin_x; k++) {
			Float_t diff = (hgen_presel->GetBinContent(k) - hupseudo->GetBinContent(k));
			
			hPull[k-1]->Fill(diff/hupseudo->GetBinError(k));
			hBin[k-1]->Fill(diff/hgen_presel->GetBinContent(k));
		}
		delete hperr;
		delete hupseudo;
		delete hupseudo_rebin;
	}
	// end pseudo

	// write results
	hurec->Write();
	hrhoij->Write();
	hematrix->Write();
	
	// pseudo exp results
	hasy.Write();
	hasy_bias.Write();
	hasy_pull.Write();
	hStatErr.Write();

	// write pull, bin histos
	for(Int_t i=0; i < bin_x; i++) {
		hBin[i]->Write();
		hPull[i]->Write();
	}

	fo->Close();

}

int main()
{	
	// load histograms
	TFile *f = new TFile("histos/rebinned.root");
	//TFile *f2 = new TFile("histos/data.root");
	TFile *f2 = new TFile("histos/pseudo_data.root");
	TFile *feff = new TFile("histos/efficiency.root");
	
	TH2F *hgenrec = (TH2F*)f->Get("matrix");
	TH1F *heff = (TH1F*)feff->Get("efficiency");
	TH1F *hgen = (TH1F*)f->Get(var_x+"_rebin");

	// 
	//TH1F *hrec = (TH1F*)f->Get(var_y+"_rebin");
	// DATA
	TH1F *hrec = (TH1F*)f2->Get(var_y+"__DATA");

	// reconstructed, subtracted, matrix, efficiency, bias
	unfold(hrec,hgenrec,heff,hgen,f2);
}
