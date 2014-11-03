import ROOT, sys

inf = sys.argv[1]
tn = sys.argv[2]
f = ROOT.TFile(inf)

t = f.Get(tn)
print("%s = %d" % (inf, int(t.GetEntries())))
