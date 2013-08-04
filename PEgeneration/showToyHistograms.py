from ROOT import *
import math

if __name__=="__main__":
    gROOT.SetStyle("Plain")
    file=TFile("nominal_rebinned.root")
    tree=file.Get("subtracted")
    histo=TH1D()
    tree.SetBranchAddress("histos", histo)
    for cnt in range(int(tree.GetEntries())):
        tree.GetEntry(cnt)
        canvas=TCanvas("canvas"+str(cnt), "", 800, 600);
        histo.Draw();
        canvas.Update();
        canvas.WaitPrimitive();
        histo.Scale(0.0)

