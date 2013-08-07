import ROOT
ROOT.gROOT.SetBatch(True)
import rootpy
import re,glob
from rootpy.io import File
from rootpy.plotting import Hist
from plots.common.utils import NestedDict
from plots.common.odict import OrderedDict
from plots.common.stack_plot import plot_hists_stacked
from plots.common.utils import PhysicsProcess, merge_hists
from plots.common.sample_style import Styling
import SingleTopPolarization.Analysis.sample_types as sample_types

def load_histos(filenames):
    outdict = PatternDict()
    for fn in filenames:
        fi = File(fn)
        for root, dirs, items in fi:
            for it in items:
                k = "/".join([root, it])
                item = fi.Get(k)
                k = "/".join([fn, k.replace("__", "/").replace(".", "__")])
                outdict[k] = item
    return outdict

class PatternDict(OrderedDict):
    def __getitem__(self, k):
        pat = re.compile(k)
        ret = []
        for key in self.keys():
            m = pat.match(key)
            if not m:
                continue
            ret.append((m.groups(), dict.__getitem__(self, key)))
        return ret

def getKeysSystWeight(base, weight, vars=["up", "down"]):
    ch = []
    for k in (["nominal"]+vars):
        c = "__".join([weight, k])
        ch.append(c)
    return tuple([base.replace(ch[0], c) for c in ch])

if __name__=="__main__":
    mcs = (
        glob.glob("hists/step3_latest/mu/mc/iso/nominal/Jul15/*.root") +
        glob.glob("hists/step3_latest/mu/data/iso/Jul15/*.root")
    )

    r = load_histos(mcs)
    print len(r.keys())

    key = (
        ".*/(.*)\.root/" + 
        "CHANNEL__mu/NJETS__2J/NTAGS__1T/MET__mtw__40/" +
        "PU__nominal/BTAG__nominal/WJETS__yield__nominal/" +
        "WJETS__shape__nominal/VARS__eta_lj__full/.*"
    )

    key_systs = (
        ".*/(.*)\.root/" + 
        "CHANNEL__mu/NJETS__2J/NTAGS__1T/MET__mtw__40/" +
        "PU__nominal/BTAG__nominal/WJETS__yield__nominal/" +
        "WJETS__shape__nominal/VARS__eta_lj__full/.*"
    )
    key_data = (
        "hists/step3_latest/mu/data/iso/.*/(.*)\.root/" + 
        "CHANNEL__mu/NJETS__2J/NTAGS__1T/MET__mtw__40/" +
        "PU__nominal/BTAG__nominal/WJETS__yield__nominal/" +
        "WJETS__shape__nominal/VARS__eta_lj__full/.*"
    )

    hdata = r[key_data]
    print "hdata = ", len(hdata)
    keys = [key]

    processes = PhysicsProcess.get_proc_dict("mu")
    merge_cmds = PhysicsProcess.get_merge_dict(processes)
    
    print merge_cmds
    for key in keys:
        mats = r[key]+hdata
        hists = dict()
        for ((samp,), hist) in mats:
            hists[samp] = hist
            if sample_types.is_mc(samp):
                Styling.mc_style(hist, samp)
            else:
                Styling.data_style(hist)
        merged = merge_hists(hists, merge_cmds)
        stacks_d = dict()
        stacks_d['data'] = [merged.pop('data')]
        stacks_d['mc'] = merged.values()

        for hi in stacks_d['mc']:
            hi.Scale(18600)

        c = ROOT.TCanvas()
        stacks = plot_hists_stacked(c, stacks_d)
        c.SaveAs("test.pdf")


import unittest
class Test(unittest.TestCase):
    def testLoad(self):
        mcs = glob.glob("hists/step3_latest/mu/mc/iso/nominal/Jul15/*.root")[0:2]
        r = load_histos(mcs)
        mats = r[".*/(.*)\.root/CHANNEL__mu/NJETS__(.*)/NTAGS__1T/MET__mtw__40/PU__nominal/BTAG__nominal/WJETS__yield__nominal/WJETS__shape__nominal/VARS__eta_lj__full/.*"]
        for k, v in mats:
            assert(isinstance(v, ROOT.TH1F))

    def testWeightSysts(self):
        k = ".*/(.*)\.root/CHANNEL__mu/NJETS__(.*)/NTAGS__1T/MET__mtw__40/PU__nominal/BTAG__nominal/WJETS__yield__nominal/WJETS__shape__nominal/VARS__eta_lj__full/.*"
        k1 = getKeysSystWeight(k, "PU")
        self.assertEqual(k1[0], k.replace("PU__nominal", "PU__nominal"))
        self.assertEqual(k1[1], k.replace("PU__nominal", "PU__up"))
        self.assertEqual(k1[2], k.replace("PU__nominal", "PU__down"))

        k1 = getKeysSystWeight(k, "BTAG", vars=["BC__up", "BC__down"])
        self.assertEqual(k1[0], k.replace("BTAG__nominal", "BTAG__nominal"))
        self.assertEqual(k1[1], k.replace("BTAG__nominal", "BTAG__BC__up"))
        self.assertEqual(k1[2], k.replace("BTAG__nominal", "BTAG__BC__down"))