import ROOT
import copy
from plots.common.cuts import Cuts, Cut
import root_numpy
import sys

def get_event_ids(tree, cut):
    arr = root_numpy.tree2rec(tree, branches=["event_id"], selection=cut)["event_id"]
    arr.sort()
    return arr
def save_ids(filename, ids):
    f = open(filename, "w")
    for _id in ids:
        f.write(str(_id))
        f.write("\n")
    f.close()

basename = sys.argv[1]
channel=sys.argv[2]
idname = basename + "/" + channel

filename="%s/step3.root" % basename
samp = ROOT.TFile(filename)
tree = samp.Get("trees/Events")
vals = []

if channel=="mu":
    cut = Cuts.hlt_isomu
    vals.append(tree.GetEntries(str(cut)))
    cut = cut * Cut("n_muons==1")
    vals.append(tree.GetEntries(str(cut)))
elif channel=="ele":
    cut = Cuts.hlt_isoele
    vals.append(tree.GetEntries(str(cut)))
    cut = cut * Cut("n_eles==1")
    vals.append(tree.GetEntries(str(cut)))

cut = cut * Cut("n_veto_mu==0")
vals.append(tree.GetEntries(str(cut)))

cut = cut * Cut("n_veto_ele==0")
cut_aftermu = copy.deepcopy(cut)
vals.append(tree.GetEntries(str(cut)))

save_ids(idname + "/events_lepton.txt", get_event_ids(tree, str(cut)))
cut = cut * Cut("n_jets==2")
vals.append(tree.GetEntries(str(cut)))
save_ids(idname + "/events_2J.txt", get_event_ids(tree, str(cut)))

if channel=="mu":
    cut = cut * Cut("mt_mu>=45")
    vals.append(tree.GetEntries(str(cut)))
elif channel=="ele":
    cut = cut * Cut("met>=35")
    vals.append(tree.GetEntries(str(cut)))
save_ids(idname + "/events_METMTW.txt", get_event_ids(tree, str(cut)))

cut = cut * Cut("n_tags==1")
vals.append(tree.GetEntries(str(cut)))
save_ids(idname + "/events_1T.txt", get_event_ids(tree, str(cut)))

vals = map(str, vals)
print "| NICPB, JP | " + " | ".join(vals) + " | "
