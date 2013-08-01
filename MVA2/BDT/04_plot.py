import array
import ROOT
import MVA2.common
import MVA2.plot_ROC
import MVA2.plot_histo
import plots.common.cuts
import plots.common.cross_sections
import numpy as np

#~ f1 = ROOT.TFile("trained_WJets.root", "UPDATE")
#~ meta1 = MVA2.common.readTObject("meta", f1)
#~ f2 = ROOT.TFile("trained_WJets_ttbar.root", "UPDATE")
#~ meta2 = MVA2.common.readTObject("meta", f2)
f = ROOT.TFile("trained_WJets_ttbar.root", "UPDATE")
meta = MVA2.common.readTObject("meta", f)

# plot histograms
channelnames = MVA2.common.samples.signal + MVA2.common.samples.WJets + MVA2.common.samples.other
files = {}
for ch in channelnames:
	#~ files[ch] = ROOT.TFile("filled_trees/"+ch+".root")
	files[ch] = ROOT.TFile("filled_trees_mu/"+ch+".root")

#~ dataname1 = "SingleMu" if meta1["lept"] == "mu" else "SingleEle"
#~ datafile1 = ROOT.TFile("filled_trees/"+dataname1+".root")
#~ dataname2 = "SingleMu" if meta2["lept"] == "mu" else "SingleEle"
#~ datafile2 = ROOT.TFile("filled_trees/"+dataname2+".root")
datafiles = {}
datafiles["SingleMu1"] = ROOT.TFile("filled_trees_mu/SingleMu1.root")
datafiles["SingleMu2"] = ROOT.TFile("filled_trees_mu/SingleMu2.root")
datafiles["SingleMu3"] = ROOT.TFile("filled_trees_mu/SingleMu3.root")

finalcut = "n_veto_mu==0 && n_veto_ele==0 && n_muons==1 && n_eles==0 && \
top_mass > 130 && top_mass < 220 && abs(eta_lj) > 2.5 && n_jets == 2 && \
n_tags == 1 && rms_lj < 0.025 && mt_mu > 50"

# find the optimal cut value
strees = {}
for sg in MVA2.common.samples.signal:
	tree = files[sg].Get("trees/Events")
	strees[tree] = plots.common.cross_sections.xs[sg]
targeteff = MVA2.common.find_efficiency(strees, meta["cutstring"], finalcut)

cutval = MVA2.common.find_cut_value(strees, "mva_BDT_all_mu_Mario", targeteff, meta["cutstring"])

MVA2.plot_histo.plot_histo(files, datafiles, ["cos_theta"], cutstring = meta["cutstring"] + " && (mva_BDT_all_mu_Mario > {0})".format(cutval), lept = meta['lept'], nbins = 30, jobname="BDT_all_mu_Mario>{0:+1.3f}".format(cutval))
MVA2.plot_histo.plot_histo(files, datafiles, ["cos_theta"], cutstring = finalcut, lept = meta['lept'], nbins = 30, jobname="cut_final")


#~ MVA2.plot_histo.plot_histo(files, datafile1, ["mva_BDT_WJets"], cutstring = meta1["cutstring"], lept = meta1['lept'], nbins = 30, jobname="discriminators")
#~ MVA2.plot_histo.plot_histo(files, datafile1, ["mva_BDT_WJets_Mario"], cutstring = meta1["cutstring"], lept = meta1['lept'], nbins = 30, jobname="discriminators")
#~ MVA2.plot_histo.plot_histo(files, datafile2, ["mva_BDT_WJets_ttbar"], cutstring = meta2["cutstring"], lept = meta2['lept'], nbins = 30, jobname="discriminators")
#~ MVA2.plot_histo.plot_histo(files, datafile2, ["mva_BDT_WJets_ttbar_Mario"], cutstring = meta2["cutstring"], lept = meta2['lept'], nbins = 30, jobname="discriminators")
#~ MVA2.plot_histo.plot_histo(files, datafiles, ["mva_BDT_all_mu_Mario"], cutstring = meta["cutstring"], lept = meta['lept'], nbins = 30, jobname="discriminators")

#~ for t in np.arange(0.3, 0.4, 0.025):
	#~ MVA2.plot_histo.plot_histo(files, datafile1, ["cos_theta"], cutstring = meta1["cutstring"] + " && (mva_BDT_WJets > {0})".format(t), lept = meta1['lept'], nbins = 30, jobname="BDT_WJets>{0:+1.3f}".format(t))
#~ for t in np.arange(0.0, 0.1, 0.025):
	#~ MVA2.plot_histo.plot_histo(files, datafile2, ["cos_theta"], cutstring = meta2["cutstring"] + " && (mva_BDT_WJets_ttbar > {0})".format(t), lept = meta2['lept'], nbins = 30, jobname="BDT_WJets_ttbar>{0:+1.3f}".format(t))
#~ for t in np.arange(-1.0, 1.0, 0.1):
	#~ MVA2.plot_histo.plot_histo(files, datafile1, ["cos_theta"], cutstring = meta2["cutstring"] + " && (mva_BDT_WJets_Mario > {0})".format(t), lept = meta1['lept'], nbins = 30, jobname="BDT_WJets_Mario>{0:+1.3f}".format(t))
#~ for t in np.arange(0.0, 0.1, 0.05):
	#~ MVA2.plot_histo.plot_histo(files, datafile2, ["cos_theta"], cutstring = meta2["cutstring"] + " && (mva_BDT_WJets_ttbar_Mario > {0})".format(t), lept = meta2['lept'], nbins = 30, jobname="BDT_WJets_ttbar_Mario>{0:+1.3f}".format(t))
#~ for t in np.arange(0.1, 0.2, 0.02):
	#~ MVA2.plot_histo.plot_histo(files, datafiles, ["cos_theta"], cutstring = meta["cutstring"] + " && (mva_BDT_all_mu_Mario > {0})".format(t), lept = meta['lept'], nbins = 30, jobname="BDT_all_mu_Mario>{0:+1.3f}".format(t))

#~ MVA2.plot_histo.plot_histo(files, datafiles, ["cos_theta"], cutstring = finalcut, lept = meta['lept'], nbins = 30, jobname="cut_final")

