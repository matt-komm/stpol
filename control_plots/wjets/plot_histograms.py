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

#matches everything
pat_all = make_pattern()
dc = copy.deepcopy

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

				hi.Rebin(5)

				histsA[item][md.N_jets][md.N_tags][md.weight][sample_name][md.jet_flavour] = hi
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
	logging.basicConfig(level=logging.INFO)


	tdrstyle()
	ROOT.gStyle.SetOptTitle(True)

	plot_order = PhysicsProcess.desired_plot_order
	plot_order.pop(plot_order.index("WJets"))
	plot_order.insert(1, "WJets W+hf")
	plot_order.insert(2, "WJets W+l")
	plot_order.insert(3, "WJets W+g")
	N_jets = 2
	N_tags = 1
	cut_region = "SR"
	cut_name = "%dJ%dT %s" % (N_jets, N_tags, cut_region)
	cos_theta = "cos #theta"
	plot_args = {"legend_text_size":0.015, "legend_pos":"top-left", "x_label":cos_theta}

	out_dir = "out/plots/wjets/%dJ%dT_%s/" % (N_jets, N_tags, cut_region)
	mkdir_p(out_dir)
	histsA, histsB = load_hists("hists/%s" % cut_region)

	wjets_hists = NestedDict()

	for k, v in histsA["cos_theta"][N_jets][N_tags]["unweighted"].items():
		if re.match("W.*Jets.*", k):
			for flavour, hist in v.items():
				wjets_hists[flavour][k] = hist

	merged_wjets = NestedDict()
	wjets_merges = OrderedDict()
	wjets_merges["sherpa"] = ["WJets_sherpa_nominal"]
	wjets_merges["madgraph"] = ["W[1-4]Jets_exclusive"]
	hists_ratio = NestedDict()

	for flavour, hists in wjets_hists.items():
		merged_wjets[flavour] = merge_hists(hists, wjets_merges, order=wjets_merges.keys())

		madgraph_rew_hists = dict(
			filter(lambda x:
				make_pattern(
					N_jets=N_jets, N_tags=N_tags, weight="weighted_wjets_mg_flavour_nominal",
					var="cos_theta", flavour=flavour, extra="/sample__W[1-4]Jets_exclusive"
				).match(x[0]), histsB.items()
			)
		).values()
		madgraph_rew = sum(madgraph_rew_hists)

		cloned = dc(merged_wjets[flavour])
		norm(cloned["sherpa"])
		norm(cloned["madgraph"])
		madgraph_rew.Scale(cloned["madgraph"].Integral() / madgraph_rew.Integral())
		cloned["madgraph/rew"] = madgraph_rew
		fname = flavour_scenarios[0][flavour]
		hists_ratio["ratio__" + fname] = dc(cloned["sherpa"].Clone("ratio__%s" % fname))
		hists_ratio["ratio__" + fname].Divide(cloned["madgraph"])
		hists_ratio["ratio__" + fname].SetTitle(fname)
		canv = plot_hists_dict(cloned, do_chi2=True, legend_pos="top-left", x_label=cos_theta)
		cloned["sherpa"].SetTitle("cos #theta %s %s" % (cut_name, fname))
		canv.SaveAs(out_dir+"sherpa_madgraph_%s.png" % flavour)


	ratios_coll = HistCollection(hists_ratio, name="hists__costheta_flavours_merged_scenario0")
	canv = plot_hists_dict(hists_ratio, max_bin=2.0, min_bin=0.5, x_label=cos_theta)
	hists_ratio.values()[0].SetTitle("sherpa to madgraph ratios")
	ratios_coll.save(out_dir)

	canv.SaveAs(out_dir + "/ratios.png")
	merged_flavours = NestedDict()
	merges = copy.deepcopy(plots.common.utils.merge_cmds)
	merges.pop("WJets")
	merges["WJets W+hf"] = ["W[1-4]Jets_exclusive/W_heavy"]
	merges["WJets W+g"] = ["W[1-4]Jets_exclusive/W_gluon"]
	merges["WJets W+l"] = ["W[1-4]Jets_exclusive/W_light"]

	sherpa_merged = merge_flavours(histsA["cos_theta"][N_jets][N_tags]["unweighted"]["WJets_sherpa_nominal"].values())

	merged_final = NestedDict()
	weights = ["weighted_wjets_mg_flavour_nominal", "weighted_wjets_mg_flavour_up", "weighted_wjets_mg_flavour_down"]
	for var in ["cos_theta", "abs_eta_lj"]:
		for weight in ["unweighted"] + weights:
			for sample_name, hists in histsA[var][N_jets][N_tags][weight].items():

				if is_wjets(sample_name):
					for merge_name, hist in merge_flavours(hists.values()).items():
						merged_flavours[var][weight][sample_name + "/" + merge_name] = hist
				else:
					merged_flavours[var][weight][sample_name] = hists[-1]


			merged_final[var][weight] = merge_hists(merged_flavours[var][weight], merges, merges.keys())

			merged_final[var][weight]["WJets W+hf"].SetFillColor(
				merged_final[var][weight]["WJets W+l"].GetFillColor()+1
			)
			merged_final[var][weight]["WJets W+g"].SetFillColor(
				merged_final[var][weight]["WJets W+l"].GetFillColor()+2
			)

			if not weight=="unweighted":
				for k, v in merged_final[var]["unweighted"].items():
					if k in merged_final[var][weight].keys():
						continue
					merged_final[var][weight][k] = dc(v)

		canv = ROOT.TCanvas()
		r = plot(canv, "2J_%s" % var, merged_final[var]["unweighted"], out_dir, desired_order=plot_order, **plot_args)

		canv = ROOT.TCanvas()
		r = plot(canv, "2J_rew_up_%s" % var, merged_final[var]["weighted_wjets_mg_flavour_up"], out_dir, desired_order=plot_order, **plot_args)

		canv = ROOT.TCanvas()
		r = plot(canv, "2J_rew_down_%s" % var, merged_final[var]["weighted_wjets_mg_flavour_down"], out_dir, desired_order=plot_order, **plot_args)

		tot_mc = sum([v for (k, v) in merged_final[var]["weighted_wjets_mg_flavour_nominal"].items() if k!="data"])
		tot_syst_error = ROOT.TGraphAsymmErrors(tot_mc)
		syst_up = sum([v for (k, v) in merged_final[var]["weighted_wjets_mg_flavour_up"].items() if k!="data"])
		syst_down = sum([v for (k, v) in merged_final[var]["weighted_wjets_mg_flavour_down"].items() if k!="data"])


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
			print "%.2f | %.2f | %.2f | %.2f" % (tot_mc.GetBinContent(i), merged_final[var]["weighted_wjets_mg_flavour_nominal"]["data"].GetBinContent(i), syst_up.GetBinContent(i), syst_down.GetBinContent(i))

		canv = ROOT.TCanvas()
		r = plot(canv, "2J_rew_%s" % var, merged_final[var]["weighted_wjets_mg_flavour_nominal"], out_dir, desired_order=plot_order, hist_tot_syst_error=tot_syst_error, **plot_args)


	hists = NestedDict()
	hists["sh"] = sherpa_merged["W_heavy"]
	hists["mg/unw"] = merged_final["cos_theta"]["unweighted"]["WJets W+hf"]
	hists["mg/rew/nom"] = merged_final["cos_theta"]["weighted_wjets_mg_flavour_nominal"]["WJets W+hf"]
	hists["sh"].Scale(hists["mg/unw"].Integral() / hists["sh"].Integral())

	canv = plot_hists_dict(hists, do_chi2=True, **plot_args)
	canv.SaveAs(out_dir + "mg_weighting_hf.png")


	hists = NestedDict()
	#hists["data"] = merged_final["unweighted"]["data"]
	hists["sh/unw"] = sum([h for k, h in sherpa_merged.items()])
	hists["mg/unw"] = sum([h for k, h in merged_final["cos_theta"]["unweighted"].items() if re.match("WJets.*", k)])
	hists["mg/rew/nom"] = sum([h for k, h in merged_final["cos_theta"]["weighted_wjets_mg_flavour_nominal"].items() if re.match("WJets.*", k)])
	#hists["mg/rew/up"] = sum([h for k, h in merged_final["weighted_wjets_mg_flavour_up"].items() if re.match("WJets.*", k)])
	#hists["mg/rew/down"] = sum([h for k, h in merged_final["weighted_wjets_mg_flavour_down"].items() if re.match("WJets.*", k)])
	#hists["data"].Scale(hists["mg/rew/nom"].Integral() / hists["data"].Integral())
	#hists["sh/unw"].Scale(hists["mg/rew/nom"].Integral() / hists["sh/unw"].Integral())
	map(lambda x: x.Rebin(2), hists.values())
	map(lambda x: norm(x), hists.values())
	canv = plot_hists_dict(hists, do_chi2=False, **plot_args)
	canv.SaveAs(out_dir + "mg_weighting_data.eps")




