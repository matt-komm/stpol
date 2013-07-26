import numpy as np
import ROOT

qs = np.linspace(0.02, .98, 49)
Ns = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 17, 18, 20, 22, 23, 25, 28, 30, 33, 35, 38, 42, 45, 49, 53, 58, 63, 68, 74, 81, 87, 95, 103, 112, 121, 132, 143, 155, 168, 183, 198, 215, 233, 253, 275, 298, 323, 351, 380, 413, 448, 486, 527, 572, 620, 673, 730, 792, 859, 932, 1011, 1097, 1190, 1291, 1401, 1519, 1648, 1788, 1940, 2104, 2283, 2477, 2687, 2915, 3162]

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



