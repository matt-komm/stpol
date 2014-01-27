import ROOT

f=ROOT.TFile("/home/fynu/mkomm/histos/mu__cos_theta__mva_0_0/rebinned.root")
matrix = f.Get("matrix")

hist =matrix.ProjectionX()
canvas=ROOT.TCanvas("canvas","",800,600)
hist.Draw()
canvas.Update()


eff=f.Get("efficiency")
gen=f.Get("hgen_presel")
matrix2=matrix.Clone()
matrix2.SetName("matrix2")
for ibin in range(hist.GetNbinsX()):
    matrix2.SetBinContent(ibin+1,0,gen.GetBinContent(ibin+1)*(1-eff.GetBinContent(ibin+1)))
    
canvas2=ROOT.TCanvas("canvas2","",800,600)
hist2 =matrix2.ProjectionX()
hist2.Draw()
canvas2.Update()
canvas2.WaitPrimitive()

