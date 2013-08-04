from ROOT import *
import math

if __name__=="__main__":
    gROOT.SetStyle("Plain")
    file=TFile("data_ele.root")
    tree=file.Get("products")
    histo=TH1D()
    tree.SetBranchAddress("pd__data_obs_cosTheta", histo)
    for cnt in range(int(tree.GetEntries())):
        tree.GetEntry(cnt)
        canvas=TCanvas("canvas"+str(cnt), "", 800, 600);
        histo.Draw();
        canvas.Update();
        canvas.WaitPrimitive();
        

