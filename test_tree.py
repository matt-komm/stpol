from SingleTopPolarization.Analysis import tree
from plots.common.cuts import Cuts, Weights
import logging
import plots.common.sample as sample
from plots.common.utils import PatternDict

import rootpy.plotting.root2matplotlib as rplt
import matplotlib.pyplot as plt
plt.rc('font', **{'family':'sans','sans-serif':['Arial']})
plt.rc('text', usetex=True)

import ROOT

#sample.logger.setLevel(logging.DEBUG)

def hist_err(axes, hist, **kwargs):
    return axes.errorbar(
        list(hist.x()),
        list(hist.y()),
        yerr=[list(hist.yerrh()),
        list(hist.yerrl())],
        drawstyle='steps-mid', **kwargs
    )

def hist_node(hist_desc, _cut, _weight):
    cut_name, cut = _cut
    weight_name, weight = _weight
    cutnode = tree.CutNode(cut, cut_name, [], [])
    weightnode = tree.WeightNode(weight, weight_name, [cutnode], [])
    histnode = tree.HistNode(hist_desc, hist_desc["name"], [weightnode], [])
    return cutnode


if __name__=="__main__":
    class DictSaver(PatternDict):
        def save(self, path, obj):
            self[path] = obj

    outd = DictSaver()

    top = tree.Node("top", [], [])

    snodes = []
    for samp in ["TTJets_FullLept.root", "TTJets_SemiLept.root"]:
        snodes.append(
            tree.SampleNode(
                outd,
                "data/Aug4_0eb863_full/mu/mc/iso/nominal/Jul15/%s" % samp,
                [top], []
            )
        )

    v = {
        "name": "met_phi",
        "var": "phi_met",
        "binning": [40, -1, 1]
        }
    w = ("w_nominal", Weights.total_weight("mu"))
    cos_theta1 = hist_node(
        v,
        ("cb_final_2j1t", Cuts.final(2,1, "mu")),
        w
    )
    cos_theta2 = hist_node(
        v,
        ("cb_final_2j0t", Cuts.final(2,0, "mu")),
        w
    )
    
    cos_theta1.addParents(top.children)
    cos_theta2.addParents(top.children)

    for snode in snodes:
        snode.recurseDown(snode)