import ROOT
import numpy
'''
efficiencyFile="/home/fynu/mkomm/ele__cos_theta__mva_0_13/efficiency.root"
matrixFile="/home/fynu/mkomm/ele__cos_theta__mva_0_13/rebinned.root"
outputFile="/home/fynu/mkomm/ele__cos_theta__mva_0_13/matrix.root"
'''

efficiencyFile="/home/fynu/mkomm/mu__cos_theta__mva_0_06/efficiency.root"
matrixFile="/home/fynu/mkomm/mu__cos_theta__mva_0_06/rebinned.root"
outputFile="/home/fynu/mkomm/mu__cos_theta__mva_0_06/matrix.root"

file=ROOT.TFile(efficiencyFile)
efficencyHist=file.Get("efficiency")
print efficencyHist
genHist=file.Get("hgen_presel")
print genHist
genSelHist=file.Get("hgen")
print genSelHist

#fill genHist into efficenxy binned histo



#genMiss.Draw()
file2=ROOT.TFile(matrixFile)
fileOut=ROOT.TFile(outputFile,"RECREATE")
matrix=file2.Get("matrix")


print matrix
measured =  matrix.ProjectionY();
truth =  matrix.ProjectionX();
nbinsM=measured.GetNbinsX();
nbinsT=truth.GetNbinsX();

binning=numpy.zeros(truth.GetNbinsX()+1)
for i in range(truth.GetNbinsX()+1):
    binning[i]=truth.GetBinLowEdge(i+1)
    print i,binning[i]

genHistRebinned=genHist.Rebin(truth.GetNbinsX(),genHist.GetName()+"_rebinned",binning)
genSelHistRebinned=genSelHist.Rebin(truth.GetNbinsX(),genSelHist.GetName()+"_rebinned",binning)
genMiss=ROOT.TH1F(genHistRebinned)
genMiss.SetName(genMiss.GetName()+"_miss")
genMiss.Add(genSelHistRebinned,-1.0)

matrixOut=ROOT.TH2F(matrix)
for ix in range(genMiss.GetNbinsX()):
    
    matrixOut.SetBinContent(ix+1,0,genMiss.GetBinContent(ix+1))
genHistRebinned.Write()
genSelHistRebinned.Write()
genMiss.Write()
matrixOut.Write()
fileOut.Close()
file2.Close()
file.Close()

