import ROOT,sys
f = ROOT.TFile(sys.argv[1])

ks = [k for k in f.GetListOfKeys()]
sks = sorted(ks, key=lambda x: x.GetName())

for k in sks:
    o = k.ReadObj()
    i = o.Integral()
    if i < 1:
        i = int(round(20000 * i))
    nom_name = "__".join(k.GetName().split("__")[0:2])
    nom = f.Get(nom_name)
#    if nom and not nom.IsZombie():
#        chi2 = nom.Chi2Test(o, "WW CHI2/NDF")
#    else:
#        chi2 = "NA"
    print k.GetName(), o.GetNbinsX(), "I=", i, "E=", int(o.GetEntries())
