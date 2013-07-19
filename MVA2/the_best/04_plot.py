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

MVA2.plot_histo.plot_histo(files, datafile, ["cos_theta", "eta_lj"], cutstring = meta["cutstring"] + " && (mva_BDT > 0.35)", lept = meta['lept'], nbins = 30, jobname="BDT_0.35")
MVA2.plot_histo.plot_histo(files, datafile, ["cos_theta", "eta_lj" ], cutstring = meta["cutstring"] + " && (abs(eta_lj) > 2.5)", lept = meta['lept'], nbins = 30, jobname="abs_eta_lj_2.5")
