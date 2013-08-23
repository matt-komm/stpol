#!/usr/bin/env python
"""
A simple script to create one or several fully reweighed analysis histograms using tree.py
"""
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
import tree
#tree.logger.setLevel(logging.DEBUG)
from plots.common.cuts import Cuts, Weights
import networkx as nx
import argparse


def analysis_tree_all_reweighed(graph, cuts, snodes, **kwargs):
    cutnodes = []
    for cut_name, cut in cuts:
        lepton = cut_name.split("_")[0]

        cutnode = tree.CutNode(cut, graph, cut_name, snodes, [],
            filter_funcs=[
                lambda x,lepton=lepton: tree.is_samp(x, lepton)
        ])
        cutnodes.append(
            cutnode
        )

        #an extra QCD cleaning cut on top of the previous cut, which is only done in antiiso
        for syst in ["nominal", "up", "down"]:
            cn = tree.CutNode(
                Cuts.antiiso(lepton, syst) * Cuts.deltaR_QCD(),
                graph, "antiiso_%s" % syst, [cutnode], [],
                filter_funcs=[
                    lambda p: tree.is_samp(p, "antiiso")
                ]
            )
            cutnodes.append(
                cn
            )

    from histo_descs import create_plots
    create_plots(graph, cutnodes, **kwargs)

    try:
        nx.write_dot(graph, outfile.replace(".root", "_gviz.dot"))
    except Exception as e:
        logger.warning("Couldn't write .dot file for visual representation of analysis: %s" % str(e))

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

    cuts = []
    for lep in ["mu", "ele"]:
        baseline = Cuts.lepton(lep) * Cuts.hlt(lep) * Cuts.metmt(lep) * Cuts.rms_lj
        c2j1t = Cuts.n_jets(2)*Cuts.n_tags(1)
        cuts += [
            ("%s_2j1t" % lep, baseline * c2j1t),

            ("%s_2j1t_eta_lj" % lep,
                baseline * c2j1t * Cuts.eta_lj
            ),
            ("%s_2j1t_cutbased_final" % lep,
                baseline * Cuts.final(2,1)
            ),
            ("%s_2j1t_mva_loose" % lep,
                baseline * c2j1t * Cuts.mva_wp(lep)
            ),
        ]

    import cPickle as pickle
    import gzip
    class PickleSaver:
        def __init__(self, fname):
            self.of = gzip.GzipFile(fname, 'wb')

        def save(self, path, obj):
            o = obj.Clone(path)
            pickle.dump(o, self.of)

        def close(self):
            self.of.close()

    out = PickleSaver(args.outfile)
    graph = nx.DiGraph()
    snodes = [tree.SampleNode(out, graph, inf, [], []) for inf in args.infiles]
    logger.info("Done constructing sample nodes: %d" % len(snodes))


    #Construct the analysis chain
    analysis_tree_all_reweighed(
        graph, cuts, snodes,
        filter_funcs=[
        ]
    )

    print "Recursing down"
    for sn in snodes:
        sn.recurseDown()
    out.close()
