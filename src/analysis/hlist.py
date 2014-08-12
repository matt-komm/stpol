import ROOT,sys
f = ROOT.TFile(sys.argv[1])

ks = [k for k in f.GetListOfKeys()]
sks = sorted(ks, key=lambda x: x.GetName())

for k in sks:
    o = k.ReadObj()
    i = o.Integral()
    if i < 1:
        i = int(round(20000 * i))
    print k.GetName(), i, int(o.GetEntries())
