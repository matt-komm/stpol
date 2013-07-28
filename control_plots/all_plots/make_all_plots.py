#!/usr/bin/env python


#Need to do basicConfig before doing any other logger commands in python 2.6
#to prevent the other loggers from not recognizing levels set here
import logging
logging.basicConfig(level=logging.WARNING)

import sys
import os

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
from plots.common.hist_plots import plot_data_mc_ratio
from plots.common.plot_defs import *
import plots.common.pretty_names as pretty_names
from plots.common.histogram import calc_int_err
from plots.common.utils import *
import random
from array import array
import plots.common.tdrstyle as tdrstyle
import rootpy
import numpy
import re

#FIXME: remove this when stable
OLD_PLOTTING = False
try:
    from plots.common.output import OutputFolder
    from plots.common.metainfo import PlotMetaInfo
except Exception as e:
    OLD_PLOTTING=True
    print "Disabling new plotting: %s" % str(e)

from rootpy.extern.progressbar import *

logger = logging.getLogger("make_all_plots")
mc_sf=1.
lumis = {
    "mu": 6784+6398+5277,
    "ele":12410+6144
}


def rescale_to_fit(sample_name, hist, fitpars, ignore_missing=True):
    """
    Rescales the histogram from a sample by the corresponding scale factors.
    Raises a KeyError when there was no match.

    sample_name - the name of the sample, corresponding to the patterns in fitpars
    hist - the Hist to be scaled
    fitpars - a list with tuple contents
        [
            ([patA1, patA2, ...], sfA),
            ([patB1, patB2, ...], sfB),
        ]

    returns - nothing
    """
    for patterns, sf in fitpars:
        for pat in patterns:
            if re.match(pat, sample_name):
                logger.debug("Rescaling sample %s to process %s, sf=%.2f" % (sample_name, pat, sf))
                hist.Scale(sf)
                #We take the first match
                return
    #If we loop through and get here, there was no match
    if not ignore_missing:
        raise KeyError("Couldn't match sample %s to fit parameters!" % sample_name)

if __name__=="__main__":
    logger.setLevel(logging.INFO)
    #logger.getLogger("OutputFolder").setLevel("INFO")

    tdrstyle.tdrstyle()

    #rootpy.log.basic_config_colorized()
    #rootpy.log.setLevel(logging.DEBUG)

    parser = argparse.ArgumentParser(
        description='Creates the final plots'
    )
    parser.add_argument(
        "-c",
        "--channel", type=str, required=True, choices=["mu", "ele"], action="append", dest="channels",
        help="the lepton channel to use"
    )
    parser.add_argument(
        "-i",
        "--indir", type=str, required=False, default=(os.environ["STPOL_DIR"] + "/step3_latest"),
        help="the input directory, which is expected to contain the subdirectories: mu/ele"
    )
    parser.add_argument(
        "-p", "--plots", type=str, required=False, default=[], action='append', choices=plot_defs.keys(),
        help="the plots to draw"
    )
    parser.add_argument(
        "-t", "--tree", type=str, required=False, default="Events", choices=['Events','Events_MVA'],
        help="the tree to use"
    )

    parser.add_argument(
        "-q", "--quiet", required=False, default=False, action="store_true", dest="quiet",
        help="Do you want to suppress most of the output?"
    )

    parser.add_argument(
        "--new", required=False, default=False, action="store_true", dest="new",
        help="Do you want to create a fresh output directory?"
    )

    parser.add_argument(
        "-T", "--tags", type=str, required=False, default=[], action='append',
        help="""
        The plotting tags to enable.
        Any plot_def that has an element in 'tags' that is also in this set will get plotted.
        You can explicitly disable tags by prepending a dot(.), this overrides any enables.
        """
    )

    args = parser.parse_args()

    if not OLD_PLOTTING:
        output_folder = OutputFolder(
            os.path.join(os.environ["STPOL_DIR"],"out", "plots"),
            subpath="make_all_plots",
            overwrite=False,
            unique_subdir=args.new
        )
        logger.info("Output folder is %s" % output_folder.out_folder)

    #Check if any of the provided hashtags matches any of the (optional) hashtags of the plot defs
    args.plots += [k for (k, v) in plot_defs.items() if 'tags' in v.keys() and len(set(args.tags).intersection(set(v['tags'])))>0]
    #Remove plots with disabled tags
    disabled_tags = map(lambda x: x[1:], filter(lambda x: x.startswith("."), args.tags))
    for n, pd in plot_defs.items():
        if 'tags' in pd.keys() and len(set(disabled_tags).intersection(set(pd['tags'])))>0:
            args.plots = filter(lambda x: x!=n, args.plots)

    #If there are no plots defined, do all of them
    if len(args.plots) == 0:
        args.plots = plot_defs.keys()
        logging.info("No plots specified, plotting everything")
    logger.info("Plotting: %s" % str(args.plots))

    pbar = None
    if args.quiet:
        logger.setLevel(logging.ERROR)
        widgets = [Percentage(), ' ', Bar(marker=RotatingMarker()), ' ', ETA()]
        pbar = ProgressBar(
            widgets=["Projecting histograms"] + widgets,
            maxval=len(args.plots)*len(args.channels)
        ).start()

    tree = args.tree
    datadirs = dict()

    # Declare which data we will use
    step3 = args.indir

    nplot = 0
    for proc in args.channels:
        logger.info("Plotting lepton channel %s" % proc)

        lumi = lumis[proc]

        physics_processes = PhysicsProcess.get_proc_dict(lepton_channel=proc)#Contains the information about merging samples and proper pretty names for samples
        merge_cmds = PhysicsProcess.get_merge_dict(physics_processes) #The actual merge dictionary

        #Get the file lists
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

            plot_def = plot_defs[pd]
            logger.info('Plot in progress %s' % pd)

            if not (plot_def["enabled"]):
                continue

            if 'mva' in pd and not 'MVA' in tree:
                continue

            var = plot_def['var']


            if not isinstance(var, basestring):
                if proc == 'ele':
                    var = var[0]
                else:
                    var = var[1]

            cut = None
            if proc == 'ele':
                cut = plot_def['elecut']
            elif proc == 'mu':
                cut = plot_def['mucut']

            cut_str = str(cut)
            weight_str = str(Weights.total(proc) *
                Weights.wjets_madgraph_shape_weight() *
                Weights.wjets_madgraph_flat_weight())

            plot_range = plot_def['range']

            hists_mc = dict()
            hists_data = dict()
            for name, sample in samples.items():
                logger.debug("Starting to plot %s" % name)
                if sample.isMC:
                    hist = sample.drawHistogram(var, cut_str, weight=weight_str, plot_range=plot_range)
                    hist.Scale(sample.lumiScaleFactor(lumi))
                    hists_mc[sample.name] = hist
                    Styling.mc_style(hists_mc[sample.name], sample.name)

                    if "fitpars" in plot_def.keys():
                        rescale_to_fit(sample.name, hist, plot_def["fitpars"])
                elif "antiiso" in name and plot_def['estQcd']:

                    #FIXME: it'd be nice to move the isolation cut to plots/common/cuts.py for generality :) -JP
                    cv='mu_iso'
                    lb=0.3
                    if proc == 'ele':
                        cv='el_iso'
                        lb=0.1
                    qcd_cut = cut*Cuts.deltaR(0.5)*Cut(cv+'>'+str(lb)+' & '+cv+'<0.5')


                    #FIXME: It would be nice to factorise this part a bit (separate method?) or make it more clear :) -JP
                    region = '2j1t'
                    if plot_def['estQcd'] == '2j0t': region='2j0t'
                    if plot_def['estQcd'] == '3j1t': region='3j1t'
                    qcd_loose_cut = cutlist[region]*cutlist['presel_'+proc]*Cuts.deltaR(0.5)*Cut(cv+'>'+str(lb)+' & '+cv+'<0.5')
                    logger.debug('QCD loose cut: %s' % str(qcd_loose_cut))
                    hist_qcd = sample.drawHistogram(var, str(qcd_cut), weight="1.0", plot_range=plot_range)
                    hist_qcd_loose = sample.drawHistogram(var, str(qcd_loose_cut), weight="1.0", plot_range=plot_range)
                    hist_qcd.Scale(qcdScale[proc][plot_def['estQcd']])
                    if hist_qcd_loose.Integral():
                        hist_qcd_loose.Scale(hist_qcd.Integral()/hist_qcd_loose.Integral())
                    sampn = "QCD"+sample.name

                    #Rescale the QCD histogram to the eta_lj fit
                    if "fitpars" in plot_def.keys():
                        rescale_to_fit(sampn, hist_qcd_loose, plot_def["fitpars"])

                    hists_mc[sampn] = hist_qcd_loose
                    hists_mc[sampn].SetTitle('QCD')
                    Styling.mc_style(hists_mc[sampn], 'QCD')

                #Real ordinary data in the isolated region
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
            if plot_defs[pd]['log']:
                order = PhysicsProcess.desired_plot_order_log+['QCD']
            merged_hists = merge_hists(hists_mc, merge_cmds, order=order)


            #Get the pretty names for the processes from the PhysicsProces.pretty_name variable
            for procname, hist in merged_hists.items():
                try:
                    hist.SetTitle(physics_processes[procname].pretty_name)
                except KeyError: #QCD does not have a defined PhysicsProcess but that's fine because we take it separately
                    pass

            yield_out_dir = "out_" + proc
            #Create the dir if it doesn't exits
            try:
                os.mkdir(yield_out_dir)
            except OSError:
                pass
            yf = open(yield_out_dir+'/%s_%s.yield' % (pd, proc), 'w')
            #htot = ROOT.TH1F('htot'+pd,'htot'+pd,plot_range[0],plot_range[1],plot_range[2])
            #htot.Sumw2()

            if hist_data.Integral()<=0:
                raise Exception("Histogram for data was empty. Something went wrong, please check.")
            #Some printout
            for hn, h in (merged_hists.items() + [("data", hist_data)]):
                #print h.GetName(), h.GetTitle(), h.Integral()
                error = array('d',[0])
                tot, err = calc_int_err(h)
                outtxt='{0} | {1:.2f} | {2:.2f}\n'.format(hn, tot, err)
                yf.write(outtxt)
                #if hn != 'data':
                #    htot.Add(h)
            htot = sum(merged_hists.values())

            #We have a separate method for the error
            tot, err = calc_int_err(htot)
            outtxt='MC | {0:.2f} | {1:.2f}\n'.format(tot,err)
            yf.write(outtxt)
            yf.close()

            chi2 = hist_data.Chi2Test(htot, "UW CHI2/NDF")
            if chi2>20:#FIXME: uglyness
                logger.error("The chi2 between data and MC is large (chi2=%.2f). You may have errors with your samples!" % chi2)
                logger.info("MC  : %s" % " ".join(map(lambda x: "%.1f" % x, list(htot.y()))))
                logger.info("DATA: %s" % " ".join(map(lambda x: "%.1f" % x, list(hist_data.y()))))
                logger.info("diff: %s" % str(
                    " ".join(map(lambda x: "%.1f" % x, numpy.abs(numpy.array(list(htot.y())) - numpy.array(list(hist_data.y())))))
                ))

            merged_hists = merged_hists.values()
            leg = legend([hist_data] + list(reversed(merged_hists)), legend_pos=plot_def['labloc'], style=['p','f'])

            canv = ROOT.TCanvas()

            #Make the stacks
            stacks_d = OrderedDict()
            stacks_d["mc"] = merged_hists
            stacks_d["data"] = [hist_data]

            #label
            xlab = plot_defs[pd]['xlab']
            if not isinstance(xlab, basestring):
                if proc == 'ele':
                    xlab = xlab[0]
                else:
                    xlab = xlab[1]
            ylab = 'N / '+str((1.*(plot_range[2]-plot_range[1])/plot_range[0]))
            if plot_defs[pd]['gev']:
                ylab+=' GeV'
            fact = 1.5
            if plot_defs[pd]['log']:
                fact = 10

            #Make a separate pad for the stack plot
            p1 = ROOT.TPad("p1", "p1", 0, 0.3, 1, 1)
            p1.Draw()
            p1.SetTicks(1, 1);
            p1.SetGrid();
            p1.SetFillStyle(0);
            p1.cd()

            stacks = plot_hists_stacked(p1, stacks_d, x_label=xlab, y_label=ylab, max_bin_mult = fact, do_log_y = plot_defs[pd]['log'])

            #Put the the lumi box where the legend is not
            boxloc = 'top-right'
            if plot_defs[pd]['labloc'] == 'top-right':
                boxloc = 'top-left'
            chan = 'Electron'
            if proc == "mu":
                chan = 'Muon'
            lbox = lumi_textbox(lumi,boxloc,'preliminary',chan+' channel')

            #Draw everything
            lbox.Draw()
            leg.Draw()
            canv.Draw()

            #Draw the ratio plot with
            ratio_pad, hratio, hline = plot_data_mc_ratio(canv, get_stack_total_hist(stacks["mc"]), hist_data)

            #This is adopted in the AN
            if proc=="ele":
                _proc = "el"
            else:
                _proc = "mu"

            out_dir = "figures"
            subpath = ""
            if "dir" in plot_def.keys():
                subpath = plot_def["dir"]
            out_dir = os.path.join(out_dir, subpath, "out_{0}".format(proc))
            fname = os.path.join(out_dir, "{0}_{1}.png".format(pd, _proc))

            try:
                os.makedirs(out_dir)
            except:
                pass

            logging.info("Saving %s" % fname)
            canv.SaveAs(fname)
            canv.SaveAs(fname.replace(".png", ".pdf"))

            comments = " chi2=%.2f" % chi2
            if "fitpars" in plot_def.keys():
                comments += " fitpars=" + str(plot_def["fitpars"])
            if not OLD_PLOTTING:
                pinfo = PlotMetaInfo(
                    pd + "_" + _proc,
                    cut,
                    weight_str,
                    flist,
                    subpath,
                    comments
                )
                output_folder.savePlot(canv, pinfo)

            canv.Close() #Need to Close to prevent hang from ROOT because of multiple TPads etc
            del canv

            nplot += 1
            if pbar:
                pbar.update(nplot)

    if pbar:
        pbar.finish()

