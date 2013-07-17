import ROOT
from plots.common.sample import Sample
from plots.common.cuts import Cuts
from root_numpy import tree2rec
import numpy
import os
import logging
import glob
import re

from plots.common.hist_plots import plot_hists
from plots.common.sample_style import Styling, ColorStyleGen
from plots.common.legend import legend
from plots.common.tdrstyle import tdrstyle
from plots.common.utils import merge_hists, mkdir_p
from collections import OrderedDict
import argparse
import pdb
import math

basedir = os.environ["STPOL_DIR"] + "/data"
datadirs = dict()
datadirs["iso"] = "/".join((basedir, "out_step3_joosep_11_07_19_44", "mu" ,"iso", "nominal"))

def get_hf_frac(name, cut):
	logging.info("Getting fractions for %s" % name)
	samp = Sample.fromFile(datadirs["iso"] + "/" + name)
	logging.debug("cut=%s" % str(cut))

	isRew = name=="WJets_sherpa_nominal_reweighted.root"
	arr = tree2rec(samp.tree, ["gen_flavour_bj", "gen_flavour_lj", "pu_weight"] + ([] if not isRew else ["wjets_flavour_weight"]), selection=str(cut))
	counts = OrderedDict()
	
	counts["Wgg"] = 0.0
	counts["Wcc"] = 0.0
	counts["WbX"] = 0.0
	counts["WgX"] = 0.0
	counts["WcX"] = 0.0
	counts["WXX"] = len(arr)

	for r in numpy.nditer(arr):
		flavours = [abs(r["gen_flavour_bj"]), abs(r["gen_flavour_lj"])]
		x = 1.0
		if isRew:
			x = r["wjets_flavour_weight"]
		#if flavours == [5,5]:
		#	counts["Wbb"] += x
		if flavours == [21,21]:
			counts["Wgg"] += x
		elif flavours == [4,4]:
			counts["Wcc"] += x
		elif 5 in flavours:
			counts["WbX"] += x
		elif 21 in flavours:
			counts["WgX"] += x
		elif 4 in flavours:
			counts["WcX"] += x
	logging.debug("counts = %s" % str(counts))
	return counts

def make_histos(cut_name, cut, samples, out_dir):
	samp_out_dir = "/".join((out_dir, cut_name))
	mkdir_p(samp_out_dir)

	for s in samples:
		fi = ROOT.TFile(samp_out_dir + "/WJets_flavour_fracs__%s" % s, "RECREATE")
		counts = get_hf_frac(s, cut)
		count_list = counts.keys()
		fi.cd()
		hi = ROOT.TH1I("flavour_counts", "Flavour counts", len(count_list), 0, len(count_list)-1)

		i = 1
		for count in count_list:
			hi.SetBinContent(i, counts[count])
			hi.SetBinError(i, math.sqrt(counts[count]))
			hi.GetXaxis().SetBinLabel(i, count)
			i += 1
		hi.Sumw2()

		#Normalize to according to all events
		hi.Scale(10000.0/hi.GetBinContent(i-1))

		samp = Sample.fromFile(datadirs["iso"] + "/" + s)
		if samp.isMC:
			if samp.name == "WJets_sherpa_nominal_reweighted":
				samp.process_name = "WJets_sherpa_nominal"
			hi.Scale(samp.lumiScaleFactor(20000))
		fi.cd()
		hi.SetDirectory(fi)
		hi.Write()
		logging.info("Wrote file %s" % fi.GetPath())
		fi.Close()
	return

if __name__=="__main__":
	logging.basicConfig(level=logging.INFO)
	tdrstyle()
	ROOT.gStyle.SetOptTitle(1)
	#ROOT.gStyle.SetTitle


	out_dir = "/".join((os.environ["STPOL_DIR"], "out", "plots", "wjets", "flavour"))
	doHists = True
	doPlots = True
	if doHists:
		samps = [
			"WJets_sherpa_nominal_reweighted.root",
			"W1Jets_exclusive.root", "W2Jets_exclusive.root", "W3Jets_exclusive.root", "W4Jets_exclusive.root",
			"WJets_sherpa_nominal.root",
			"WJets_inclusive.root",
			#"TTJets_MassiveBinDECAY.root",
			#"T_t_ToLeptons.root",
			#"SingleMu.root"
		]
		make_histos("2J", Cuts.one_muon*Cuts.lepton_veto*Cuts.rms_lj*Cuts.mt_mu*Cuts.n_jets(2)*Cuts.eta_lj*Cuts.top_mass_sig, samps, out_dir)
		#make_histos("2J1T", Cuts.final(2, 1), samps, out_dir)
	if doPlots:
		cut_name = "2J"
		fnames = glob.glob(out_dir + "/%s/WJets_flavour_fracs__*.root" % cut_name)
		files = {}
		hists = {}
		for fn in fnames:
			files[re.match(".*__(.*).root", fn).group(1)] = ROOT.TFile(fn)
		logging.info("files = %s" % str(files))

		for sn, fi in files.items():
			hi = fi.Get("flavour_counts")
			hi.SetName(sn)
			pn = sn
			if sn=="WJets_sherpa_nominal_reweighted":
				pn = "WJets_sherpa_nominal"
			Styling.mc_style(hi, pn)
			hists[sn] = hi

		merges = OrderedDict()
		merges["WJets inc. MG"] = ["WJets_inclusive"]
		merges["WJets exc, MG"] =  ["W1Jets_exclusive", "W2Jets_exclusive", "W3Jets_exclusive", "W4Jets_exclusive"]
		merges["WJets inc. SHRP"] =  ["WJets_sherpa_nominal"]
		merges["WJets inc. SHRP (rew)"] =  ["WJets_sherpa_nominal_reweighted"]
		#merges["TTBar inc. MG"] =  ["TTJets_MassiveBinDECAY"]
		#merges["t-channel"] =  ["T_t_ToLeptons"]
		#merges["data"] =  ["TTJets_MassiveBinDECAY"]
		hists_merged = merge_hists(hists, merges)
		hists = hists_merged.values()

		ColorStyleGen.style_hists(hists)
		for h in hists:
			h.SetFillColor(ROOT.kWhite)
			h.Scale(10000.0/h.Integral())
		c = plot_hists(hists, x_label="flavour(j,j)", y_label="", draw_cmd="HIST E1")
		leg = legend(hists, styles=len(hists)*["f"], nudge_x=-0.1)
		hists[0].SetTitle("Jet flavour fraction (a.u.) in %s" % cut_name)
		#hists[0].SetFillColor(ROOT.kGreen+2)
		hists[0].SetMinimum(1)
		hists[0].SetMaximum(10**5)
		#hists[0].SetLineColor(ROOT.kGreen+2)
		c.SetLogy()
		c.SaveAs(out_dir + "/flavour_%s.png" % cut_name)

		for i in range(1,hists[0].GetNbinsX()+1):
			sh = hists[2]
			mg = hists[1]
			x = mg.GetBinContent(i) / sh.GetBinContent(i)
			err = math.sqrt(math.pow(mg.GetBinError(i)/mg.GetBinContent(i), 2) + math.pow(sh.GetBinError(i)/sh.GetBinContent(i), 2))*x
			print "weights[%s] = %f; //error=%f" % (hists[1].GetXaxis().GetBinLabel(i), x, err)