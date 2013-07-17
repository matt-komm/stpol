#!/usr/bin/env python
import sys
import os

if len(sys.argv) < 2: 
    print "Usage: ./make_all_plots.py <ele/mu>"
    sys.exit(1)
proc = sys.argv[1]

import ROOT
import plots
from plots.common.stack_plot import plot_hists_stacked
from plots.common.odict import OrderedDict
from plots.common.sample import Sample
from plots.common.cuts import Cuts
from plots.common.legend import *
from plots.common.sample_style import Styling
import plots.common.pretty_names as pretty_names
from plots.common.utils import merge_cmds, merge_hists
import random

import plots.common.tdrstyle as tdrstyle
tdrstyle.tdrstyle()

datadirs = dict()

# reduce chatter
import logging
logging.basicConfig(level=logging.INFO)

# Declare which data we will use
step3 = os.environ['STPOL_DIR']+'/step3_new/'
data_fn = 'Single'+proc.title()
del merge_cmds['data']
flist=sum(merge_cmds.values(),[])
tree='Events'
from plot_defs import plot_defs

lumiele=6144
lumimu=6398
lumi = lumiele
if proc == 'mu':
    lumi = lumimu

# Load in the data
datadirs["iso"] = "/".join((step3, proc ,"iso", "nominal"))
datadirs["antiiso"] = "/".join((step3, proc ,"antiiso", "nominal"))

#Load all the samples in the isolated directory
samples={}
for f in flist:
    samples[f] = Sample.fromFile(datadirs["iso"]+'/'+f+'.root', tree_name=tree)

samples[data_fn] = Sample.fromFile(datadirs["iso"] + "/" + data_fn + ".root",tree_name=tree)
samples["data_aiso"] = Sample.fromFile(datadirs["antiiso"] + "/" + data_fn + ".root",tree_name=tree)


hists_mc = dict()
hist_data = None

#Define the variable, cut, weight and lumi
for pd in plot_defs.keys():
    if not plot_defs[pd]['enabled']:
        continue
    var = plot_defs[pd]['var']
    cut = plot_defs[pd]['commonCut']
    if proc == 'ele':
        cut *= plot_defs[pd]['elecut']
    if proc == 'mu':
        cut *= plot_defs[pd]['mucut']

    cut_str = str(cut)
    weight_str = "SF_total"

    plot_range = plot_defs[pd]['range']

    for name, sample in samples.items():
        print "Starting:",name
        if sample.isMC:
            hist = sample.drawHistogram(var, cut_str, weight=weight_str, plot_range=plot_range)
            hist.hist.Scale(sample.lumiScaleFactor(lumi))
            hists_mc[sample.name] = hist.hist
            Styling.mc_style(hists_mc[sample.name], sample.name)
        elif name[0:6] == "Single":
            hist_data = sample.drawHistogram(var, cut_str, weight="1.0", plot_range=plot_range).hist
            hist_data.SetTitle('Data')
            Styling.data_style(hist_data)

        elif name == "data_aiso" and plot_defs[pd]['estQcd']:
            hist_qcd = sample.drawHistogram(var, cut_str, weight="1.0", plot_range=plot_range).hist
            hist_qcd.Scale(0.5)
            hists_mc['QCD'] = hist_qcd
            Styling.mc_style(hists_mc['QCD'], 'QCD')

    #Combine the subsamples to physical processes
    merged_hists = merge_hists(hists_mc, merge_cmds).values()
    leg = legend([hist_data]+merged_hists, legend_pos=plot_defs[pd]['labloc'], style=['p','f'])

    #Some printout
    for h in merged_hists + [hist_data]:
        print h.GetName(), h.GetTitle(), h.Integral()

    canv = ROOT.TCanvas()

    stacks_d = OrderedDict()
    stacks_d["mc"] = merged_hists+[hist_qcd]
    stacks_d["data"] = [hist_data]
    #xlab = 'cos #theta'
    #ylab = 'N / 0.1'
    xlab = plot_defs[pd]['xlab']
    ylab = 'N / '+str((1.*(plot_range[2]-plot_range[1])/plot_range[0]))
    if plot_defs[pd]['gev']:
        ylab+=' GeV'
    stacks = plot_hists_stacked(canv, stacks_d, x_label=xlab, y_label=ylab, max_bin_mult = 1.3, do_log_y = plot_defs[pd]['log'])
    leg.Draw()
    canv.Draw()
    
    #Create the dir if it doesn't exits
    try:
        os.mkdir("out_"+proc)
    except OSError:
        pass
    canv.SaveAs('out_'+proc+'/'+pd+'.png')
