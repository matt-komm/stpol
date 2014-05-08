from plots.common.sample import get_paths, Sample
from plots.common.utils import NestedDict
from plots.common.cuts import Cuts
from plots.common.cross_sections import lumi_iso
from plots.common.utils import merge_hists
from plots.common.histogram import HistCollection, norm
from plots.common.hist_plots import plot_hists_dict
import numpy, copy
from plots.common.odict import OrderedDict
from plots.common.tdrstyle import tdrstyle

import logging
if __name__=="__main__":

	tdrstyle()

	logging.basicConfig(level=logging.INFO)
	basepath = get_paths(samples_dir="data/83a02e9_Jul22_sftotal/", dataset="latest")
	sampnames = [
		"TTJets_FullLept", "TTJets_SemiLept",
		"T_t_ToLeptons", "Tbar_t_ToLeptons",
		"W1Jets_exclusive", "W2Jets_exclusive", "W3Jets_exclusive", "W4Jets_exclusive"

	]
	path = basepath["mc"]["mu"]["nominal"]["iso"]

	cut = Cuts.final(2,1)*Cuts.mu
	var = "cos_theta"
	plot_range=[20, -1, 1]
	lumi = lumi_iso["mu"]
	plot_args = {"x_label": "cos #theta"}


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
		"tchan": [".*_ToLeptons"],
		"wjets": ["W[1-4]Jets.*"]
	}

	pretty_names = {
		"ttbar": "t#bar{t}",
		"tchan": "signal (t-channel)",
		"wjets": "W",
	}

	pretty_names_weights = {
		"unw": "unweighted",
		"nom": "nominal",
		"bc_up": "SF_{bc} up",
		"bc_down": "SF_{bc} down",
		"l_up": "SF_{l} up",
		"l_down": "SF_{l} down",
	}

	recreate = True
	if recreate:
		for sn in sampnames:
			sample = Sample.fromFile(path + "/" + sn + ".root")

			for wn, w in weights:
				hi = sample.drawHistogram(var, str(cut), weight=w, plot_range=plot_range)
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
		hists = OrderedDict([(wn, colls[wn].hists[proc]) for wn, w in weights])
		for hn, h in hists.items():
			h.SetTitle(pretty_names_weights[hn])
		hists_normed = copy.deepcopy(hists)

		for hn, h in hists_normed.items():
			norm(h, setName=False)
			if hn!="unw":
				h.Divide(hists_normed["unw"])

		hists_normed["unw"].Divide(hists_normed["unw"])
		#hists_normed.pop("unw")

		c1 = plot_hists_dict(hists, False, **plot_args)
		c1.Update()
		c1.SaveAs("weighted_%s.pdf" % proc)


		c2 = plot_hists_dict(hists_normed, setNames=False, draw_cmd="HIST",
			min_bin=0.990, max_bin=1.01, legend_pos="top-left",
		**plot_args)
		c2.Update()
		c2.SaveAs("weighted_norm_%s.pdf" % proc)
