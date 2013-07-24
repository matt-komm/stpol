import ROOT
from plot_utils import data_mc, plot_hists_dict
from plots.common.cuts import Cuts, Weights
from plots.common.sample import Sample, get_paths
from plots.common.cross_sections import lumi_iso
from plots.common.histogram import HistCollection
import rootpy, numpy
import glob
import re
import root_numpy
import pdb
from copy import deepcopy

if __name__=="__main__":
	import logging
	rootpy.log.basic_config_colorized()
	logging.basicConfig(level=logging.WARNING)
	logger = rootpy.log["/systematics"]

	data_repro = "Jul15"
	path = get_paths()[data_repro]["mc"]["mu"]["nominal"]["iso"]
	logger.info("Input path %s" % path)
	samples = [
		Sample.fromFile(f) for f in
			filter(lambda x: re.match(".*/W[1-4]Jets.*", x), glob.glob(path + "/*.root"))
	]
	logger.info("samples %s" % samples)


	cut = Cuts.final(2,1)
	tot_hists = dict()
	for wn, w in [
		("nominal", Weights.wjets_madgraph_shape_weight("nominal")),
		("shape_up", Weights.wjets_madgraph_shape_weight("wjets_up")),
		("shape_down", Weights.wjets_madgraph_shape_weight("wjets_down"))
	]:
		p = data_mc(
			"cos_theta", "2J1T_%s" % (wn),
			cut, Weights.total("mu", "nominal")*w,
			samples, ".", True, lumi_iso["mu"], plot_range=[20, -1, 1],
		)
		sumw = [(sample.name, numpy.mean(root_numpy.root2array(sample.tfile.GetPath()[:-2], "trees/WJets_weights", branches=[str(w)])[str(w)])) for sample in samples]
		s = sum(p.hists.values())
		tot_hists[wn] = deepcopy(s)

	hc = HistCollection(tot_hists, name="wjets")
	for hn, h in hc.hists.items():
		print hn, h.Integral()

	canv = plot_hists_dict(hc.hists)
	hc.save(".")
