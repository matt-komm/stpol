import numpy as np
import ROOT

qs = np.arange(0.02, 1.00, 0.02)
Ns = range(5, 105, 5)

KSSgraph = ROOT.TGraph2D(len(Ns)*len(qs)) # Kolmogorov-Smirnov for signal
KSSgraph.SetNameTitle("KSSgraph", "Kolmogorov-Smirnov for signal")
KSBgraph = ROOT.TGraph2D(len(Ns)*len(qs)) # Kolmogorov-Smirnov for background
KSBgraph.SetNameTitle("KSBgraph", "Kolmogorov-Smirnov for background")
KSgraph =  ROOT.TGraph2D(len(Ns)*len(qs)) # Kolmogorov-Smirnov
KSgraph.SetNameTitle("KSgraph", "Kolmogorov-Smirnov")
Agraph =   ROOT.TGraph2D(len(Ns)*len(qs)) # area under ROC curve
Agraph.SetNameTitle("Agraph", "Area under ROC curve")

i = 0

for q in qs:
	f = ROOT.TFile("trained/{0:.2f}.root".format(q))
	for N in Ns:
		# calculate Kolmogorov-Smirnov probability
		hs_test = f.Get("Method_BDT/{0:.2f}_BDT_{1}/MVA_{0:.2f}_BDT_{1}_S".format(q, N))
		hb_test = f.Get("Method_BDT/{0:.2f}_BDT_{1}/MVA_{0:.2f}_BDT_{1}_B".format(q, N))
		hs_train = f.Get("Method_BDT/{0:.2f}_BDT_{1}/MVA_{0:.2f}_BDT_{1}_Train_S".format(q, N))
		hb_train = f.Get("Method_BDT/{0:.2f}_BDT_{1}/MVA_{0:.2f}_BDT_{1}_Train_B".format(q, N))
		KSS = hs_test.KolmogorovTest(hs_train)
		KSB = hb_test.KolmogorovTest(hb_train)
		KSSgraph.SetPoint(i, q, N, KSS)
		KSBgraph.SetPoint(i, q, N, KSB)
		KSgraph.SetPoint(i, q, N, min(KSS, KSB))
		
		# calculate area under ROC curve
		hROC = f.Get("Method_BDT/{0:.2f}_BDT_{1}/MVA_{0:.2f}_BDT_{1}_rejBvsS".format(q, N))
		A = hROC.Integral("width")
		Agraph.SetPoint(i, q, N, A)

		i += 1

canvases = {}

for g in [KSSgraph, KSBgraph, KSgraph, Agraph]:
	canvases[g] = ROOT.TCanvas()
	g.Draw("COLZ")
	img = ROOT.TImage.Create()
	img.FromPad(canvases[g])
	img.WriteImage(g.GetName()+".png")



