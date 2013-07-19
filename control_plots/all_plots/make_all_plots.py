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
from plots.common.utils import lumi_textbox
from plots.common.odict import OrderedDict
from plots.common.sample import Sample
from plots.common.cuts import Cuts,Cut
from plots.common.legend import *
from plots.common.sample_style import Styling
from plots.common.plot_defs import *
import plots.common.pretty_names as pretty_names
from plots.common.utils import merge_cmds, merge_hists
import random
from array import array

import plots.common.tdrstyle as tdrstyle
tdrstyle.tdrstyle()

datadirs = dict()

# reduce chatter
import logging
logging.basicConfig(level=logging.INFO)

# Declare which data we will use
step3 = os.environ['STPOL_DIR']+'/step3_mva/'
data_fn = 'Single'+proc.title()
del merge_cmds['data']
flist=sum(merge_cmds.values(),[])
tree='Events_MVA'

mc_sf=1.
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
keylist=plot_defs.keys()
if len(sys.argv) == 3:
    keylist=[sys.argv[2]]

for pd in keylist:
    if not plot_defs[pd]['enabled'] and len(keylist) > 1:
        continue
    var = plot_defs[pd]['var']
    cut = None
    if proc == 'ele':
        cut = plot_defs[pd]['elecut']
    if proc == 'mu':
        cut = plot_defs[pd]['mucut']

    cut_str = str(cut)
    weight_str = "SF_total"

    plot_range = plot_defs[pd]['range']
    hist_qcd = None
    for name, sample in samples.items():
        print "Starting:",name
        if sample.isMC:
            hist = sample.drawHistogram(var, cut_str, weight=weight_str, plot_range=plot_range)
            hist.hist.Scale(sample.lumiScaleFactor(lumi)*mc_sf)
            hists_mc[sample.name] = hist.hist
            Styling.mc_style(hists_mc[sample.name], sample.name)
        elif name[0:6] == "Single":
            hist_data = sample.drawHistogram(var, cut_str, weight="1.0", plot_range=plot_range).hist
            hist_data.SetTitle('Data')
            Styling.data_style(hist_data)

        elif name == "data_aiso" and plot_defs[pd]['estQcd'] and proc == 'ele':
            cv='mu_iso'
            lb=0.3
            if proc == 'ele':
                cv='el_reliso'
                lb=0.1
            qcd_cut = cut*Cut('deltaR_lj>0.3 && deltaR_bj>0.3 && '+cv+'>'+str(lb)+' & '+cv+'<0.5')
            hist_qcd = sample.drawHistogram(var, str(qcd_cut), weight="1.0", plot_range=plot_range).hist
            hist_qcd.Scale(qcdScale[proc][plot_defs[pd]['estQcd']])
            hists_mc['QCD'] = hist_qcd
            hists_mc['QCD'].SetTitle('QCD')
            Styling.mc_style(hists_mc['QCD'], 'QCD')

    #Combine the subsamples to physical processes
    add=[]
    if hist_qcd:
        add=[hist_qcd]
    merged_hists = add+merge_hists(hists_mc, merge_cmds).values()
    leg = legend([hist_data]+merged_hists, legend_pos=plot_defs[pd]['labloc'], style=['p','f'])

    #Create the dir if it doesn't exits
    try:
        os.mkdir("out_"+proc)
    except OSError:
        pass

    yf = open('out_'+proc+'/'+pd+'.yield','w')
    htot = ROOT.TH1F('htot'+pd,'htot'+pd,plot_range[0],plot_range[1],plot_range[2])
    htot.Sumw2()
    #Some printout
    for h in merged_hists + [hist_data]:
        print h.GetName(), h.GetTitle(), h.Integral()
        error = array('d',[0])
        tot=h.IntegralAndError(0,plot_range[0]+2,error)
        err=error[0]
        outtxt='{0}\t{1:.2f} +- {2:.2f}\n'.format(h.GetTitle(),tot,err)
        yf.write(outtxt)
        if h.GetTitle() != 'Data':
            htot.Add(h)

    error = array('d',[0])
    tot=htot.IntegralAndError(0,plot_range[0]+2,error)
    err=error[0]
    outtxt='MC total\t{0:.2f} +- {1:.2f}\n'.format(tot,err)
    yf.write(outtxt)
    yf.close()

    canv = ROOT.TCanvas()

    stacks_d = OrderedDict()
    stacks_d["mc"] = merged_hists #+[hist_qcd]
    stacks_d["data"] = [hist_data]
    #xlab = 'cos #theta'
    #ylab = 'N / 0.1'
    xlab = plot_defs[pd]['xlab']
    ylab = 'N / '+str((1.*(plot_range[2]-plot_range[1])/plot_range[0]))
    if plot_defs[pd]['gev']:
        ylab+=' GeV'
    stacks = plot_hists_stacked(canv, stacks_d, x_label=xlab, y_label=ylab, max_bin_mult = 1.5, do_log_y = plot_defs[pd]['log'])
    boxloc = 'top-right'
    if plot_defs[pd]['labloc'] == 'top-right':
        boxloc = 'top-left'
    lbox = lumi_textbox(lumi,boxloc)
    lbox.Draw()
    leg.Draw()
    canv.Draw()
    
    canv.SaveAs('out_'+proc+'/'+pd+'.png')
