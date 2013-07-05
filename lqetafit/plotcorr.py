from ROOT import TFile, TCanvas, TColor, gStyle
from math import sqrt
from array import array

fcov = TFile("cov.root")
canvas = TCanvas("c1","Covariance")
hcov = fcov.Get("covariance")
hcorr = hcov.Clone("correlation")
hcorr.SetTitle("correlation")
hcorr.Reset()
hcorr.Sumw2()

n = hcorr.GetNbinsX()

std = []

# get std deviations from diagonal
for i in range(n):
    std.append(sqrt(hcov.GetBinContent(i+1,i+1)))

for i in range(n):
    for j in range(n):
        hcorr.SetBinContent(i+1,j+1,hcov.GetBinContent(i+1,j+1)/std[i]/std[j])

hcorr.SetMinimum(-1)
hcorr.SetMaximum(1)

# text color
#hcorr.SetMarkerColor(0)

# setup color palette
r = [1.0, 1.0, 0.0]
g = [0.0, 1.0, 0.3]
b = [0.0, 1.0, 1.0]
stop = [.0, 0.5, 1.0]

# convert to c arrays
rarray = array('d',r)
garray = array('d',g)
barray = array('d',b)
stoparray = array('d',stop)

palsize = 100
fi = TColor.CreateGradientColorTable(3, stoparray, rarray, garray, barray, palsize)
palette = []
for i in range(palsize):
    palette.append(fi+i)
palarray = array('i',palette)

gStyle.SetPalette(palsize,palarray)
gStyle.SetOptStat(0)

hcorr.Draw("COLZ TEXT")
canvas.Print("corr.png")
canvas.Print("corr.pdf")
fcov.Close()
