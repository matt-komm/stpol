import ROOT
from DataFormats.FWLite import Events, Handle, Lumis
import time
import numpy
import sys
import pdb

file_list = sys.argv[2:]

print file_list

events = Events(
    file_list
)

ofi = ROOT.TFile(sys.argv[1], "RECREATE")
ofi.cd()
class Histo:
    def __init__(self, src, fillfn, *args):
        self.handle = Handle(src[0])
        self.label = src[1]
        self.hist = ROOT.TH1F(*args)
        if not fillfn:
            self.fillfn = lambda x: x[0] if len(x)>0 else 0
        else:
            self.fillfn = fillfn
    def fill(self, event):
        event.getByLabel(self.label, self.handle)
        if self.handle.isValid():
            prod = self.handle.product()
            self.hist.Fill(self.fillfn(prod))

histos = []
meth = Histo(
    ("std::vector<float>", ("patMETNTupleProducer", "Pt")),
    None, "met", "met", 50, 0, 300
)
histos.append(meth)
mtweleh = Histo(
    ("double", ("eleMTW", "", "STPOLSEL2")),
    None, "ele_mtw", "ele_mtw", 50, 0, 300
)
histos.append(mtweleh)
mtwmuh = Histo(
    ("double", ("muMTW", "", "STPOLSEL2")),
    None, "mu_mtw", "mu_mtw", 50, 0, 300
)
histos.append(mtwmuh)
n_jets = Histo(
    ("int", ("goodJetCount")),
    None, "n_jets", "n_jets", 4, 0, 4
)
histos.append(n_jets)
n_tags = Histo(
    ("int", ("bJetCount")),
    None, "n_tags", "n_tags", 4, 0, 4
)
histos.append(n_tags)
cos_theta = Histo(
    ("double", ("cosTheta", "cosThetaLightJet")),
    None, "cos_theta", "cos_theta", 50, -1, 1
)

histos.append(cos_theta)

ttbar_weight = Histo(
    ("double", ("ttbarTopWeight", "weight")),
    None, "ttbar_weight", "ttbar_weight", 50, 0, 2
)
histos.append(ttbar_weight)

nEv = 0
t0 = time.time()

for event in events:
    for h in histos:
        h.fill(event)

    nEv += 1

t1 = time.time()
print "processing speed: %.2f events/sec" % (nEv / (t1-t0))

for h in histos:
    print h.hist.GetName(), h.hist.GetEntries(), h.hist.Integral(), h.hist.GetMean(), h.hist.GetRMS()
ofi.Write()
ofi.Close()
