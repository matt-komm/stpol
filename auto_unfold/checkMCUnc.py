import ROOT
import os
import math

fileName="test.root"
branchName="products"
histoTreeName="pd__data_obs_cos_theta_bg"
ROOT.gROOT.SetBatch(True)
file=ROOT.TFile(fileName)
tree=file.Get(branchName)
histo=ROOT.TH1D()
tree.SetBranchAddress(histoTreeName, histo)
tree.GetEntry(0)
histoBinDist=[]
for ibin in range(histo.GetNbinsX()):
    histoBinDist.append(ROOT.TH1F("hist"+str(ibin),"bin "+str(ibin),100,0.0,300.0))
for ientry in range(tree.GetEntries()):
    tree.GetEntry(ientry)
    for ibin in range(histo.GetNbinsX()):
        histoBinDist[ibin].Fill(histo.GetBinContent(ibin+1))
        
canvas=ROOT.TCanvas("canvas","",1800,1600)
canvas.Divide(4,3)
for ibin in range(histo.GetNbinsX()):
    canvas.cd(ibin+1)
    histoBinDist[ibin].Draw()
    print ibin
    print "\tmean:",round(histoBinDist[ibin].GetMean(),3),"rms:",round(histoBinDist[ibin].GetRMS(),3)
    print "\tsqrt(mean):",round(math.sqrt(histoBinDist[ibin].GetMean()),3)
    
canvas.Update()
canvas.Print("binDist.pdf")
#canvas.WaitPrimitive()
