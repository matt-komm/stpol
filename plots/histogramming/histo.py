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
import numpy


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

    cut_jet_tag = Cuts.n_jets(2)*Cuts.n_tags(1)

    cuts = []
    for lep in ["mu", "ele"]:
        baseline = Cuts.lepton(lep) * Cuts.hlt(lep) * Cuts.metmt(lep) * Cuts.rms_lj
        cuts += [
            #Without the MET cut
            ("%s_2j1t_nomet" % lep, Cuts.lepton(lep) * Cuts.hlt(lep) * Cuts.rms_lj * cut_jet_tag),

            #Baseline for fit
            ("%s_2j1t_baseline" % lep, baseline * cut_jet_tag),
            #("%s_2j1t_eta_lj" % lep,
            #    baseline * cut_jet_tag * Cuts.eta_lj
            #),

            #Cut-based check
            ("%s_2j1t_cutbased_final" % lep,
                baseline * cut_jet_tag * Cuts.top_mass_sig * Cuts.eta_lj
            ),

            #MVA-based selection
            ("%s_2j1t_mva_loose" % lep,
                baseline * cut_jet_tag * Cuts.mva_wp(lep)
            ),
        ]
        #MVA scan
        for mva in numpy.linspace(0, 0.8, 9):
            cuts.append(
                ("%s_2j1t_mva_scan_%s" % (lep, str(mva).replace(".","_")),
                    baseline * cut_jet_tag * Cuts.mva_wp(lep, mva)
                ),
            )

    import cPickle as pickle
    import gzip
    class PickleSaver:
        def __init__(self, fname):
            self.of = gzip.GzipFile(fname, 'wb')
            self.nhists = 0

        def save(self, path, obj):
            pickle.dump(obj, self.of)
            self.nhists += 1

        def close(self):
            self.of.close()

    out = PickleSaver(args.outfile)
    graph = nx.DiGraph()
    snodes = [tree.SampleNode(out, graph, inf, [], []) for inf in args.infiles]
    logger.info("Done constructing sample nodes: %d" % len(snodes))


    #Construct the analysis chain
    analysis_tree_all_reweighed(graph, cuts, snodes)

    import time
    t0 = time.time()
    for sn in snodes:
        sn.recurseDown()
    t1 = time.time()
    out.close()
    nevents = sum([sn.sample.getEventCount() for sn in snodes])
    logger.info("STATS %d events, %d histograms, %d seconds" % (nevents, out.nhists, t1-t0))
