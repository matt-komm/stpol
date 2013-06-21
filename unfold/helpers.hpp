#ifndef HELPERS_H
#define HELPERS_H

#include <iostream>
#include <list>
#include <assert.h>
#include <TH1F.h>
#include <TH2F.h>
#include <TF1.h>
#include <THStack.h>
#include <TCanvas.h>
#include <TLegend.h>
#include <TMath.h>
#include <TFile.h>
#include <TLatex.h>
#include <TROOT.h>
#include <TSpline.h>
#include <TUnfold.h>
#include <TUnfoldSys.h>
#include <TGraphAsymmErrors.h>
#include <TGraphErrors.h>
#include <sstream>
#include <vector>
#include <utility>
#include <algorithm>
#include <TPave.h>
#include <TList.h>
#include <TPaveText.h>
#include <TVirtualPad.h>
#include <TClass.h>
#include "TApplication.h"
#include "TRandom3.h"
#include "TLorentzVector.h"

using namespace std;


// scales histogram to wanted value, works for 2d as well (!)
TH1* scale_to(TH1* h, double val)
{
  h->Scale(val/h->Integral());
  return h;
}


void fill_nooverflow_1d(TH1* h, double val, double weight)
{
  if(val > h->GetXaxis()->GetXmax())
    val = h->GetXaxis()->GetXmax()-0.00001;
  if(val < h->GetXaxis()->GetXmin())
    val = h->GetXaxis()->GetXmin()+0.00001; 
  h->Fill(val, weight);
}

void fill_nooverflow_2d(TH2* h, double valx, double valy, double weight)
{
  const double xmax = h->GetXaxis()->GetXmax();
  const double xmin = h->GetXaxis()->GetXmin();
  const double ymax = h->GetYaxis()->GetXmax();
  const double ymin = h->GetYaxis()->GetXmin();
  
  
  if(valx > xmax)
    valx =xmax-0.00001;
  if(valx < xmin)
    valx = xmin+0.00001; 
  
  if(valy > ymax)
    valy = ymax-0.00001;
  if(valy < ymin)
    valy = ymin+0.00001; 
  
  h->Fill(valx, valy, weight);
}


// finds bin by content and ensures a bin within actual range is returned
int findfixbin_nooverflow(TH1* h, double val)
{
  int nbins = h->GetNbinsX();
  
  int bin = h->FindFixBin(val);
  if(bin < 1) bin = 1;
  if(bin > nbins) bin = nbins;
  
  return bin;
}


double asymmetry_error_naive(double pos, double neg)
{
  return 2/pow(pos+neg,2)*sqrt(neg*pos*pos+pos*neg*neg); 
}


double asymmetry_error_custom_errors(double pos, double poserr, double neg, double negerr)
{
  return 2/pow(pos+neg,2)*sqrt(negerr*negerr*pos*pos + poserr*poserr*neg*neg); 
}



double asymmetryerror_afterunfolding_1d(TH2* Corr, TH1* unf)
{
  int int_maxbin = unf->GetNbinsX();
  
  if(int_maxbin%2 != 0)
    cout << "better choose different binning\n";
  
  double Nplus = unf->Integral(int_maxbin/2+1,int_maxbin);
  double Nminus = unf->Integral(1,int_maxbin/2);
  
  double E_Asy_neg = -2*Nplus/pow (Nplus + Nminus, 2);
  double E_Asy_pos =  2*Nminus/pow(Nplus + Nminus, 2);
  
  
  TH1D der_vector("","",int_maxbin, 0, int_maxbin);
  TH2D matrix_corr("","",int_maxbin, 0, int_maxbin, int_maxbin, 0, int_maxbin);
  TH1D temp_vector("","", int_maxbin, 0, int_maxbin);
  
  for(int i=1; i<=int_maxbin; i++)
  {
    if(i<=int_maxbin/2)
      der_vector.SetBinContent(i-1, E_Asy_neg);
    if(i>int_maxbin/2)
      der_vector.SetBinContent(i-1, E_Asy_pos);
    temp_vector.SetBinContent(i-1, 0);
        
    for(int j=1; j<=int_maxbin; j++)
    {
      matrix_corr.SetBinContent(i-1, j-1, Corr->GetBinContent(i,j));
    }
  }
  
  for(int i=0; i<int_maxbin; i++)
  {
    for(int j=0; j<int_maxbin; j++)
    {
      temp_vector.SetBinContent(i, temp_vector.GetBinContent(i) + matrix_corr.GetBinContent(i,j)*der_vector.GetBinContent(j));
    }
  }
  
  double Error_Unf=0;
  for(int i=0; i<int_maxbin; i++)
  {
    Error_Unf += der_vector.GetBinContent(i)*temp_vector.GetBinContent(i);
  }
  
  Error_Unf=sqrt(Error_Unf);

  return Error_Unf;
        
}



double asymmetryerror_afterunfolding_2d(TH2* Corr, int int_maxbin, double Nplus, double Nminus, int nbinssensvar )
{
  if(int_maxbin%2 != 0)
    cerr << "Bin number not divisible by 2.\n";
  
  double E_Asy_neg = -2*Nplus/pow (Nplus + Nminus, 2);
  double E_Asy_pos =  2*Nminus/pow(Nplus + Nminus, 2);
  
  TH1D der_vector("","",int_maxbin, 0, int_maxbin);
  TH2D matrix_corr("","",int_maxbin, 0, int_maxbin, int_maxbin, 0, int_maxbin);
  TH1D temp_vector("","", int_maxbin, 0, int_maxbin);
  
  for(int i=1; i<=int_maxbin; i++)
  {
    // the unwrapped 1d histo has several cycles of the whole sensvar distribution, each with a different mass
    // value (or pt_ttbar, or..). so we need to get the index within the current cycle to determine if we're
    // looking at a bin with positive or negative sensvar.
    const int xindex = int((i-1)/nbinssensvar);
    const int mcleanedIndex = i - xindex * nbinssensvar;
    
    if(mcleanedIndex<=nbinssensvar/2)
      der_vector.SetBinContent(i-1, E_Asy_neg);
    else
      der_vector.SetBinContent(i-1, E_Asy_pos);
    
    
    
    temp_vector.SetBinContent(i-1, 0);
    
    for(int j=1; j<=int_maxbin; j++)
    {
      matrix_corr.SetBinContent(i-1, j-1, Corr->GetBinContent(i,j));
    }
  }
  
  for(int i=0; i<int_maxbin; i++)
  {
    for(int j=0; j<int_maxbin; j++)
    {
      temp_vector.SetBinContent(i, temp_vector.GetBinContent(i) + matrix_corr.GetBinContent(i,j)*der_vector.GetBinContent(j));
    }
  }
  
  double Error_Unf=0;
  for(int i=0; i<int_maxbin; i++)
  {
    Error_Unf += der_vector.GetBinContent(i)*temp_vector.GetBinContent(i);
  }
  
  Error_Unf=sqrt(Error_Unf);
  
  return Error_Unf;
  
}


// gives asymmetry error in one bin of the x axis. Nplus and Nminus already must contain the numbers for that sole bin.
double asymmetryerror_afterunfolding_2d_onexbin(TH2* Corr, int int_maxbin, double Nplus, double Nminus, int nbinssensvar, int xbin)
{
  if(int_maxbin%2 != 0)
    cerr << "Bin number not divisible by 2.\n";
    
  double E_Asy_neg = -2*Nplus/pow (Nplus + Nminus, 2);
  double E_Asy_pos =  2*Nminus/pow(Nplus + Nminus, 2);
  
  
  TH1D der_vector("","",int_maxbin, 0, int_maxbin);
  TH2D matrix_corr("","",int_maxbin, 0, int_maxbin, int_maxbin, 0, int_maxbin);
  TH1D temp_vector("","", int_maxbin, 0, int_maxbin);
  
  for(int i=1; i<=int_maxbin; i++)
  {
    // the unwrapped 1d histo has several cycles of the whole sensvar distribution, each with a different mass
    // value (or pt_ttbar, or..). so we need to get the index within the current cycle to determine if we're
    // looking at a bin with positive or negative sensvar.
    const int xindex = int((i-1)/nbinssensvar);
    
    if(xindex != xbin) // if it's in another x bin it doesn't go into asymmetry calculation, so derivative is zero
    {
      der_vector.SetBinContent(i-1, 0);
    }
    else
    {
      const int mcleanedIndex = i - xindex * nbinssensvar;
      if(mcleanedIndex<=nbinssensvar/2)
        der_vector.SetBinContent(i-1, E_Asy_neg);
      else
        der_vector.SetBinContent(i-1, E_Asy_pos);
    }
        
    
    temp_vector.SetBinContent(i-1, 0);
    
    for(int j=1; j<=int_maxbin; j++)
    {
      matrix_corr.SetBinContent(i-1, j-1, Corr->GetBinContent(i,j));
    }
  }
  
  for(int i=0; i<int_maxbin; i++)
  {
    for(int j=0; j<int_maxbin; j++)
    {
      temp_vector.SetBinContent(i, temp_vector.GetBinContent(i) + matrix_corr.GetBinContent(i,j)*der_vector.GetBinContent(j));
    }
  }
  
  
  double Error_Unf=0;
  for(int i=0; i<int_maxbin; i++)
  {
    Error_Unf += der_vector.GetBinContent(i)*temp_vector.GetBinContent(i);
  }
  
  Error_Unf=sqrt(Error_Unf);
  
  return Error_Unf;
  
}

/*
// simulates the error on a sample with different number of events N
double asymmetry_error_customN(double pos, double neg, double N)
{
  double ges = pos + neg;
  pos = pos * N / ges;
  neg = neg * N / ges;
  return 2/pow(pos+neg,2)*sqrt(neg*pos*pos+pos*neg*neg); 
}*/

// concatenates columns to make 1d histo out of 2d histo
void unwrap2dhisto(TH2* h2, TH1* h1)
{
  int n=0;
  for(int x=1; x<=h2->GetXaxis()->GetNbins(); x++)
  {
    for(int y=1; y<=h2->GetYaxis()->GetNbins(); y++)
    {
      n++;
      h1->SetBinContent(n, h2->GetBinContent(x,y));
      h1->SetBinError(n, h2->GetBinError(x,y));
    }
  }
  h1->Sumw2();
}

// helper class to get correctly weighted histograms from several input files.
// create an object, for each file call addFile with the correct weight,
// then get weighted histograms by calling getHisto.
class CombinedHisto
{
  public:
  CombinedHisto() {}
  
  void addFile(TString filename, double weight)
  {
    TFile* file = new TFile(filename);
    files.AddLast((TObject*)file);
    weights.push_back(weight);    
  }
  
  TH1F* getHisto(TString path)
  {
    TH1F* hist = 0;
    TIter nextfile(&files);        
    TFile* file;
       
    list<double>::iterator weight_iter = weights.begin();
    
    while(( file = (TFile*) nextfile() ))
    {
      double weight = *weight_iter;
      
      if(!hist)
      {
        hist = (TH1F*)file->Get(path);
        hist->Scale(weight);
      }
      else
      {
        TH1F* temp = (TH1F*)file->Get(path);
        temp->Scale(weight);
        hist->Add( temp );
        delete temp;
      }
      
      weight_iter++;
    }
    
    return hist;    
  }
  
  
  
  private:
  TList files;
  list<double> weights;
  
};


string getEnv(const char* name)
{
  const char* value;
  value = getenv(name);
  if(value)
  {
    return value;
  }
  else
  {
    cerr << "ENVVAR " << name << " MISSING, EXITING" << endl;
    exit(1);
    return string();
  } 
}



double Rapidity(const TLorentzVector& l){
  double ee = l.E();
  double ppz = l.Pz();
  return .5f* log( (ee+ppz)/(ee-ppz) );
}


// normalize migmatrix column-wise
TH2* normalizeMigMat(TH2* h)
{
  TH2* hclone = (TH2*) h->Clone();
  const int xbins = hclone->GetNbinsX();
  const int ybins = hclone->GetNbinsY();
    
  for(int x=0; x<xbins; x++)  
  {
    double integ = hclone->Integral(x+1, x+1, 1, ybins);
    for(int y=0; y<ybins; y++)
    {
      hclone->SetBinContent(x+1,y+1, hclone->GetBinContent(x+1, y+1)/integ);
    }
  }
  
  return hclone;
}



void saveAs(TCanvas* c, string path)
{
  c->SaveAs((path+".pdf").c_str());
  c->SaveAs((path+".png").c_str());
  //c->SaveAs((path+".eps").c_str());
}

void saveAs(TCanvas* c, TString path)
{
  c->SaveAs(path+".pdf");
  c->SaveAs(path+".png");
  //c->SaveAs(path+".eps");
}
void saveAs(TCanvas* c, const char* path)
{
  TString p(path);
  c->SaveAs(p+".pdf");
  c->SaveAs(p+".png");
  //c->SaveAs(p+".eps");
}

void saveAs(TVirtualPad* c, string path)
{
  c->SaveAs((path+".pdf").c_str());
  c->SaveAs((path+".png").c_str());
  //c->SaveAs((path+".eps").c_str());
}

void saveAs(TVirtualPad* c, TString path)
{
  c->SaveAs(path+".pdf");
  c->SaveAs(path+".png");
  //c->SaveAs(path+".eps");
}
void saveAs(TVirtualPad* c, const char* path)
{
  TString p(path);
  c->SaveAs(p+".pdf");
  c->SaveAs(p+".png");
  //c->SaveAs(p+".eps");
}


#endif // HELPERS_H
