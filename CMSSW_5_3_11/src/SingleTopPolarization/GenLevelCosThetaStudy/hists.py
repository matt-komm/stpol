#!/usr/bin/env python
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
        self.hist.Sumw2()
        if not fillfn:
            self.fillfn = lambda x: x[0] if len(x)>0 else 0
        else:
            self.fillfn = fillfn
        self.weight_handle = None
        self.weight_label = None
    def fill(self, event):
        try:
            event.getByLabel(self.label, self.handle)
            if self.weight_handle:
                event.getByLabel(self.weight_label, self.weight_handle)

            if self.handle.isValid():
                prod = self.handle.product()
                if self.weight_handle and self.weight_handle.isValid():
                    w = self.weight_handle.product()[0]
                else:
                    w = 1.0
                self.hist.Fill(self.fillfn(prod), w)
        except ValueError as e:
            print "Error while filling histogram: ", self.label, " ", str(e)
            sys.exit(1)

histos = []
bjet_pt = Histo(
    ("std::vector<float>", ("btaggedJet", "Pt")),
    None, "bjet_pt", "bjet_pt", 60, 0, 300
)
histos.append(bjet_pt)

ljet_pt = Histo(
    ("std::vector<float>", ("lightJet", "Pt")),
    None, "ljet_pt", "ljet_pt", 60, 0, 300
)
histos.append(ljet_pt)

bjet_eta = Histo(
    ("std::vector<float>", ("btaggedJet", "Eta")),
    None, "bjet_eta", "bjet_eta", 60, -4.5, 4.5
)
histos.append(bjet_eta)

ljet_eta = Histo(
    ("std::vector<float>", ("lightJet", "Eta")),
    None, "ljet_eta", "ljet_eta", 60, -4.5, 4.5
)
histos.append(ljet_eta)

#mtweleh = Histo(
#    ("double", ("eleMTW", "", "STPOLSEL2")),
#    None, "ele_mtw", "ele_mtw", 50, 0, 300
#)
#histos.append(mtweleh)
#mtwmuh = Histo(
#    ("double", ("muMTW", "", "STPOLSEL2")),
#    None, "mu_mtw", "mu_mtw", 50, 0, 300
#)
#histos.append(mtwmuh)
#n_jets = Histo(
#    ("int", ("goodJetCount")),
#    None, "n_jets", "n_jets", 4, 0, 4
#)
#histos.append(n_jets)
#n_tags = Histo(
#    ("int", ("bJetCount")),
#    None, "n_tags", "n_tags", 4, 0, 4
#)

#histos.append(n_tags)
cos_theta = Histo(
    ("double", ("cosTheta", "cosThetaLightJet")),
    None, "cos_theta", "cos_theta", 60, -1, 1
)
histos.append(cos_theta)

gen_weight = Histo(
    ("double", ("particleSelector", "genWeight")),
    None, "gen_weight", "gen_weight", 60, 0, 1
)
histos.append(gen_weight)

cos_theta_weighted = Histo(
    ("double", ("cosTheta", "cosThetaLightJet")),
    None, "cos_theta_weighted", "cos_theta_weighted", 60, -1, 1
)
cos_theta_weighted.weight_handle = Handle("double")
cos_theta_weighted.weight_label = ("particleSelector", "genWeight")
histos.append(cos_theta_weighted)

#ttbar_weight = Histo(
#    ("double", ("ttbarTopWeight", "weight")),
#    None, "ttbar_weight", "ttbar_weight", 50, 0, 2
#)
#histos.append(ttbar_weight)

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
