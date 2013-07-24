import ROOT
from plot_utils import data_mc
from plots.common.cuts import Cuts, Weights
from plots.common.sample import Sample, get_paths
from plots.common.cross_sections import lumi_iso
from plots.common.histogram import HistCollection
import logging
import rootpy
import glob
import re

logger = logging.getLogger("systematics")
if __name__=="__main__":
	rootpy.log.basic_config_colorized()
	rootpy.log.setLevel(level=logging.WARNING)

	data_repro = "Jul15"
	path = get_paths()[data_repro]["mc"]["mu"]["nominal"]["iso"]
	logger.info("Input path %s" % path)
	samples = [
		Sample.fromFile(f) for f in
			filter(lambda x: re.match(".*/W[1-4]Jets.*", x), glob.glob(path + "/*.root"))
	]
	logger.info("samples %s" % samples)

	tot_hists = dict()
	for wn, w in [
		("nominal", Weights.wjets_madgraph_shape_weight("nominal")),
		("shape_up", Weights.wjets_madgraph_shape_weight("wjets_up")),
		("shape_down", Weights.wjets_madgraph_shape_weight("wjets_down"))
	]:
		p = data_mc(
			"cos_theta", "2J1T SR",
			Cuts.final(2,1), Weights.total("mu", "nominal")*w,
			samples, ".", True, lumi_iso["mu"], plot_range=[20, -1, 1],
		)
		s = sum(p.hists.values())
		tot_hists[wn] = s

	hc = HistCollection(tot_hists, name="wjets")
	hc.save(".")