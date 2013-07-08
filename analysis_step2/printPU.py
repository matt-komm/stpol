import ROOT
import sys

f = ROOT.TFile(sys.argv[1])

hist = f.Get("pileup")
hist.Scale(1.0/hist.Integral())
for i in range(1, hist.GetNbinsX()+1):
    print hist.GetBinContent(i)
