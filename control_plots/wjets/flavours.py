import ROOT
from plots.common.sample import Sample
from plots.common.cuts import Cuts
from root_numpy import tree2rec
import os
import logging
import glob
import re

from plots.common.hist_plots import plot_hists
from plots.common.sample_style import Styling, ColorStyleGen
from plots.common.legend import legend
from plots.common.tdrstyle import tdrstyle
from plots.common.utils import merge_hists
import argparse

basedir = os.environ["STPOL_DIR"] + "/data"
datadirs = dict()
datadirs["iso"] = "/".join((basedir, "out_step3_joosep_11_07_19_44", "mu" ,"iso", "nominal"))

def get_hf_frac(name, cut):
	logging.info("Getting fractions for %s" % name)
	samp = Sample.fromFile(datadirs["iso"] + "/" + name)
	arr = tree2rec(samp.tree, ["gen_flavour_bj", "gen_flavour_lj"], str(cut))

	counts = dict()
	counts["Wbb"] = 0.0
	counts["WbX"] = 0.0
	counts["WcX"] = 0.0
	counts["WXX"] = 0.0
	for i in arr:
		flavours = [abs(i["gen_flavour_bj"]), abs(i["gen_flavour_lj"])]
		if flavours[0]==5 and flavours[1]==5:
			counts["Wbb"] += 1.0
		elif 5 in flavours:
			counts["WbX"] += 1.0
		elif 4 in flavours:
			counts["WcX"] += 1.0
		else:
			counts["WXX"] += 1.0
	return counts

def make_histos(cut_name, cut, samples, out_dir):
	out_dir = "/".join((out_dir, cut_name))
	mkdir_p(out_dir)
	for s in samples:
		fi = ROOT.TFile(out_dir + "/WJets_flavour_fracs__%s" % s, "RECREATE")
		fi.cd()
		hi = ROOT.TH1I("flavour_counts", "Flavour counts", 4, 0, 3)
		counts = get_hf_frac(s, cut)
		hi.AddBinContent(1, counts["Wbb"])
		hi.AddBinContent(2, counts["WbX"])
		hi.AddBinContent(3, counts["WcX"])
		hi.AddBinContent(4, counts["WXX"])
		hi.GetXaxis().SetBinLabel(1, "Wbb")
		hi.GetXaxis().SetBinLabel(2, "WbX")
		hi.GetXaxis().SetBinLabel(3, "WcX")
		hi.GetXaxis().SetBinLabel(4, "WXX")
		samp = Sample.fromFile(datadirs["iso"] + "/" + s)
		if samp.isMC:
			hi.Scale(samp.lumiScaleFactor(20000))
		fi.Write()
		logging.info("Wrote file %s" % fi.GetPath())
		fi.Close()
	return

if __name__=="__main__":
	logging.basicConfig(level=logging.INFO)
	cut = Cuts.final(2,0)
	tdrstyle()
	ROOT.gStyle.SetOptTitle(1)


	out_dir = "/".join((os.environ["STPOL_DIR"], "plots", "wjets", "flavour"))
	doHists = False
	doPlots = True
	if doHists:
		samps = [
			"W1Jets_exclusive.root", "W2Jets_exclusive.root", "W3Jets_exclusive.root", "W4Jets_exclusive.root",
			"WJets_sherpa_nominal.root",
			#"WJets_inclusive.root",
			#"TTJets_MassiveBinDECAY.root",
			#"T_t_ToLeptons.root",
			#"SingleMu.root"
		]
		make_histos("2J0T", Cuts.final(2, 0), samps, out_dir)
		make_histos("2J1T", Cuts.final(2, 1), samps, out_dir)
	if doPlots:
		fnames = glob.glob("WJets_flavour_fracs__*.root")
		files = {}
		hists = {}
		for fn in fnames:
			files[re.match(".*__(.*).root", fn).group(1)] = ROOT.TFile(fn)

		for sn, fi in files.items():
			hi = fi.Get("flavour_counts")
			hi.SetName(sn)
			Styling.mc_style(hi, sn)
			hists[sn] = hi

		merges = dict()
		#merges["WJets inc. MG"] = ["WJets_inclusive"]
		merges["WJets exc, MG"] =  ["W1Jets_exclusive", "W2Jets_exclusive", "W3Jets_exclusive", "W4Jets_exclusive"]
		merges["WJets inc. SHRP"] =  ["WJets_sherpa_nominal"]
		#merges["TTBar inc. MG"] =  ["TTJets_MassiveBinDECAY"]
		#merges["t-channel"] =  ["T_t_ToLeptons"]
		#merges["data"] =  ["TTJets_MassiveBinDECAY"]
		hists_merged = merge_hists(hists, merges)
		hists = hists_merged.values()
		c = plot_hists(hists, x_label="flavour(j,j)", y_label="")
		leg = legend(hists, styles=["f", "f", "f", "f"])
		hists[0].SetTitle("Jet flavour in 20/fb")
		hists[0].SetFillColor(ROOT.kGreen+2)
		hists[0].SetLineColor(ROOT.kGreen+2)

			