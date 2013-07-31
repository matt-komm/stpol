import ROOT
import MVA2.common
import plots.common.colors
import plots.common.cross_sections
import math

categories = {
	'T_t_ToLeptons': "t-channel",
	'Tbar_t_ToLeptons': "t-channel",
	'W1Jets_exclusive': "WJets",
	'W2Jets_exclusive': "WJets",
	'W3Jets_exclusive': "WJets",
	'W4Jets_exclusive': "WJets",
	'TTJets_FullLept': "t#bar{t} (#rightarrow lq, ll)",
	'TTJets_SemiLept': "t#bar{t} (#rightarrow lq, ll)",
	'T_s': "s-channel",
	'Tbar_s': "s-channel",
	'T_tW': "tW-channel",
	'Tbar_tW': "tW-channel",
	'WW': "diboson",
	'WZ': "diboson",
	'ZZ': "diboson",
	'GJets1': "GJets",
	'GJets2': "GJets",
	'DYJets': "DY-jets",
	'data': "Data",
}

def plot_histo(mc, data, variables, cutstring, lept, nbins = 20, jobname="noname"):
	trees = {}
	weights = {}
	for ch in mc.keys():
		trees[ch] = mc[ch].Get("trees/Events")
		weights[ch] = MVA2.common.getSCF(lept, ch, mc[ch].Get("trees/count_hist").GetBinContent(1))
	for ch in data.keys():
		trees[ch] = data[ch].Get("trees/Events")
		weights[ch] = 1
	
	for var in variables:
		stack = ROOT.THStack(var+"_stack_"+jobname, "Distribution of "+var)
		minval = MVA2.common.find_min_in_trees(trees.values(), var, special=[])
		maxval = MVA2.common.find_max_in_trees(trees.values(), var, special=[])
		maxval += (maxval-minval)*0.25 # to make room for the legend
		histos = {}
		for ch in mc.keys():
			histos[ch] = ROOT.TH1F(ch+"_"+var+"_"+jobname, var+" distribution of "+ch, nbins, minval, maxval)
			trees[ch].Draw(var+" >> "+ch+"_"+var+"_"+jobname, "("+str(weights[ch])+")*("+cutstring+")")
			histos[ch].SetFillColor(plots.common.colors.sample_colors_same[ch])
			#histos[ch].Sumw2()
			histos[ch].Scale(1, "width")
			stack.Add(histos[ch])
		
		datahisto = ROOT.TH1F("data_"+var+"_"+jobname, var+", "+jobname, nbins, minval, maxval)
		datahisto.SetMarkerStyle(1)
		for ch in data.keys():
			trees[ch].Draw(var + " >>+ data_"+var+"_"+jobname, cutstring)
		datahisto.Sumw2()
		datahisto.Scale(1, "width")
		
		canvas = ROOT.TCanvas(var+"_canvas_"+jobname, "Canvas for "+var, 800, 600)
		if (datahisto.GetMaximum() > stack.GetMaximum()):
			datahisto.Draw("E1")
			stack.Draw("SAME")
			datahisto.Draw("SAME E1")
		else:
			stack.Draw()
			datahisto.Draw("SAME E1")
		
		legend = ROOT.TLegend(0.75, 0.15, 0.95, 0.75)
		legend.AddEntry(datahisto, "data", "P")
		for ch in mc.keys():
			legend.AddEntry(histos[ch], ch, "F")
		legend.Draw()
		
		img = ROOT.TImage.Create()
		img.FromPad(canvas)
		img.WriteImage('histo_'+var+"_"+jobname+".png")
		
	# output purity info
	cnt = {}
	err = {}
	cnt["MC total"] = 0
	err["MC total"] = 0
	
	for ch in mc.keys():
		cat = categories[ch]
		if not cat in cnt.keys():
			cnt[cat] = 0
			err[cat] = 0
		cnt[cat]        += trees[ch].GetEntries(cutstring) * weights[ch]
		cnt["MC total"] += trees[ch].GetEntries(cutstring) * weights[ch]
		err[cat]        += trees[ch].GetEntries(cutstring) * weights[ch] * weights[ch]
		err["MC total"] += trees[ch].GetEntries(cutstring) * weights[ch] * weights[ch]
	
	cnt["Data"] = 0
	err["Data"] = 0
	for ch in data.keys():
		cnt["Data"] += trees[ch].GetEntries(cutstring)
		err["Data"] += trees[ch].GetEntries(cutstring)
	
	efff = open("eff_"+jobname+".txt", 'w')
	efff.write("cutstring = " + cutstring + "\n\n")
	for cat in ["diboson", "WJets", "DY-jets", "GJets", "t#bar{t} (#rightarrow lq, ll)", "tW-channel", "s-channel", "t-channel", "Data", "MC total"]:
		if not cat in cnt.keys():
			continue
		efff.write(cat + ":\t{0:.2f} +- {1:.2f}\n".format(cnt[cat], math.sqrt(err[cat])))
	efff.write("\npurity = {0:.0f}%\n".format(100*cnt["t-channel"]/cnt["MC total"]))
	
	efff.close()
	
	
