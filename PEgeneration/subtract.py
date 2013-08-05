from ROOT import *
import math
import numpy

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
    for name in [
        #"PE_muon_nominal",
        #"PE_muon_statonly",
        #"PE_muon_yieldonly",
        #"PE_muon",
        "data_muon"
        ]:
        print "processing ",name
        histo=TH1D()
        histoBG=TH1D()
        file=TFile(name+".root")
        tree=file.Get("products")
        
        tree.SetBranchAddress("pd__data_obs_cosTheta", histo)
        #histo.SetDirectory(0)
        
        file2=TFile("PE_muon_nominal.root")
        
        tree2=file2.Get("products")
        tree2.SetBranchAddress("pd__data_obs_cosThetaBG", histoBG)
        #histoBG.SetDirectory(0)
        
        fileOut=TFile("subtracted_"+name+".root","RECREATE")
        treeOut=TTree("subtracted","subtracted")

        binning=numpy.array([-1.000000,-0.421600,-0.180600,0.000000,0.089400,0.189400,0.275800,0.356200,0.434400,0.507000,0.573600,0.639400,0.709200,0.789400,1.000000])
        histoSubtracted=TH1D("subtracted","",len(binning)-1,binning)
        treeOut.Branch("histos", histoSubtracted)
        
        for cnt in range(int(tree.GetEntries())):
            tree.GetEntry(cnt)
            tree2.GetEntry(cnt)
            
            for ibin in range(len(binning)-1):
                y=histo.GetBinContent(ibin+1)-histoBG.GetBinContent(ibin+1)
                if (y<0):
                    print "warn: ",name,y
                    histoSubtracted.SetBinContent(ibin+1,0)
                else:
                    histoSubtracted.SetBinContent(ibin+1,y)
            '''
            canvas=TCanvas("canvas"+str(cnt), "", 800, 600)
            histo.Draw()
            histoBG.Draw("P*Same")
            histoSubtracted.Draw("Same")
            canvas.Update();
            canvas.WaitPrimitive();
            '''
            treeOut.Fill()
        
        treeOut.Write()
        fileOut.Close()
        file2.Close()
        file.Close()
    
