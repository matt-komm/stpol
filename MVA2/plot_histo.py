import ROOT
import MVA2.common
import plots.common.colors
import plots.common.cross_sections
import math

def plot_histo(mc, data, variables, cutstring, lept, nbins = 20, jobname="noname"):
	trees = {}
	weights = {}
	for ch in mc.keys():
		trees[ch] = mc[ch].Get("trees/Events")
		weights[ch] = MVA2.common.getSCF(lept, ch, mc[ch].Get("trees/count_hist").GetBinContent(1))
	trees["data"] = data.Get("trees/Events")
	weights["data"] = 1
	
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
		
		datahisto = ROOT.TH1F("data_"+var+"_"+jobname, var+" distribution of data", nbins, minval, maxval)
		datahisto.SetMarkerStyle(1)
		trees["data"].Draw(var + " >> data_"+var+"_"+jobname, cutstring)
		datahisto.Sumw2()
		datahisto.Scale(1, "width")
		
		canvas = ROOT.TCanvas(var+"_canvas_"+jobname, "Canvas for "+var, 800, 600)
		datahisto.Draw("E1")
		stack.Draw("SAME")
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
	print "cutstring = " + cutstring
	for ch in mc.keys() + ["data"]:
		print ch + ": {0:.2f} +- {1:.2f}".format(trees[ch].GetEntries(cutstring) * weights[ch], math.sqrt(trees[ch].GetEntries(cutstring)) * weights[ch])
	
