import ROOT
import numpy

file=ROOT.TFile("/home/fynu/mkomm/mu_cos_theta_mva_0_09/efficiency.root")
efficencyHist=file.Get("efficiency")
print efficencyHist
genHist=file.Get("hgen_presel_rebin")
print genHist
genSelHist=file.Get("hgen")
print genSelHist

#fill genHist into efficenxy binned histo

binning=[]
for i in range(efficencyHist.GetNbinsX()+1):
    binning.append(efficencyHist.GetBinLowEdge(i+1))

genMiss=ROOT.TH1D("genMiss","",len(binning)-1,numpy.array(binning))
#canvas=ROOT.TCanvas("canvas","",800,600)
for cnt in range(genMiss.GetNbinsX()):
    print efficencyHist.GetBinContent(cnt+1)
    genMiss.SetBinContent(cnt+1,genHist.GetBinContent(cnt+1)*(1-efficencyHist.GetBinContent(cnt+1)))
#genMiss.Draw()
file2=ROOT.TFile("/home/fynu/mkomm/mu_cos_theta_mva_0_09/rebinned.root")
fileOut=ROOT.TFile("/home/fynu/mkomm/mu_cos_theta_mva_0_09/matrix.root","RECREATE")
matrix=file2.Get("matrix")
print matrix
matrixOut=ROOT.TH2F(matrix)
for ix in range(genMiss.GetNbinsX()):
    print genMiss.GetBinContent(ix+1)
    matrixOut.SetBinContent(ix+1,0,genMiss.GetBinContent(ix+1));
matrixOut.Write()
fileOut.Close()
file2.Close()
file.Close()

