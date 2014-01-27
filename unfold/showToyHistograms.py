from ROOT import *
import math

def calcAsy(hist):
    sumUp=0.0
    sumDown=0.0
    for i in range(histo.GetNbinsX()):
        if histo.GetBinCenter(i+1)>0:
            sumUp+=histo.GetBinContent(i+1)
        else:
            sumDown+=histo.GetBinContent(i+1)
    return (sumUp-sumDown)/(sumUp+sumDown)

if __name__=="__main__":
    gROOT.SetStyle("Plain")
    '''
    file=TFile("PE_muon_statonly.root")
    tree=file.Get("products")
    histo=TH1D()
    tree.SetBranchAddress("pd__data_obs_cosTheta", histo)
    '''
    #file=TFile("unfolded_data_ele.root")
    file=TFile("unfolded_PE_ele.root")
    #file=TFile("unfolded_PE_muon_statonly.root")
    tree=file.Get("unfolded")
    histo=TH1D()
    tree.SetBranchAddress("tunfold", histo)
    
    asyHist = TH1F("asyHist","",60,0.1,0.7)
    
    for cnt in range(int(tree.GetEntries())):
        tree.GetEntry(cnt)
        
        asy=calcAsy(histo)
        asyHist.Fill(asy)
        print asy
        '''
        canvas=TCanvas("canvas"+str(cnt), "", 800, 600);
        histo.Draw();
        pave=TPaveText(0.1,0.8,0.5,0.9,"NDC")
        pave.AddText("A="+str(round(asy,4)))
        pave.Draw("Same")
        canvas.Update();
        canvas.WaitPrimitive();
        '''
        
    canvas=TCanvas("canvas"+str(cnt), "", 800, 600);
    asyHist.Draw();
    canvas.Update()
    canvas.WaitPrimitive()
    
