#include <stdio.h>
#include <stdlib.h>

#include "TApplication.h"
#include "TCanvas.h"
#include "TH1D.h"
#include "TFile.h"
#include "TTree.h"
#include "TSystem.h"
#include "TRandom.h"
#include "TMatrixD.h"
#include "TMath.h"
#include "TUnfold.h"
#include "TSpline.h"
#include "TMinuit.h"
#include "TUnfoldDensity.h"
using namespace std;


void copyHistContent(TH1D* from, TH1D* to)
{
    for (int cnt=0; cnt<from->GetNbinsX()+2;++cnt) {
        to->SetBinContent(cnt,from->GetBinContent(cnt));
    }
}

void copyMatrixContent(TMatrixD* from, TMatrixD* to)
{
    for (int row=0; row<from->GetNrows();++row){
        for (int col=0; col<from->GetNcols(); ++col) {
            (*to)[row][col]=(*from)[row][col];
        }
    }
}

TMatrixD* convertHistToMatrix(TH2D* from)
{
    TMatrixD* matrix = new TMatrixD(from->GetNbinsX(),from->GetNbinsY());
    for (int row=0; row<from->GetNbinsX();++row){
        for (int col=0; col<from->GetNbinsY(); ++col) {
            (*matrix)[row][col]=(*from).GetBinContent(row+1,col+1);
        }
    }
    return matrix;
}


TUnfold* myUnfold1d_TUnfoldGlobalPointerForTMinuit;
TH1F* myUnfold1d_hdataGlobalPointerForTMinuit;

static void myUnfold1d_globalFunctionForMinuit(int &npar, double *gin, double &f, double *par, int iflag)
{
  
  const double logtau = par[0];
  const double scaleBias = par[1];
  myUnfold1d_TUnfoldGlobalPointerForTMinuit->DoUnfold(pow(10, logtau), myUnfold1d_hdataGlobalPointerForTMinuit, scaleBias);
  
  f = myUnfold1d_TUnfoldGlobalPointerForTMinuit->GetRhoAvg();
}


double minimizeRhoAverage(TH2D* response, int nsteps, double log10min, double log10max)
{
    TH1D* measured =  response->ProjectionY();
    TH1D* truth =  response->ProjectionX();
    int nbinsM=measured->GetNbinsX();
    int nbinsT=truth->GetNbinsX();
    Float_t* binningM = new Float_t[nbinsM+1];
    for (int cnt=0; cnt<nbinsM+1;++cnt)
    {
        binningM[cnt]=measured->GetBinLowEdge(cnt+1); 
        //printf("measured: %f\r\n", binningM[cnt]);
    }
    Float_t* binningT = new Float_t[nbinsT+1];
    for (int cnt=0; cnt<nbinsT+1;++cnt)
    {
        binningT[cnt]=truth->GetBinLowEdge(cnt+1);
        //printf("truth: %f\r\n", binningT[cnt]);
    }
    
  TH1F* hdata = new TH1F("input","",nbinsM,binningM);
    for (int cnt=0; cnt<1000; ++cnt)
    {
        hdata->Fill(gRandom->Uniform(-1.0,1.0));
    }
    TUnfoldDensity* unfold = new TUnfoldDensity(response,TUnfold::kHistMapOutputHoriz,TUnfold::kRegModeCurvature);
    unfold->SetInput(hdata);
    
  myUnfold1d_TUnfoldGlobalPointerForTMinuit = unfold;
  myUnfold1d_hdataGlobalPointerForTMinuit = hdata;
  
  // Instantiate Minuit for 2 parameters
  TMinuit minuit(2);
  minuit.SetFCN(myUnfold1d_globalFunctionForMinuit);
  minuit.SetPrintLevel(1); // -1 no output, 1 output
  
  //TMinuit::DefineParameter( Int_t parNo, const char *name, Double_t initVal, Double_t initErr, Double_t lowerLimit, Double_t upperLimit )
  minuit.DefineParameter(0, "logtau", (log10min+log10max)/2, 1, log10min, log10max);
  minuit.DefineParameter(1, "scaleBias", 1.0, 0.01, 0.0, 10.0);
  minuit.FixParameter(1);
  
  minuit.SetMaxIterations(nsteps);
  minuit.Migrad();
  
  double bestlogtau = -1000;
  double bestlogtau_err = -1000; // error is meaningless because we don't have a likelihood, but method expects it
  minuit.GetParameter(0, bestlogtau, bestlogtau_err);
  //printf("tau: %f\r\n",bestlogtau);
  return pow(10, bestlogtau);
  //unfold->DoUnfold(pow(10, bestlogtau), hdata, scaleBias); 
}

double scanTau(TH2D* response)
{
    const int num=100;
    double* tau = new double[num];
    double* pmean = new double[num];
    double pmean_min=1.0;
    double pmean_min_tau=0.0;
    double* pmax = new double[num];
    double pmax_min=1.0;
    double pmax_min_tau=0.0;
    double* phalfmax=new double[num];
    double phalfmax_min=1.0;
    double phalfmax_min_tau=0.0;
    
    
    TH1D* measured =  response->ProjectionY();
    TH1D* truth =  response->ProjectionX();
    int measuredT=measured->GetNbinsX();
    int nbinsT=truth->GetNbinsX();
    
    /*TCanvas* test = new TCanvas("canvas","",800,600);
    test->Divide(2,1);
    test->cd(1);
    measured->SetTitle("measured");
    measured->Draw();
    test->cd(2);
    truth->SetTitle("truth");
    truth->Draw();
    test->Update();
    test->WaitPrimitive();*/
    Float_t* binningM = new Float_t[measured->GetNbinsX()+1];
    for (int cnt=0; cnt<measured->GetNbinsX()+1;++cnt)
    {
        binningM[cnt]=measured->GetBinLowEdge(cnt+1); 
    }
    Float_t* binningT = new Float_t[truth->GetNbinsX()+1];
    for (int cnt=0; cnt<truth->GetNbinsX()+1;++cnt)
    {
        binningT[cnt]=truth->GetBinLowEdge(cnt+1);
    }
    TH1D* histo_input_tunfold = new TH1D("input","",measuredT,binningM);
    for (int cnt=0; cnt<1000; ++cnt)
    {
        histo_input_tunfold->Fill(gRandom->Uniform(-1.0,1.0));
    }
    /*
    cout<<"......scan for tau......."<<endl;
    TUnfoldDensity* tunfold = new TUnfoldDensity(response,TUnfold::kHistMapOutputHoriz,TUnfold::kRegModeSize);
    tunfold->SetInput(histo_input_tunfold);
    TSpline* scanResult;
    cout<<"scanning...";
    int nmin = tunfold->ScanTau(100,0,0,&scanResult);
    cout<<"  finished"<<endl;
    TCanvas* canvas = new TCanvas("scan","",800,600);
    scanResult->Draw();
    canvas->Update();
    canvas->Print("scan.pdf");
    double taumin=0.0;
    double corrmin=0.0;
    scanResult->GetKnot(nmin, taumin, corrmin);
    return taumin;
    */
    
    for (int cnt=0;cnt<num;++cnt) {
        tau[cnt]=cnt/(1.0*num)*0.4+0.6;

        TUnfoldDensity* tunfold = new TUnfoldDensity(response,TUnfold::kHistMapOutputHoriz,TUnfold::kRegModeCurvature);
        tau[cnt]=TMath::Power(10.0,1.0*(cnt/(1.0*num)*7.0-6.0));

        //tau[cnt]=0.0001;
        tunfold->DoUnfold(tau[cnt],histo_input_tunfold);
        
        //TH1D *x = new TH1D("x","unfolded",nbinsT,binningT);
        TH1 *x = tunfold->GetOutput("x","unfolded");
        TH2D* error = new TH2D("error","",nbinsT,binningT,nbinsT,binningT);
        tunfold->GetEmatrix(error);
        //tunfold->GetRhoIJ(error);
        /*
        TCanvas* test = new TCanvas("canvas","",800,600);
        test->Divide(2,1);
        test->cd(1);
        x->SetTitle("unfolded");
        x->Draw();
        test->cd(2);
        
        error->SetTitle("error");
        error->Draw("colz");
        
        test->Update();
        test->WaitPrimitive();
        */
        
        
        
        TMatrixD* cov_matrix = convertHistToMatrix(error);
        TMatrixD inv_cov_matrix=TMatrixD(TMatrixD::kInverted,*cov_matrix);
        
        
        double* p = new double[nbinsT];
        pmean[cnt]=0.0;
        pmax[cnt]=0.0;
        for (int i=0; i<nbinsT; ++i) {
            p[i]=sqrt(1.0-1.0/(inv_cov_matrix[i][i]*(*cov_matrix)[i][i]));
            pmean[cnt]+=p[i];
            if (p[i]>pmax[cnt]) {
                pmax[cnt]=p[i];
            }
            if ((i>(nbinsT/2)) && (phalfmax[cnt]<p[i])) {
            	phalfmax[cnt]=p[i];
            }
        }
        pmean[cnt]=pmean[cnt]/(1.0*nbinsT);
        if (pmean[cnt]<pmean_min) {
            pmean_min=pmean[cnt];
            pmean_min_tau=tau[cnt];
        }
        if (pmax[cnt]<pmax_min) {
            pmax_min=pmax[cnt];
            pmax_min_tau=tau[cnt];
        }
        if (phalfmax[cnt]<phalfmax_min) {
			phalfmax_min=phalfmax[cnt];
			phalfmax_min_tau=tau[cnt];
		}
		
    }
    
    return pmean_min_tau;
}

int main( int argc, const char* argv[] )
{
    TApplication* rootapp = new TApplication("example",0,0);
    if (argc<7) {
        printf("Usage:\r\n");
        printf("\tunfold \t[inputFile] [treeName] [branchName] [reponseFile] \r\n");
        printf("\t\t[reponseMatrixName] [outputFile] [reg]\r\n");
        return -1;
    }
    printf("use: inputFile='%s'\r\n",argv[1]);
    printf("use: treeName='%s'\r\n",argv[2]);
    printf("use: branchName='%s'\r\n",argv[3]);
    printf("use: responseFile='%s'\r\n",argv[4]);
    printf("use: responseMatrixName='%s'\r\n",argv[5]);
    printf("use: outputFile='%s'\r\n",argv[6]);
    printf("use: regScale='%f'\r\n",atof(argv[7]));
    
    TFile input(argv[1],"r");

    TTree* tree_input = (TTree*)input.Get(argv[2]);
    
    TH1D* histo_input = new TH1D();
    tree_input->SetBranchAddress(argv[3],&histo_input);
    tree_input->GetEntry(0);
    
    /*
    TCanvas* canvas = new TCanvas("canvas","",800,600);  
    histo_input->Draw();
    canvas->Update();
    canvas->WaitPrimitive();
    */
    
    TFile responseFile(argv[4],"r");
    TH2D* response =(TH2D*)responseFile.Get(argv[5]);

    TFile output(argv[6],"RECREATE");
    TTree* tree_output = new TTree("unfolded","");


    TH1D* measured =  response->ProjectionY();
    TH1D* truth =  response->ProjectionX();
    int measuredT=measured->GetNbinsX();
    int nbinsT=truth->GetNbinsX();
    
    /*TCanvas* test = new TCanvas("canvas","",800,600);
    test->Divide(2,1);
    test->cd(1);
    measured->SetTitle("measured");
    measured->Draw();
    test->cd(2);
    truth->SetTitle("truth");
    truth->Draw();
    test->Update();
    test->WaitPrimitive();*/
    Float_t* binningM = new Float_t[measured->GetNbinsX()+1];
    for (int cnt=0; cnt<measured->GetNbinsX()+1;++cnt)
    {
        binningM[cnt]=measured->GetBinLowEdge(cnt+1); 
    }
    Float_t* binningT = new Float_t[truth->GetNbinsX()+1];
    for (int cnt=0; cnt<truth->GetNbinsX()+1;++cnt)
    {
        binningT[cnt]=truth->GetBinLowEdge(cnt+1);
    }
    
    TH1D* histo_output_tunfold = new TH1D("output","",nbinsT,binningT);
    tree_output->Branch("tunfold",&histo_output_tunfold);
    gErrorIgnoreLevel = kPrint | kInfo | kWarning;
    
    double tau = scanTau(response);
    double tauSteffen = minimizeRhoAverage(response, 100, -10, 0);
    printf("tau: %e\r\n",tau);
    printf("tauSteffen: %e\r\n",tauSteffen);
    int nevents = tree_input->GetEntries();
    //nevents=10000;
    printf("events: %i\r\n",nevents);
    
    tau=tau*atof(argv[7]);
    for (int cnt=0; cnt<nevents;++cnt) {
        
        tree_input->GetEntry(cnt);
        printf("unfolding...%i \r\n",cnt);
        if (nevents>200 && cnt%int(nevents/20.0)==0) {
            printf("unfolding...%i %%\r\n",int(100.0*cnt/nevents));
        }
        //just add a small amount such that the linear system stays well defined and solvable
        for (int ibin=0; ibin<histo_input->GetNbinsX();++ibin)
        {
             histo_input->SetBinContent(ibin+1,histo_input->GetBinContent(ibin+1)+0.000001);
        }
        TUnfoldDensity* tunfold = new TUnfoldDensity(response,TUnfold::kHistMapOutputHoriz, TUnfold::kRegModeCurvature);
        //tunfold->SetBias(truth);
        tunfold->DoUnfold(tau,histo_input);
        histo_output_tunfold->Scale(0.0);
        //tunfold->GetOutput(histo_output_tunfold);
        TH1 *x = tunfold->GetOutput("x","unfolded");
        if (x->GetNbinsX()!=histo_output_tunfold->GetNbinsX())
        {
            cout<<"error - output binning not expected - "<<x->GetNbinsX()<<":"<<histo_output_tunfold->GetNbinsX()<<endl;
            return -1;
        }
        for (int ibin=0; ibin<x->GetNbinsX();++ibin)
        {
             histo_output_tunfold->SetBinContent(ibin+1,x->GetBinContent(ibin+1));
        }
        /*
        TCanvas* canvas = new TCanvas("canvas","",800,600);
        //histo_input->Draw();
        //measured->Draw("P*Same");
        //histo_output_tunfold->Add(truth,-1.0);
        histo_output_tunfold->Draw();
        //truth->Scale(1.06);
        //truth->Draw("P*Same");
        canvas->Update();
        canvas->WaitPrimitive();
        */
        tree_output->Fill();
    }
    
    responseFile.Close();
    tree_output->Write();
    output.Close();
    input.Close();
    printf("finished\r\n");
    return 0;
}

