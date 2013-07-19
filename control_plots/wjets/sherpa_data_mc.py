from plot_utils import *
from plots.common.tdrstyle import *
from plots.common.sample import *
from SingleTopPolarization.Analysis import sample_types
from plots.common.cuts import *
from plots.common.odict import *

LUMI_TOTAL = 20000
if __name__=="__main__":
	logging.basicConfig(level=logging.ERROR)
	tdrstyle()
	logger.setLevel(level=logging.INFO)
	logging.getLogger("utils").setLevel(logging.INFO)
	ROOT.gStyle.SetOptTitle(True)

	import argparse

	parser = argparse.ArgumentParser(description='Draw WJets sherpa plots')
	parser.add_argument('--recreate', dest='recreate', action='store_true')
	parser.add_argument('--tag', type=str, default="test")
	parser.add_argument('--outdir', type=str, default=".")
	args = parser.parse_args()
	mkdir_p(args.outdir)

	if args.recreate:
	    samples = load_samples(os.environ["STPOL_DIR"])
	    for s in samples.values():
	        if sample_types.is_wjets(s.name):
	            s.tree.AddFriend("trees/WJets_weights", s.tfile)

	else:
	    samples = {}


	coll1 = data_mc("n_tags", "2J", Cuts.final_jet(2), Weights.total("nominal"), samples.values(), args.outdir, args.recreate, LUMI_TOTAL, plot_range=[3, 0, 3])
	Styling.style_collection(coll1)

	merges = dict()
	merges["madgraph"] = copy.deepcopy(merge_cmds)
	merges["madgraph"]["WJets (mg)"] = copy.deepcopy(merges["madgraph"]["WJets"])
	merges["madgraph"].pop("WJets")
	merges["sherpa"] = copy.deepcopy(merge_cmds)
	merges["sherpa"].pop("WJets")
	merges["sherpa"]["WJets (sh)"] = ["WJets_sherpa_nominal"]

	hmerged = merge_hists(coll1.hists, merges["madgraph"])
	coll2 = HistCollection(hmerged, name="merged_mg")
	canv = ROOT.TCanvas()
	plot(canv, "2J_mg", coll2.hists, args.outdir, do_log_y=True, min_bin=1, x_label="N_{tags}")

	hmerged = merge_hists(coll1.hists, merges["sherpa"])
	coll3 = HistCollection(hmerged, name="merged_sh")
	canv = ROOT.TCanvas()
	plot(canv, "2J_sh", coll3.hists, args.outdir, do_log_y=True, min_bin=1, x_label="N_{tags}")

	coll1 = data_mc("n_tags", "3J", Cuts.final_jet(3), Weights.total("nominal"), samples.values(), args.outdir, args.recreate, LUMI_TOTAL, plot_range=[4, 0, 4])
	Styling.style_collection(coll1)

	hmerged = merge_hists(coll1.hists, merges["madgraph"])
	coll2 = HistCollection(hmerged, name="merged_mg")
	canv = ROOT.TCanvas()
	plot(canv, "3J_mg", coll2.hists, args.outdir, do_log_y=True, min_bin=1, x_label="N_{tags}")

	hmerged = merge_hists(coll1.hists, merges["sherpa"])
	coll3 = HistCollection(hmerged, name="merged_sh")
	canv = ROOT.TCanvas()
	plot(canv, "3J_sh", coll3.hists, args.outdir, do_log_y=True, min_bin=1, x_label="N_{tags}")