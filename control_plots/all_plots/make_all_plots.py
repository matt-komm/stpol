#!/usr/bin/env python
import sys
import os

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("make_all_plots")
logger.setLevel(logging.INFO)

import argparse
import ROOT
ROOT.gROOT.SetBatch(True)
import plots
from plots.common.stack_plot import plot_hists_stacked
from plots.common.odict import OrderedDict
from plots.common.sample import Sample
from plots.common.cuts import *
from plots.common.legend import *
from plots.common.sample_style import Styling
from plots.common.plot_defs import *
import plots.common.pretty_names as pretty_names
from plots.common.utils import *
import random
from array import array
import plots.common.tdrstyle as tdrstyle
import rootpy

import pdb

mc_sf=1.
lumis = {
    "mu": 6784+6398+5277,
    "ele":12410+6144
}
if __name__=="__main__":
    tdrstyle.tdrstyle()

    #rootpy.log.basic_config_colorized()

    parser = argparse.ArgumentParser(
        description='Creates the final plots'
    )
    parser.add_argument(
        "--channel", type=str, required=True, choices=["mu", "ele"],
        help="the lepton channel to use"
    )
    parser.add_argument(
        "--indir", type=str, required=False, default=(os.environ["STPOL_DIR"] + "/step3_latest"),
        help="the input directory"
    )
    parser.add_argument(
        "-p", "--plots", type=str, required=False, default=None, action='append', choices=plot_defs.keys(),
        help="the plots to draw"
    )
    parser.add_argument(
        "-t", "--tree", type=str, required=False, default="Events", choices=['Events','Events_MVA'],
        help="the tree to use"
    )

    args = parser.parse_args()
    if args.plots is None:
        args.plots = plot_defs.keys()
    proc=args.channel
    tree = args.tree
    datadirs = dict()

    # Declare which data we will use
    step3 = args.indir

    lumi = lumis[proc]

    merge_cmds = PhysicsProcess.get_merge_dict(lepton_channel=proc)
    flist = get_file_list(
        merge_cmds,
        args.indir + "/%s/mc/iso/nominal/Jul15/" % proc
    )
    flist += get_file_list(
        merge_cmds,
        args.indir + "/%s/data/iso/Jul15/" % proc
    )
    flist += get_file_list(
        {'data':merge_cmds['data']},
        args.indir + "/%s/data/antiiso/Jul15/" % proc
    )
    if len(flist)==0:
        raise Exception("Couldn't open any files. Are you sure that %s exists and contains root files?" % args.indir)

    #Load all the samples in the isolated directory
    samples={}
    for f in flist:
        samples[f] = Sample.fromFile(f, tree_name=tree)

    for pd in args.plots:
        logger.info('Plot in progress %s' % pd)
        if not plot_defs[pd]['enabled'] and len(args.plots) > 1:
            continue
        if 'mva' in pd and not 'MVA' in tree:
            continue
        var = plot_defs[pd]['var']
        cut = None
        if proc == 'ele':
            cut = plot_defs[pd]['elecut']
        elif proc == 'mu':
            cut = plot_defs[pd]['mucut']

        cut_str = str(cut)
        weight_str = str(Weights.total(proc) *
            Weights.wjets_madgraph_shape_weight() *
            Weights.wjets_madgraph_flat_weight())

        plot_range = plot_defs[pd]['range']

        hists_mc = dict()
        hists_data = dict()
        for name, sample in samples.items():
            logger.info("Starting to plot %s" % name)
            if sample.isMC:
                hist = sample.drawHistogram(var, cut_str, weight=weight_str, plot_range=plot_range)
                hist.Scale(sample.lumiScaleFactor(lumi))
                hists_mc[sample.name] = hist
                Styling.mc_style(hists_mc[sample.name], sample.name)
            elif "antiiso" in name and plot_defs[pd]['estQcd']:
                cv='mu_iso'
                lb=0.3
                if proc == 'ele':
                    cv='el_iso'
                    lb=0.1
                qcd_cut = cut*Cuts.deltaR(0.5)*Cut(cv+'>'+str(lb)+' & '+cv+'<0.5')
                qcd_loose_cut = cutlist[plot_defs[pd]['estQcd']]*cutlist['presel_'+proc]*Cuts.deltaR(0.5)*Cut(cv+'>'+str(lb)+' & '+cv+'<0.5')
                logger.info('QCD loose cut: %s' % str(qcd_loose_cut))
                hist_qcd = sample.drawHistogram(var, str(qcd_cut), weight="1.0", plot_range=plot_range)
                hist_qcd_loose = sample.drawHistogram(var, str(qcd_loose_cut), weight="1.0", plot_range=plot_range)
                hist_qcd.Scale(qcdScale[proc][plot_defs[pd]['estQcd']])
                if hist_qcd_loose.Integral():
                    hist_qcd_loose.Scale(hist_qcd.Integral()/hist_qcd_loose.Integral())
                hists_mc["QCD"+sample.name] = hist_qcd_loose
                hists_mc["QCD"+sample.name].SetTitle('QCD')
                Styling.mc_style(hists_mc["QCD"+sample.name], 'QCD')
            elif not "antiiso" in name:
                hist_data = sample.drawHistogram(var, cut_str, weight="1.0", plot_range=plot_range)
                hist_data.SetTitle('Data')
                Styling.data_style(hist_data)
                hists_data[name] = hist_data

        if len(hists_data.values())==0:
            raise Exception("Couldn't draw the data histogram")

        #Combine the subsamples to physical processes
        hist_data = sum(hists_data.values())
        merge_cmds['QCD']=["QCD"+merge_cmds['data'][0]]
        order=['QCD']+PhysicsProcess.desired_plot_order
        merged_hists = merge_hists(hists_mc, merge_cmds, order=order).values()
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
        stacks_d["mc"] = merged_hists 
        stacks_d["data"] = [hist_data]
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
