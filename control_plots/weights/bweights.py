from plots.common.sample import get_paths, Sample
from plots.common.utils import NestedDict
from plots.common.cuts import Cuts
from plots.common.cross_sections import lumi_iso
from plots.common.utils import merge_hists
from plots.common.histogram import HistCollection
from plots.common.hist_plots import plot_hists

import logging
if __name__=="__main__":
	logging.basicConfig(level=logging.INFO)
	basepath = get_paths(samples_dir="data/83a02e9_Jul22_sftotal/", dataset="latest")
	sampnames = ["TTJets_FullLept", "TTJets_SemiLept", "T_t_ToLeptons", "Tbar_t_ToLeptons"]
	path = basepath["mc"]["mu"]["nominal"]["iso"]

	cut = Cuts.final(2,1)*Cuts.mu
	var = "cos_theta"
	plot_range=[50, -1, 1]
	lumi = lumi_iso["mu"]


	weights = [
	    ("unw", "1.0"),
	    ("nom", "b_weight_nominal"),
	    ("bc_up", "b_weight_nominal_BCup"),
	    ("bc_down", "b_weight_nominal_BCdown"),
	    ("l_up", "b_weight_nominal_Lup"),
	    ("l_down", "b_weight_nominal_Ldown"),
	]
	hists = NestedDict()

	merge_cmds = {
		"ttbar": ["TTJets_.*"],
		"tchan": [".*_ToLeptons"]
	}

	recreate=False
	if recreate:
		for sn in sampnames:
			sample = Sample.fromFile(path + "/" + sn + ".root")

			for wn, w in weights:
				hi = sample.drawHistogram(var, str(cut), weight_str=w, plot_range=plot_range)
				hi.Scale(sample.lumiScaleFactor(lumi))
				hists[wn][sample.name] = hi

		
		merged = dict()
		for wn, w in weights:
			merged[wn] = merge_hists(hists[wn], merge_cmds)
			hc = HistCollection(merged[wn], name="bweight_%s" % wn)
			hc.save(".")

	colls = dict()
	for wn, w in weights:
		hc = HistCollection.load("./bweight_%s.root" % wn)
		colls[wn] = hc


	for proc in merge_cmds.keys():
		hists = dict([(wn, colls[wn].hists[proc]) for wn, w in weights])
		plot_hists_dict(hists)



