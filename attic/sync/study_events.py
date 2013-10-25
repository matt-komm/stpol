import ROOT
from plots.common.cuts import Cuts, Cut
from root_numpy import tree2rec

f = ROOT.TFile("exclusive/step3.root")

tree = f.Get("trees/Events")

interesting = [
    1798880,
    1808687,
    1838545
]

#interesting = [1837809]
for ev in tree:
    if ev.event_id in interesting:
        print "id =",ev.event_id, " pt =",ev.mu_pt, " iso =",ev.mu_iso, " eta =",ev.mu_eta

print "all events"
arr = tree2rec(tree, branches=["event_id"])
for i in interesting:
    if i in arr["event_id"]:
        print "%d is in tree" % i


print "HLT selection"
arr = tree2rec(tree, branches=["event_id"], selection=str(Cuts.hlt_isomu))
for i in interesting:
    if i in arr["event_id"]:
        print "%d passes HLT" % i
