import ROOT
ROOT.gROOT.SetBatch(True)
from rootpy.io.file import File
import glob
import re
from plots.common.sample import *
from plots.common.histogram import *
from plots.common.sample_style import *
from SingleTopPolarization.Analysis.sample_types import *
import copy
import plots.common.utils
from plots.common.utils import merge_hists
from plots.common.tdrstyle import tdrstyle
from plots.common.hist_plots import *
from plots.common.sample_style import *
from plots.common.odict import OrderedDict
import pdb

from plot_utils import *

import logging

def make_pattern(N_jets=".*", N_tags=".*", flavour=".*", weight=".*", var=".*", extra=""):
	return re.compile(".*N_jets__(%s)/N_tags__(%s)/jet_flavour__(%s)/weight__(%s)/var__(%s)%s" % (N_jets, N_tags, flavour, weight, var, extra))

pat_all = make_pattern()
def make_metadata(histname):
	match = re.match(pat_all, histname)
	if not match:
		raise Exception("Couldn't match histname to pattern")

	(N_jets, N_tags, flavour, weight, varname) = match.groups()
	md = HistMetaData(
		N_jets=int(N_jets),
		N_tags=int(N_tags),
		weight=weight,
		jet_flavour=int(flavour),
		varname=varname
	)
	return md

def filter_hists(pat, hists):
	return filter(lambda x: re.match(k))

class NestedDict(OrderedDict):
	def __missing__(self, key):
		self[key] = NestedDict()
		return self[key]

dc = copy.deepcopy

LUMI=19739

def load_hists(dirname):
	files = map(File, glob.glob(dirname+"/*.root"))
	histsA = NestedDict()
	histsB = NestedDict()

	for fi in files:
		sample_name = get_sample_name(fi.name)
		process_name = get_process_name(sample_name)
		sample_xs = sample_xs_map[process_name]

		for root, dirs, items in fi.walk():
			for item in items:
				if(item.startswith("elist")):
					continue
				hn = fi.GetPath() + "/" + root + "/" + item
				hi = fi.Get("/".join([root, item])).Clone()
				hi.SetDirectory(0)
				
				md = make_metadata(hn)
				md.sample_name = sample_name
				md.sample_xs = sample_xs
				if is_mc(sample_name):
					hi.Scale(sample_xs*LUMI)

				if is_mc(sample_name):
					Styling.mc_style(hi, process_name)
				else:
					Styling.data_style(hi)

				hi.METADATA = md

				hi.Rebin(10)

				histsA[md.N_jets][md.N_tags][md.weight][sample_name][md.jet_flavour] = hi
				histsB[root + "/sample__%s" % sample_name + "/hist__%s" % item] = hi
		fi.Close()
	return histsA, histsB

def merge_flavours(hists):
	ret = dict()
	ret["W_heavy"] = sum(filter(lambda x: x.METADATA.jet_flavour>=0 and x.METADATA.jet_flavour<=4, hists))
	ret["W_gluon"] = sum(filter(lambda x: x.METADATA.jet_flavour>=5 and x.METADATA.jet_flavour<=6, hists))
	ret["W_light"] = sum(filter(lambda x: x.METADATA.jet_flavour==7, hists))
	for k, v in ret.items():
		v.SetName(k)
	return ret


if __name__=="__main__":

	tdrstyle()
	ROOT.gStyle.SetOptTitle(True)

	N_jets = 2
	N_tags = 1
	cut_region = "SR"
	cut_name = "%dJ%dT %s" % (N_jets, N_tags, cut_region)

	out_dir = "out/plots/wjets/%dJ%dT_%s/" % (N_jets, N_tags, cut_region)
	mkdir_p(out_dir)
	logging.basicConfig(level=logging.INFO)
	histsA, histsB = load_hists("hists/%s" % cut_region)

	wjets_hists = NestedDict()

	for k, v in histsA[N_jets][N_tags]["unweighted"].items():
		if re.match("W.*Jets.*", k):
			for flavour, hist in v.items():
				wjets_hists[flavour][k] = hist

	merged_wjets = NestedDict()
	wjets_merges = OrderedDict()
	wjets_merges["sherpa"] = ["WJets_sherpa_nominal"]
	wjets_merges["madgraph"] = ["W[1-4]Jets_exclusive"]
	hists_ratio = NestedDict()
	for flavour, hists in wjets_hists.items():
		merged_wjets[flavour] = merge_hists(hists, wjets_merges)

		madgraph_rew_hists = dict(
			filter(lambda x:
				make_pattern(
					N_jets=N_jets, N_tags=N_tags, weight="weighted_wjets_mg_flavour_nominal",
					var="cos_theta", flavour=flavour, extra="/sample__W[1-4]Jets_exclusive"
				).match(x[0]), histsB.items()
			)
		).values()
		madgraph_rew = sum(madgraph_rew_hists)
		#pdb.set_trace()
		#norm(madgraph_rew)

		cloned = dc(merged_wjets[flavour])
		norm(cloned["sherpa"])
		norm(cloned["madgraph"])
		madgraph_rew.Scale(cloned["madgraph"].Integral() / madgraph_rew.Integral())
		cloned["madgraph/rew"] = madgraph_rew
		fname = flavour_scenarios[0][flavour]
		hists_ratio["ratio__" + fname] = cloned["sherpa"].Clone("ratio")
		hists_ratio["ratio__" + fname].Divide(cloned["madgraph"])
		canv = plot_hists_dict(cloned, do_chi2=True, legend_pos="top-left")
		cloned["sherpa"].SetTitle("cos #theta %s %s" % (cut_name, fname))
		canv.SaveAs(out_dir+"sherpa_madgraph_%s.png" % flavour)

	ratios_coll = HistCollection(hists_ratio, name="hists__costheta_flavours_merged_scenario0")
	ratios_coll.save(out_dir)

	merged_flavours = NestedDict()
	merges = copy.deepcopy(plots.common.utils.merge_cmds)
	merges.pop("WJets")
	merges["WJets W+hf"] = ["W[1-4]Jets_exclusive/W_heavy"]
	merges["WJets W+g"] = ["W[1-4]Jets_exclusive/W_gluon"]
	merges["WJets W+l"] = ["W[1-4]Jets_exclusive/W_light"]

	sherpa_merged = merge_flavours(histsA[N_jets][N_tags]["unweighted"]["WJets_sherpa_nominal"].values())

	merged_final = NestedDict()
	weights = ["weighted_wjets_mg_flavour_nominal", "weighted_wjets_mg_flavour_up", "weighted_wjets_mg_flavour_down"]
	for weight in ["unweighted"] + weights:
		for sample_name, hists in histsA[N_jets][N_tags][weight].items():

			if is_wjets(sample_name):
				for merge_name, hist in merge_flavours(hists.values()).items():
					merged_flavours[weight][sample_name + "/" + merge_name] = hist
			else:
				merged_flavours[weight][sample_name] = hists[-1]


		merged_final[weight] = merge_hists(merged_flavours[weight], merges)

		merged_final[weight]["WJets W+hf"].SetFillColor(
			merged_final[weight]["WJets W+l"].GetFillColor()+1
		)
		merged_final[weight]["WJets W+g"].SetFillColor(
			merged_final[weight]["WJets W+l"].GetFillColor()+2
		)

		if not weight=="unweighted":
			for k, v in merged_final["unweighted"].items():
				if k in merged_final[weight].keys():
					continue
				merged_final[weight][k] = dc(v)

	canv = ROOT.TCanvas()
	r = plot(canv, "2J", merged_final["unweighted"], out_dir, legend_pos="top-left")

	canv = ROOT.TCanvas()
	r = plot(canv, "2J_rew_up", merged_final["weighted_wjets_mg_flavour_up"], out_dir, legend_pos="top-left")

	canv = ROOT.TCanvas()
	r = plot(canv, "2J_rew_down", merged_final["weighted_wjets_mg_flavour_down"], out_dir, legend_pos="top-left")

	tot_mc = sum([v for (k, v) in merged_final["weighted_wjets_mg_flavour_nominal"].items() if k!="data"])
	tot_syst_error = ROOT.TGraphAsymmErrors(tot_mc)
	syst_up = sum([v for (k, v) in merged_final["weighted_wjets_mg_flavour_up"].items() if k!="data"])
	syst_down = sum([v for (k, v) in merged_final["weighted_wjets_mg_flavour_down"].items() if k!="data"])


	bins_x = numpy.array([x for x in tot_mc.x()])
	errs_x = numpy.array(len(bins_x)*[0])
	bins_up, bins_down, bins_center = numpy.array([y for y  in syst_up.y()]), numpy.array([y for y  in syst_down.y()]), numpy.array([y for y  in tot_mc.y()])
	err_low = numpy.abs(bins_center-bins_down)
	err_high = numpy.abs(bins_center-bins_up)
	tot_syst_error = ROOT.TGraphAsymmErrors(
		len(bins_x), bins_x, bins_center,
		errs_x, errs_x,
		err_low, err_high)


	print "mc | data | syst up | syst down"
	for i in range(1, len(bins_up)+1):
		print "%.2f | %.2f | %.2f | %.2f" % (tot_mc.GetBinContent(i), merged_final["weighted_wjets_mg_flavour_nominal"]["data"].GetBinContent(i), syst_up.GetBinContent(i), syst_down.GetBinContent(i))

	canv = ROOT.TCanvas()
	r = plot(canv, "2J_rew", merged_final["weighted_wjets_mg_flavour_nominal"], out_dir, legend_pos="top-left", hist_tot_syst_error=tot_syst_error)


	hists = NestedDict()
	hists["sh"] = sherpa_merged["W_heavy"]
	hists["mg/unw"] = merged_final["unweighted"]["WJets W+hf"]
	hists["mg/rew/nom"] = merged_final["weighted_wjets_mg_flavour_nominal"]["WJets W+hf"]
	hists["sh"].Scale(hists["mg/unw"].Integral() / hists["sh"].Integral())

	canv = plot_hists_dict(hists, do_chi2=True, legend_pos="top-left")
	canv.SaveAs(out_dir + "mg_weighting_hf.png")




