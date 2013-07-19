import ROOT
import MVA2.common


def plot_ROC(signals, backgrounds, variables, nbins = 100, name='noname', title='MVA ROC plot'):
	"""plots the ROC curve for for the trees in signals vs trees in backgrounds for variables"""
	
	sh = {}
	bh = {}
	for var in variables:
		minval = MVA2.common.find_min_in_trees(signals.keys() + backgrounds.keys(), var)
		maxval = MVA2.common.find_max_in_trees(signals.keys() + backgrounds.keys(), var)
		sh[var] = ROOT.TH1F("sh_"+var, var+" distribution for signal", nbins, minval, maxval)
		bh[var] = ROOT.TH1F("bh_"+var, var+" distribution for background", nbins, minval, maxval)
		if var in ["eta_lj"]:
			for sg in signals.keys():
				sg.Draw("abs("+var+") >>+ sh_"+var, str(signals[sg]))
			for bg in backgrounds.keys():
				bg.Draw("abs("+var+") >>+ bh_"+var, str(backgrounds[bg]))
		else:
			for sg in signals.keys():
				sg.Draw(var+" >>+ sh_"+var, str(signals[sg]))
			for bg in backgrounds.keys():
				bg.Draw(var+" >>+ bh_"+var, str(backgrounds[bg]))
	
	graph = {}
	for var in variables:
		
		graph[var] = ROOT.TGraph(nbins)
		
		# total counts
		nsg = sh[var].GetSumOfWeights()
		nbg = bh[var].GetSumOfWeights()
		
		# accumulating sums
		ssg = 0.0 
		sbg = 0.0
		for i in range(nbins):
			ssg += sh[var].GetBinContent(i)
			sbg += bh[var].GetBinContent(i)
			graph[var].SetPoint(i, 1.0 - ssg/nsg, sbg/nbg)
	
	
	canvas = ROOT.TCanvas("canv_"+name, "ROC curves", 650, 650)
	canvas.SetGrid()
	canvas.SetTicks()
	
	index = {}
	ngraph = 0
	for var in variables:
		ngraph += 1
		index[var] = ngraph
		graph[var].SetLineColor(ngraph)
		graph[var].SetLineWidth(2)
		#graph[var].Draw("AC SAME")
		if ngraph == 1:
			graph[var].Draw("AL")
			graph[var].GetXaxis().SetTitle("signal efficiency")
			graph[var].GetYaxis().SetTitle("background rejection")
			graph[var].GetXaxis().CenterTitle()
			graph[var].GetYaxis().CenterTitle()
			graph[var].SetTitle(title)
		else:
			graph[var].Draw("L SAME")
			
	
	legend = ROOT.TLegend(0.13, 0.13, 0.35, 0.35)
	for var in variables:
		legend.AddEntry(graph[var], var, "LP")
	legend.Draw()
	
	
	img = ROOT.TImage.Create()
	img.FromPad(canvas)
	img.WriteImage('ROC_'+name+".png")
	
	


