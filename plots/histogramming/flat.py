#!/usr/bin/env python
"""
A simple example how to make a histogram using the current tree.py framework.
"""

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

import tree
from plots.common.cuts import Cuts, Weights
import networkx as nx
import argparse


def analysis_tree(cuts, weights, variables, infiles, outfile):
    out = tree.ObjectSaver(outfile)

    graph = nx.DiGraph()

    snodes = [tree.SampleNode(out, graph, inf, [], []) for inf in infiles]

    logger.info("Done constructing sample nodes: %d" % len(snodes))

    for cut in cuts:
        histnode = tree.hist_node(graph, cut, weights, variables)
        histnode.addParents(snodes)

    tree.HistNode.logger.setLevel(logging.INFO)
    
    try:
        nx.write_dot(graph, outfile.replace(".root", "_gviz.dot"))
    except Exception as e:
        logger.warning("Couldn't write .dot file for visual representation of analysis: %s" % str(e))
    return snodes, out


if __name__=="__main__":

    parser = argparse.ArgumentParser(
        description='Produces a hierarchy of histograms corresponding to cuts and weights.'
    )

    parser.add_argument('outfile', action='store',
        help="The output file name."
    )

    parser.add_argument('infiles', nargs='+',
        help="The input file names"
    )
    args = parser.parse_args()

    import ROOT

    #Define all the variables that we want to see
    variables = [
        ("cos_theta", "cos_theta", [20, -1, 1]),

        #Demonstrate some weird binning
        ("cos_theta_binned", "cos_theta", [-1, -0.4674, -0.2558, -0.1028, 0.0, 0.116, 0.2126, 0.2956, 0.379, 0.4568, 0.5302, 0.6038, 0.6822, 0.7694, 1]),
        
        #ROOT functions can be used
        ("abs_eta_lj", "abs(eta_lj)", [20, 0, 5]),

        ("bdt", Cuts.mva_vars['mu'], [60, -1, 1]),
    ]

    #Define all the weight strategies that we want to apply
    weights = [
        ("weight__nominal", Weights.total_weight("mu")),

        #Demonstrate reweighting
        ("weight__puw", Weights.pu("nominal")),
        ("weight__puw_up", Weights.pu("up")),
    ]

    #All the cut regions that we are interested in
    cuts = [
        ("2j0t", Cuts.mt_mu()*Cuts.n_jets(2)*Cuts.n_tags(0)*Cuts.lepton("mu")*Cuts.hlt("mu")),
        ("2j1t", Cuts.mt_mu()*Cuts.n_jets(2)*Cuts.n_tags(1)*Cuts.lepton("mu")*Cuts.hlt("mu")),
        ("final_cb_2j1t", Cuts.final(2,1))
    ]

    #Construct the analysis chain
    snodes, out = analysis_tree(cuts, weights, variables, args.infiles, args.outfile)

    print "Recursing down"
    for sn in snodes:
        sn.recurseDown()

    out.tfile.close()