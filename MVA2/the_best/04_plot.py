import array
import ROOT
import MVA2.common
import MVA2.plot_ROC
import MVA2.plot_histo
import plots.common.cuts


f = ROOT.TFile("trained.root", "UPDATE")
meta = MVA2.common.readTObject("meta", f)

# plot trained method ROC curves
s = {
	f.Get("test/signal/T_t_ToLeptons") : plots.common.cross_sections.xs["T_t_ToLeptons"]/meta["initial_events"]["T_t_ToLeptons"],
	f.Get("test/signal/Tbar_t_ToLeptons") : plots.common.cross_sections.xs["Tbar_t_ToLeptons"]/meta["initial_events"]["Tbar_t_ToLeptons"],
}
b = {
	f.Get("test/background/W1Jets_exclusive") : plots.common.cross_sections.xs["W1Jets_exclusive"]/meta["initial_events"]["W1Jets_exclusive"],
	f.Get("test/background/W2Jets_exclusive") : plots.common.cross_sections.xs["W2Jets_exclusive"]/meta["initial_events"]["W2Jets_exclusive"],
	f.Get("test/background/W3Jets_exclusive") : plots.common.cross_sections.xs["W3Jets_exclusive"]/meta["initial_events"]["W3Jets_exclusive"],
	f.Get("test/background/W4Jets_exclusive") : plots.common.cross_sections.xs["W4Jets_exclusive"]/meta["initial_events"]["W4Jets_exclusive"],
}

MVA2.plot_ROC.plot_ROC(s, b, ["mva_" + mva for mva in meta["mvas"]] + ["eta_lj"], name="plot", title="comparison of MVAs vs plain eta_lj cut")

# plot histograms
channelnames = MVA2.common.samples.signal + MVA2.common.samples.WJets + MVA2.common.samples.other
files = {}
for ch in channelnames:
	files[ch] = ROOT.TFile("filled_trees/"+ch+".root")

dataname = "SingleMu" if meta["lept"] == "mu" else "SingleEle"
datafile = ROOT.TFile("filled_trees/"+dataname+".root")

MVA2.plot_histo.plot_histo(files, datafile, ["cos_theta"], cutstring = meta["cutstring"] + " && (mva_BDT > 0.0)", lept = meta['lept'], nbins = 30, jobname="BDT_0.0")
MVA2.plot_histo.plot_histo(files, datafile, ["cos_theta"], cutstring = meta["cutstring"] + " && (mva_BDT > 0.1)", lept = meta['lept'], nbins = 30, jobname="BDT_0.1")
MVA2.plot_histo.plot_histo(files, datafile, ["cos_theta"], cutstring = meta["cutstring"] + " && (mva_BDT > 0.2)", lept = meta['lept'], nbins = 30, jobname="BDT_0.2")
MVA2.plot_histo.plot_histo(files, datafile, ["cos_theta"], cutstring = meta["cutstring"] + " && (mva_BDT > 0.3)", lept = meta['lept'], nbins = 30, jobname="BDT_0.3")
MVA2.plot_histo.plot_histo(files, datafile, ["cos_theta"], cutstring = meta["cutstring"] + " && (mva_BDT > 0.4)", lept = meta['lept'], nbins = 30, jobname="BDT_0.4")
MVA2.plot_histo.plot_histo(files, datafile, ["cos_theta"], cutstring = meta["cutstring"] + " && (mva_BDT > 0.5)", lept = meta['lept'], nbins = 30, jobname="BDT_0.5")
MVA2.plot_histo.plot_histo(files, datafile, ["cos_theta"], cutstring = meta["cutstring"] + " && (mva_BDT > 0.6)", lept = meta['lept'], nbins = 30, jobname="BDT_0.6")
MVA2.plot_histo.plot_histo(files, datafile, ["mva_BDT"], cutstring = meta["cutstring"], lept = meta['lept'], nbins = 30, jobname="mva_BDT")
