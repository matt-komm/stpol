import ROOT
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
import pdb

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
    hfiles = (
        glob.glob("hists/hdfs/local/stpol/step3/Aug4_0eb863_full/mu/mc/iso/nominal/Jul15/*.root") +
        glob.glob("hists/hdfs/local/stpol/step3/Aug4_0eb863_full/mu/data/iso/Jul15/*.root") +
        glob.glob("hists/hdfs/local/stpol/step3/Aug4_0eb863_full/mu/data/iso/Aug1/*.root")
    )

    r = load_histos(hfiles)
    print len(r.keys())

    cut = "CHANNEL__mu/NJETS__2J/NTAGS__1T/MET__mtw__40/"
    weight = "PU__nominal/BTAG__nominal/WJETS__yield__nominal/WJETS__shape__nominal/"
    var = "VARS__eta_lj__full/"
    key = (
        "hists/step3_latest/mu/mc/iso/nominal/.*/(.*)\.root/" + 
        cut +
        weight +
        var + ".*"
    )

    key_data = (
        "hists/step3_latest/mu/data/iso/.*/(.*)\.root/" + 
        cut +
        weight +
        var + ".*"
    )

    hdata = r[key_data]
    print "hdata = ", len(hdata)
    keys_s1 = getKeysSystWeight(
        key, "BTAG", vars=["BC__up", "BC__down"]
    )
    keys = [
        ("nominal", [key]),
        ("BTAG_BC", [keys_s1[1], keys_s1[2]]) 
    ]
    
    processes = PhysicsProcess.get_proc_dict("mu")
    merge_cmds = PhysicsProcess.get_merge_dict(processes)

    stacks_syst = []
    mc_nominal = None
    for name, _keys in keys:
        mcs = []
        for key in _keys:
            mats = r[key]
            hists = dict()
            for ((samp,), hist) in mats:
                hists[samp] = hist
                Styling.mc_style(hist, samp)
            merged = merge_hists(hists, merge_cmds)
            hists = merged.values()
            for hi in hists:
                hi.Scale(18600)
            mcs.append(*hists)
        if name=="nominal" and len(mcs)==1:
            mc_nominal = mcs

        stacks_syst.append((name, mcs))

    tot_nominal = sum(mc_nominal)

    from SingleTopPolarization.Analysis import systematics
    tot_up, tot_down = systematics.total_syst(
        tot_nominal,
        stacks_syst[1:]
    )

    from plots.common.hist_plots import plot_hists
    canv = plot_hists([tot_nominal, tot_up, tot_down])
    for i in [tot_nominal, tot_up, tot_down]:
        print list(i.y())

    #from rootpy.interactive import wait
    #import rootpy.plotting.root2matplotlib as rplt
    #import matplotlib.pyplot as plt
    #from matplotlib.ticker import AutoMinorLocator, MultipleLocator

    # plot with matplotlib
    # fig = plt.figure(figsize=(7, 5), dpi=100, facecolor='white')
    # axes = plt.axes([0.15, 0.15, 0.8, 0.8])
#    axes.xaxis.set_minor_locator(AutoMinorLocator())
#    axes.yaxis.set_minor_locator(AutoMinorLocator())
#    axes.yaxis.set_major_locator(MultipleLocator(20))
#    axes.tick_params(which='major', labelsize=15, length=8)
#    axes.tick_params(which='minor', length=4)
    # rplt.bar(tot_nominal, axes=axes, fill=False)
    # rplt.bar(tot_up, axes=axes, fill=False, color='b')
    # rplt.bar(tot_down, axes=axes, fill=False, color='g')
    # rplt.errorbar(h3, xerr=False, emptybins=False, axes=axes)
    # plt.xlabel('Mass', position=(1., 0.), ha='right', size=16)
    # plt.ylabel('Events', position=(0., 1.), va='top', size=16)
    # axes.xaxis.set_label_coords(1., -0.12)
    # axes.yaxis.set_label_coords(-0.12, 1.)
    # axes.set_ylim(0, plot_max)
    # leg = plt.legend(numpoints=1)
    # frame = leg.get_frame()
    # frame.set_fill(False)
    # frame.set_linewidth(0)
    # axes.text(0.3, 0.8, 'matplotlib',
    #         verticalalignment='center', horizontalalignment='center',
    #         transform=axes.transAxes, fontsize=20)

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