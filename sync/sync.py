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

def get_ids(fn):
    return set(map(int, open(fn)))
def compare(fna, fnb):
    id_a,id_b = get_ids(fna), get_ids(fnb)
    print "A: ", len(id_a), " B: ", len(id_b)
    common = id_a.intersection(id_b)
    difa = id_a.difference(id_b)
    difb = id_b.difference(id_a)

    if len(difa)>0:
        print "difa ", list(difa)[0:3]
    if len(difb)>0:
        print "difb ", list(difb)[0:3]

    print "A&B: ", len(common), "| A!B: ", len(difa),"| B!A: ", len(difb)

def cutflow(basename, channel):
    idname = basename + "/" + channel

    filename="%s/step3.root" % basename
    samp = ROOT.TFile(filename)
    tree = samp.Get("trees/Events")
    vals = []

    if channel=="mu":
        cut = Cuts.hlt_isomu
        vals.append(tree.GetEntries(str(cut)))
        cut = cut * Cut("n_muons==1&&n_eles==0")
        vals.append(tree.GetEntries(str(cut)))
    elif channel=="ele":
        cut = Cuts.hlt_isoele
        vals.append(tree.GetEntries(str(cut)))
        cut = cut * Cut("n_eles==1&&n_muons==0")
        vals.append(tree.GetEntries(str(cut)))

    save_ids(idname + "/events_lepton.txt", get_event_ids(tree, str(cut)))

    cut = cut * Cut("n_veto_mu==0")
    vals.append(tree.GetEntries(str(cut)))

    cut = cut * Cut("n_veto_ele==0")
    cut_aftermu = copy.deepcopy(cut)
    vals.append(tree.GetEntries(str(cut)))

    save_ids(idname + "/events_vetolep.txt", get_event_ids(tree, str(cut)))
    cut = cut * Cut("n_jets==2")
    vals.append(tree.GetEntries(str(cut)))
    save_ids(idname + "/events_2J.txt", get_event_ids(tree, str(cut)))

    if channel=="mu":
        cut = cut * Cut("mt_mu>=40")
        vals.append(tree.GetEntries(str(cut)))
    elif channel=="ele":
        cut = cut * Cut("met>=35")
        vals.append(tree.GetEntries(str(cut)))
    save_ids(idname + "/events_METMTW.txt", get_event_ids(tree, str(cut)))

    cut = cut * Cut("n_tags==1")
    vals.append(tree.GetEntries(str(cut)))
    save_ids(idname + "/events_1T.txt", get_event_ids(tree, str(cut)))

    vals = map(str, vals)
    return "| NICPB, JP | " + " | ".join(vals) + " | "

if __name__=="__main__":
    print "mu"
    print "exclusive: ", cutflow("exclusive", "mu")
    print "inclusive: ", cutflow("inclusive", "mu")

    print "exclusive mu"
    compare("exclusive/mu/events_2J.txt", "matthias_events/sync_muon_exlusive_2jets.txt")
    compare("exclusive/mu/events_METMTW.txt", "matthias_events/sync_muon_exlusive_mtw.txt")
    compare("exclusive/mu/events_1T.txt", "matthias_events/sync_muon_exlusive_1btag.txt")

    print "inclusive mu"
    compare("inclusive/mu/events_2J.txt", "matthias_events/sync_muon_inclusive_2jets.txt")
    compare("inclusive/mu/events_METMTW.txt", "matthias_events/sync_muon_inclusive_mtw.txt")
    compare("inclusive/mu/events_1T.txt", "matthias_events/sync_muon_inclusive_1btag.txt")

    print "ele"
    print "exclusive: ", cutflow("exclusive", "ele")
    print "inclusive: ", cutflow("inclusive", "ele")
    compare("inclusive/ele/events_lepton.txt", "matthias_events/sync_ele_inc.txt")



