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
        printf("measured: %f\r\n", binningM[cnt]);
    }
    Float_t* binningT = new Float_t[truth->GetNbinsX()+1];
    for (int cnt=0; cnt<truth->GetNbinsX()+1;++cnt)
    {
        binningT[cnt]=truth->GetBinLowEdge(cnt+1);
        printf("truth: %f\r\n", binningT[cnt]);
    }
    TH1D* histo_input_tunfold = new TH1D("input","",measuredT,binningM);
    for (int cnt=0; cnt<1000; ++cnt)
    {
        histo_input_tunfold->Fill(gRandom->Uniform(-1.0,1.0));
    }
    
    for (int cnt=0;cnt<num;++cnt) {
        tau[cnt]=cnt/(1.0*num)*0.4+0.6;

        TUnfold* tunfold = new TUnfold(response,TUnfold::kHistMapOutputHoriz);
        tau[cnt]=TMath::Power(10.0,1.0*(cnt/(1.0*num)*7.0-6.0));

        //tau[cnt]=0.0001;
        tunfold->DoUnfold(tau[cnt],histo_input_tunfold);
        
        TH1D *x = new TH1D("x","unfolded",nbinsT,binningT);
        tunfold->GetOutput(x);
        TH2D* error = new TH2D("error","",nbinsT,binningT,nbinsT,binningT);
        tunfold->GetEmatrix(error);
        //tunfold->GetRhoIJ(error);
        
        /*TCanvas* test = new TCanvas("canvas","",800,600);
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
    if (argc<6) {
        printf("Usage:\r\n");
        printf("\tunfold \t[inputFile] [treeName] [branchName] [reponseFile] \r\n");
        printf("\t\t[reponseMatrixName] [outputFile]\r\n");
        return -1;
    }
    printf("use: inputFile='%s'\r\n",argv[1]);
    printf("use: treeName='%s'\r\n",argv[2]);
    printf("use: branchName='%s'\r\n",argv[3]);
    printf("use: responseFile='%s'\r\n",argv[4]);
    printf("use: responseMatrixName='%s'\r\n",argv[5]);
    printf("use: outputFile='%s'\r\n",argv[6]);

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
    TH2D* response =(TH2D*)responseFile.Get(argv[5]);;

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
        printf("measured: %f\r\n", binningM[cnt]);
    }
    Float_t* binningT = new Float_t[truth->GetNbinsX()+1];
    for (int cnt=0; cnt<truth->GetNbinsX()+1;++cnt)
    {
        binningT[cnt]=truth->GetBinLowEdge(cnt+1);
        printf("truth: %f\r\n", binningT[cnt]);
    }
    
    TH1D* histo_output_tunfold = new TH1D("output","",nbinsT,binningT);
    tree_output->Branch("tunfold",&histo_output_tunfold);

    double tau = scanTau(response)*0.11;
    printf("tau: %f\r\n",tau);

    int nevents = tree_input->GetEntries();
    //nevents=10000;
    printf("events: %i\r\n",nevents);
    gErrorIgnoreLevel = kPrint | kInfo | kWarning;
    
    for (int cnt=0; cnt<nevents;++cnt) {
        
        tree_input->GetEntry(cnt);
        
        if (nevents>200 && cnt%int(nevents/20.0)==0) {
            printf("unfolding...%i %%\r\n",int(100.0*cnt/nevents));
        }
        TUnfold* tunfold = new TUnfold(response,TUnfold::kHistMapOutputHoriz);
        tunfold->DoUnfold(tau,histo_input);
        histo_output_tunfold->Scale(0.0);
        tunfold->GetOutput(histo_output_tunfold);
        
        /*
        TCanvas* canvas = new TCanvas("canvas","",800,600);
        
        
        //histo_input->Draw();
        //measured->Draw("P*Same");
        histo_output_tunfold->Add(truth,-1.0);
        histo_output_tunfold->Draw();
        //truth->Scale(0.9);
        //truth->Draw("P*Same");
        */
        
        
        //canvas->Update();
        //canvas->WaitPrimitive();
        
        tree_output->Fill();
    }
    
    responseFile.Close();
    tree_output->Write();
    output.Close();
    input.Close();
    printf("finished\r\n");
    return 0;
}

