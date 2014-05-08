#!/usr/bin/env python
"""
Creates the necessary histograms for studying the met-phi modulation
"""
import logging
logging.basicConfig(level=logging.INFO)

from SingleTopPolarization.Analysis import tree
from plots.common.cuts import Cuts, Weights
import plots.common.sample as sample
from plots.common.utils import PatternDict, PhysicsProcess

from plots.common.hist_plots import hist_err
import rootpy.plotting.root2matplotlib as rplt
import matplotlib.pyplot as plt
import networkx as nx

plt.rc('font', **{'family':'sans','sans-serif':['Arial']})
plt.rc('text', usetex=True)

import ROOT

if __name__=="__main__":
    class DictSaver(PatternDict):
        def save(self, path, obj):
            self[path] = obj

    outd = DictSaver()


    graph = nx.DiGraph()
    top = tree.Node(graph, "top", [], [])

    datadirs = [
        "data/Aug4_0eb863_full/mu",
        #"/hdfs/local/stpol/step3/Jul26_MVA_multivar_v1/mu"
    ]

    sample_fnames = []
    processes = [
        PhysicsProcess.WJets_mg_exc,
        PhysicsProcess.TTJets_exc,
        PhysicsProcess.tchan
    ]

    print "Constructing sample nodes"
    for d in datadirs:
        for proc in processes:
            sample_fnames += proc.getFiles(d + "/mc/iso/nominal/Jul15")
        sample_fnames += PhysicsProcess.SingleMu.getFiles(d + "/data/iso")

    snodes = tree.sample_nodes(graph, sample_fnames, outd, top)
    print "Done constructing sample nodes"
    variables = {}
    variables["met_phi"] = {
        "name": "met_phi",
        "var": "phi_met",
        "binning": [20, -3.14, 3.14]
    }
    variables["cos_theta"] = {
        "name": "cos_theta",
        "var": "cos_theta",
        "binning": [20, -1, 1]
    }
    variables["bdt"] = {
        "name": "bdt",
        "var": Cuts.mva_vars['mu'],
        "binning": [60, -1, 1]
    }

    weights = [
        ("weight__nominal", Weights.total_weight("mu")),
    ]


    c1 = (
        "2j0t",
        Cuts.mt_mu()*Cuts.n_jets(2)*Cuts.n_tags(0)*Cuts.lepton("mu")*Cuts.hlt("mu"),
    )
    c2 = (
        "2j1t",
        Cuts.mt_mu()*Cuts.n_jets(2)*Cuts.n_tags(1)*Cuts.lepton("mu")*Cuts.hlt("mu"),
    )
    c3 = (
        "final_cb_2j1t",
        Cuts.final(2,1),
    )
    cuts = [c1, c2, c3]

    varnodes = {}
    for k, v in variables.items():
        for c in cuts:
            vn = tree.hist_node(graph, v, c, weights)
            vn.addParents(top.children())

    tree.HistNode.logger.setLevel(logging.INFO)
    print "Recursing down"
    for snode in snodes:
        snode.recurseDown()
