import ROOT
from plot_utils import data_mc, plot_hists_dict
from plots.common.cuts import Cuts, Weights, Weight
from plots.common.sample import Sample, get_paths
from plots.common.cross_sections import lumi_iso
from plots.common.histogram import HistCollection
from plots.common.odict import OrderedDict
import rootpy, numpy
import glob
import re
import root_numpy
import pdb
from copy import deepcopy
from plots.common.tdrstyle import tdrstyle
ROOT.gROOT.SetBatch(True)

def shape_variation(var, plot_range, varname, recreate, out_name):
	tot_hists = OrderedDict()
	tdrstyle()
	for wn, w in [
		("unw", Weight("1.0")),
		("nominal", Weights.wjets_madgraph_shape_weight("nominal")),
		("shape_up", Weights.wjets_madgraph_shape_weight("wjets_up")),
		("shape_down", Weights.wjets_madgraph_shape_weight("wjets_down"))
	]:
		p = data_mc(
			var, "2J0T_%s" % (wn),
			cut, Weights.total("mu", "nominal")*w,
			samples, ".", recreate, lumi_iso["mu"], plot_range=plot_range,
		)
		for hn, h in p.hists.items():
			logger.debug("%s %.2f" % (hn, h.Integral()))
		#sumw = [(sample.name, numpy.mean(root_numpy.root2array(sample.tfile.GetPath()[:-2], "trees/WJets_weights", branches=[str(w)])[str(w)])) for sample in samples]
		s = sum(p.hists.values()).Clone()
		tot_hists[wn] = s

	hc = HistCollection(tot_hists, name=out_name)
	for hn, h in hc.hists.items():
		print hn, h.Integral()

	canv = plot_hists_dict(hc.hists, do_chi2=False, do_ks=True, x_label=varname, legend_pos="top-left")
	hc.hists.values()[0].SetTitle("shape variation")
	canv.SaveAs(out_name + ".png")
	hc.save(out_name)
	return hc, canv

if __name__=="__main__":
	ROOT.TH1F.AddDirectory(False)
	import logging
	#rootpy.log.basic_config_colorized()
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
	recreate = True


	r1 = shape_variation("cos_theta", [10, -1, 1], "cos #theta", recreate, "variations_cos_theta")
	r2 = shape_variation("abs(eta_lj)", [10, 2.5, 4.5], "|#eta|_{j'}", recreate, "variations_abs_eta_lj")
	
