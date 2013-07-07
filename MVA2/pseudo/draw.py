import ROOT

tfile = ROOT.TFile('data.root')
ttree = tfile.Get("trees/Events")

ht = ROOT.TH1F('AAA', 'Title?', 20, -5, 5)
ttree.Draw('x >> AAA')
ht.Draw()
