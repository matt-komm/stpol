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
import ROOT


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

    # try:
    #     nx.write_dot(graph, outfile.replace(".root", "_gviz.dot"))
    # except Exception as e:
    #     logger.warning("Couldn't write .dot file for visual representation of analysis: %s" % str(e))

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

    cuts_jet_tag = [
        ("%dj%dt"%(n,m), Cuts.n_jets(n)*Cuts.n_tags(m)) for n in [2,3] for m in [0,1,2]
    ]
    # cuts_jet_tag = [
    #     ("2j1t", Cuts.n_jets(2)*Cuts.n_tags(1))
    # ]

    cuts = []
    for cutname, cbline in cuts_jet_tag:
        for lep in ["mu", "ele"]:
            cn = "%s_%s" % (lep, cutname)
            baseline = Cuts.lepton(lep) * Cuts.hlt(lep) * Cuts.metmt(lep) * Cuts.rms_lj
            cuts += [
                #Without the MET cut
                ("%s_nomet" % cn, Cuts.lepton(lep) * Cuts.hlt(lep) * Cuts.rms_lj * cbline),

                #Baseline for fit
                ("%s_baseline" % cn, baseline * cbline),

                #Cut-based check
                ("%s_cutbased_final" % cn,
                    baseline * cbline * Cuts.top_mass_sig * Cuts.eta_lj
                ),

                #MVA-based selection
                ("%s_mva_loose" % cn,
                    baseline * cbline * Cuts.mva_wp(lep)
                ),
            ]
            #MVA scan
           # for mva in numpy.linspace(0, 0.8, 9):
           #     cuts.append(
           #         ("%s_mva_scan_%s" % (cn, str(mva).replace(".","_")),
           #             baseline * cbline * Cuts.mva_wp(lep, mva)
           #         ),
           #     )

    import cPickle as pickle
    import gzip
    class PickleSaver:
        def __init__(self, fname):
            self.of = gzip.GzipFile(fname, 'wb')
            self.of_list = open(fname+".header", 'wb')
            self.nhists = 0

        def save(self, path, obj):
            self.of_list.write(path + "\n")
            obj.SetName(path)
            pickle.dump(obj, self.of)
            self.nhists += 1

        def close(self):
            self.of.close()
            self.of_list.close()


    class FlatROOTSaver:
        def __init__(self, fname):
            self.of = ROOT.TFile(fname, "RECREATE")
            self.nhists = 0

        def save(self, path, obj):
            obj.SetName(path.replace("/", "___"))
            self.of.cd()
            obj.Write("", ROOT.TObject.kOverwrite)
            self.nhists += 1

        def close(self):
            self.of.Close()

    out = FlatROOTSaver(args.outfile)
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
