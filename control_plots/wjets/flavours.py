import ROOT
ROOT.gROOT.SetBatch(True)
from plots.common.sample import Sample
from plots.common.cuts import Cuts
from root_numpy import tree2rec
import numpy
import os
import logging
import glob
import re

from plots.common.sample import get_paths
from plots.common.cuts import flavour_scenarios
from plots.common.hist_plots import plot_hists
from plots.common.sample_style import Styling, ColorStyleGen
from plots.common.legend import legend
from plots.common.tdrstyle import tdrstyle
from plots.common.utils import merge_hists, mkdir_p
from collections import OrderedDict
from rootpy.io import File
from rootpy.plotting import Hist
import argparse
import pdb
import math

basedir = os.environ["STPOL_DIR"] + "/data"

def get_hf_frac(name, cut):
	logging.info("Getting fractions for %s" % name)
	basepath = get_paths(dataset="latest")
	samp = Sample.fromFile(
		"/".join([basepath["mc"]["mu"]["nominal"]["iso"], name])
	)

	hi = samp.drawHistogram("wjets_flavour_classification0", str(cut), plot_range=[8, 0, 8], dtype="I")
	out = dict()
	for sc, fr in zip(flavour_scenarios[0], list(hi.y())):
		out[sc] = fr
	return out

def make_histos(cut_name, cut, samples, out_dir):
	samp_out_dir = "/".join((out_dir, cut_name))
	mkdir_p(samp_out_dir)

	for s in samples:
		fi = ROOT.TFile(samp_out_dir + "/WJets_flavour_fracs__%s" % s, "RECREATE")
		counts = get_hf_frac(s, cut)
		count_list = counts.keys()
		fi.cd()
		hi = Hist(len(count_list), 0, len(count_list)-1, type="f", name="flavour_counts")

		i = 1
		for count in count_list:
			hi.SetBinContent(i, counts[count])
			hi.SetBinError(i, math.sqrt(counts[count]))
			hi.GetXaxis().SetBinLabel(i, count)
			i += 1
		hi.Sumw2()

		#Normalize to according to all events
		hi.Scale(10000.0/hi.GetBinContent(i-1))

		fi.cd()
		hi.SetDirectory(fi)
		hi.Write()
		logging.info("Wrote file %s" % fi.GetPath())
		fi.Close()
	return

if __name__=="__main__":
	logging.basicConfig(level=logging.WARNING)
	tdrstyle()
	ROOT.gStyle.SetOptTitle(0)
	out_dir = "/".join((os.environ["STPOL_DIR"], "out", "plots", "wjets", "flavour"))
	doHists = True
	doPlots = True
	if doHists:
		samps = [
			"W1Jets_exclusive.root", "W2Jets_exclusive.root", "W3Jets_exclusive.root", "W4Jets_exclusive.root",
			"WJets_sherpa.root",
		]
		make_histos("2J", Cuts.one_muon*Cuts.n_jets(2), samps, out_dir)
		#make_histos("2J1T", Cuts.final(2, 1), samps, out_dir)
	if doPlots:
		cut_name = "2J"
		fnames = glob.glob(out_dir + "/%s/WJets_flavour_fracs__*.root" % cut_name)
		files = {}
		hists = {}
		for fn in fnames:
			files[re.match(".*__(.*).root", fn).group(1)] = File(fn)
		logging.info("files = %s" % str(files))

		for sn, fi in files.items():
			hi = fi.Get("flavour_counts")
			hi.SetName(sn)
			pn = sn
			Styling.mc_style(hi, pn)
			hists[sn] = hi

		merges = OrderedDict()
		merges["W (madgraph)"] =  ["W1Jets_exclusive", "W2Jets_exclusive", "W3Jets_exclusive", "W4Jets_exclusive"]
		merges["W (sherpa)"] =  ["WJets_sherpa"]
		hists_merged = merge_hists(hists, merges)
		hists = hists_merged.values()

		ColorStyleGen.style_hists(hists)
		for h in hists:
			logging.info(list(h.y()))
			h.SetFillColor(ROOT.kWhite)
			h.Scale(1.0/h.Integral())
		c = plot_hists(hists, x_label="flavour(j,j)", y_label="", draw_cmd="HIST E1")
		leg = legend(hists, styles=len(hists)*["f"], nudge_x=-0.1)
		hists[0].SetTitle("Jet flavour fraction n %s" % cut_name)
		#hists[0].SetFillColor(ROOT.kGreen+2)
		hists[0].SetMinimum(10**-3)
		hists[0].SetMaximum(10)
		#hists[0].SetLineColor(ROOT.kGreen+2)
		c.SetLogy()
		c.SaveAs(out_dir + "/flavour_%s.pdf" % cut_name)
		c.Close()