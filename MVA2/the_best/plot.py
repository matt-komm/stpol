import array
import ROOT
import MVA2.common
import MVA2.plot_ROC
import plots.common

f = ROOT.TFile("trained.root", "UPDATE")

meta = MVA2.common.readTObject("meta", f)


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



MVA2.plot_ROC.plot_ROC(s, b, [ "mva_Likelihood", "mva_BDT", "eta_lj" ])
