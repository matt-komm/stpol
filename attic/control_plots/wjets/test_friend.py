from plots.common.sample import Sample
from plots.common.sample_style import ColorStyleGen
from plots.common.hist_plots import plot_hists
from plots.common.cuts import Cuts, Weights
from plots.common.legend import legend
from plots.common.tdrstyle import tdrstyle

if __name__=="__main__":
	samp = Sample.fromFile("~/Documents/stpol/data/out_step3_joosep_11_07_19_44/mu/iso/nominal/W4Jets_exclusive.root")
	samp.tree.AddFriend("trees/WJets_weights", samp.file_name)

	tdrstyle()
	
	cut = str(Cuts.final(2,0)*Cuts.Wflavour("W_heavy"))
	mean_weight = samp.drawHistogram(str(Weights.wjets_madgraph_weight("nominal")), cut, weight="1.0", plot_range=[200, 0, 2]).hist.GetMean()
	print "mean weight=%.2f" % mean_weight
	hi0 = samp.drawHistogram("cos_theta", cut, weight="1.0", plot_range=[20, -1, 1]).hist
	hi0.Scale(samp.lumiScaleFactor(20000))
	hi1 = samp.drawHistogram("cos_theta", cut, weight=str(Weights.wjets_madgraph_weight("nominal")), plot_range=[20, -1, 1]).hist
	hi1.Scale(samp.lumiScaleFactor(20000))
	hi2 = samp.drawHistogram("cos_theta", cut, weight=str(Weights.wjets_madgraph_weight("wjets_up")), plot_range=[20, -1, 1]).hist
	hi2.Scale(samp.lumiScaleFactor(20000))
	hi3 = samp.drawHistogram("cos_theta", cut, weight=str(Weights.wjets_madgraph_weight("wjets_down")), plot_range=[20, -1, 1]).hist
	hi3.Scale(samp.lumiScaleFactor(20000))

	hists = [hi0, hi1, hi2, hi3]
	#for h in hists:
	#	h.Scale(1.0/h.Integral())
	hi0.SetTitle("unweighted")
	hi1.SetTitle("weighted")
	hi2.SetTitle("weighted wjets_up")
	hi3.SetTitle("weighted wjets_down")
	ColorStyleGen.style_hists(hists)
	canv = plot_hists(hists, x_label="cos #theta")
	leg = legend(hists, styles=["f", "f"], nudge_x=-0.2)
	hi0.SetTitle("WJets hf yield with variations, 2J0T")
	canv.Update()