#!/usr/bin/env python


#Need to do basicConfig before doing any other logger commands in python 2.6
#to prevent the other loggers from not recognizing levels set here
import sys

import logging

#FIXME: make this part nicer
level = logging.WARNING
if "--DEBUG" in sys.argv:
    sys.argv.pop(sys.argv.index("--DEBUG"))
    level=logging.DEBUG
logging.basicConfig(level=level)

import os

import argparse
import ROOT
ROOT.gROOT.SetBatch(True)
import plots
from plots.common.stack_plot import plot_hists_stacked
from plots.common.odict import OrderedDict
from plots.common.sample import Sample
from plots.common.legend import *
from plots.common.sample_style import Styling
from plots.common.hist_plots import plot_data_mc_ratio
from plots.common.plot_defs import *
import plots.common.pretty_names as pretty_names
from plots.common.histogram import calc_int_err
from plots.common.utils import *
from plots.common.data_mc import data_mc_plot
from plots.common.cuts import Weights
import random
from array import array
import plots.common.tdrstyle as tdrstyle
import rootpy
import numpy
import re

from plots.common.output import OutputFolder
from plots.common.metainfo import PlotMetaInfo
from plots.common.cross_sections import lumis as xslumis

from rootpy.extern.progressbar import *

logger = logging.getLogger("make_all_plots")

#FIXME: take the lumis from a central database
lumis = {
    "mu": xslumis["83a02e9_Jul22"]["iso"]["mu"],
    "ele": xslumis["83a02e9_Jul22"]["iso"]["ele"]
}

def yield_string(h, hn=None):
    """
    Returns the yield of a Hist in a human-readable format.

    Args:
        h: a Hist of the yield to process

    Keywords:
        hn: the name of the process to be printed.

    Returns: the final yield string
    """
    if not hn:
        hn = hn.GetTitle()
    _int, _err = calc_int_err(h)
    return "%s | %.2f | %.2f\n" % (hn, _int, _err)

def save_yield_table(hmerged_mc, hdata, ofdir, name):
    """
    Saves the yield table of the total MC and data histograms.

    Args:
        hmerged_mc: a dictionary with (str, Hist) of the Monte Carlo histograms
        hdata: a Hist with data
        ofdir: the output directory for the yield table file
        name: the name of the yield table file, without a suffix

    Returns: nothing
    """
    with open(os.path.join(ofdir, name+".yield"), "w") as ofi:
        hsum = None
        for hn, h in hmerged_mc.items():
            if hn is "data":
                continue
            ofi.write(yield_string(h, hn))
            if not hsum:
                hsum = h
            else:
                hsum += h
        ofi.write(yield_string(hsum, "MC"))
        ofi.write(yield_string(hdata, "data"))

        for procname, hist in merged_hists.items():
            try:
                hist.SetTitle(physics_processes[procname].pretty_name)
            except KeyError:
            #QCD does not have a defined PhysicsProcess but that's fine because
            #we take it separately
                pass

def change_syst(paths, dest):
    """
    A crude way to change the MC samples from nominal to a specific systematic
    run.

    Args:
        paths: a list with the filesystem paths to change.
        dest: the destination systematics.

    Returns: a list with the changed paths.
    """
    return map(lambda x: x.replace("nominal", dest) if "nominal" in x else x, paths)

def total_syst(hnominal, hists, corr=None):
    #FIXME: implement addition of correlated histograms
    if not corr:
        corr = numpy.identity(len(hists))

    bins_nom = numpy.array(hnominal.y())
    bins_syst = map(numpy.array, map(lambda h: h.y(), hists))
    bins_diff = map(lambda b: b-bins_nom, bins_syst)



if __name__=="__main__":
    logger.setLevel(logging.DEBUG)

    tdrstyle.tdrstyle()

    parser = argparse.ArgumentParser(
        description='Creates the final plots'
    )
    parser.add_argument(
        "-c",
        "--channel", type=str, required=False, choices=["mu", "ele"], action="append", dest="channels", default=None,
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
        "--cluster", required=False, default=False, action="store_true", dest="cluster",
        help="Do you want to run on the cluster, suppressing PNG output?"
    )

    parser.add_argument(
        "--new", required=False, default=False, action="store_true", dest="new",
        help="Do you want to create a fresh output directory?"
    )

    parser.add_argument(
        "--systs", required=False, default=None, action="store", dest="syst",
        help="A comma separated list of the systematic variations that you want to consider on the ratio plot"
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

    #Do both channels by default
    if not args.channels:
        args.channels = ["mu", "ele"]

    output_folder = OutputFolder(
        os.path.join(os.environ["STPOL_DIR"],"out", "plots"),
        subpath="make_all_plots",
        overwrite=False,
        unique_subdir=args.new,
        skip_png=args.cluster
    )
    logger.info("Output folder is %s" % output_folder.out_folder)

    #FIXME: factorize
    #Check if any of the provided hashtags matches any of the (optional) hashtags of the plot defs
    args.plots += [k for (k, v) in plot_defs.items() if 'tags' in v.keys() and len(set(args.tags).intersection(set(v['tags'])))>0]
    #Remove plots with disabled tags
    disabled_tags = map(lambda x: x[1:], filter(lambda x: x.startswith("."), args.tags))
    for n, plotname in plot_defs.items():
        if 'tags' in plotname.keys() and len(set(disabled_tags).intersection(set(plotname['tags'])))>0:
            args.plots = filter(lambda x: x!=n, args.plots)

    #If there are no plots defined, do all of them
    if len(args.tags)==0 and len(args.plots) == 0:
        args.plots = plot_defs.keys()
        logging.info("No plots specified, plotting everything")
    logger.info("Plotting: %s" % str(args.plots))

    #Do the progress bar
    pbar = None
    nplot = 0
    if args.quiet:
        logger.setLevel(logging.ERROR)
        widgets = [Percentage(), ' ', Bar(marker=RotatingMarker()), ' ', ETA()]
        pbar = ProgressBar(
            widgets=["Projecting histograms"] + widgets,
            maxval=len(args.plots)*len(args.channels)
        ).start()

    tree = args.tree

    #The enabled systematic up/down variation sample prefixes to put on the ratio plot
    systs = {
        "JES": ["EnUp", "EnDown"],
        "JER": ["ResUp", "ResDown"],
        "MET": ["UnclusteredEnUp", "UnclusteredEnDown"],
    }

    for lepton_channel in args.channels:
        logger.info("Plotting lepton channel %s" % lepton_channel)

        weight = Weights.total(lepton_channel)*Weights.wjets_madgraph_shape_weight()*Weights.wjets_madgraph_flat_weight()

        physics_processes = PhysicsProcess.get_proc_dict(lepton_channel=lepton_channel)#Contains the information about merging samples and proper pretty names for samples
        merge_cmds = PhysicsProcess.get_merge_dict(physics_processes) #The actual merge dictionary

        lumi = lumis[lepton_channel]

        #Get the file lists
        flist = get_file_list(
            merge_cmds,
            args.indir + "/%s/mc/iso/nominal/Jul15/" % lepton_channel
        )
        for iso in ['iso', 'antiiso']:
            for ds in ['Jul15', 'Aug1']:
                flist += get_file_list(
                    merge_cmds,
                    args.indir + "/%s/data/%s/%s/" % (lepton_channel, iso, ds)
                )
        if len(flist)==0:
            raise Exception("Couldn't open any files. Are you sure that %s exists and contains root files?" % args.indir)

        samples={}
        for f in flist:
            samples[f] = Sample.fromFile(f, tree_name=tree)

        samples_syst = {}
        for name, syst in systs.items():
            samples_syst[name] = {}
            for s in syst:
                samples_syst[name][s] = {}
                for f in change_syst(flist, s):
                    samples_syst[name][s][f] = Sample.fromFile(f, tree_name=tree)

        for plotname in args.plots:

            plot_def = plot_defs[plotname]

            canv, merged_hists, htot_mc, htot_data = data_mc_plot(samples, plot_def, plotname, lepton_channel, lumi, weight, physics_processes)

            #Draw the histograms from systematically variated samples
            hists_tot_mc_syst_up = {}
            hists_tot_mc_syst_down = {}
            for name, samps in samples_syst.items():
                pdb.set_trace()
                _canv, _merged_hists, _htot_mc, _htot_data = data_mc_plot(samps, plot_def, plotname, lepton_channel, lumi, weight, physics_processes)
                chi2 = htot_mc.Chi2Test(_htot_mc, "WW CHI2/NDF")
                logger.info("Chi2 between nominal and %s is %.2f" % (syst, chi2))
                if "Up" in syst:
                    hists_tot_mc_syst_up[syst] = _htot_mc
                elif "Down" in syst:
                    hists_tot_mc_syst_down[syst] = _htot_mc
                else:
                    raise ValueError("Unhandled systematic " + syst)

            #Draw the ratio plot with
            do_norm = plot_def.get("normalize", False)
            if not do_norm:
                logger.warning("FIXME: Only the first systematic is taken into account at the moment")
                if len(hists_tot_mc_syst_up.values())==1 and len(hists_tot_mc_syst_down.values())==1:
                    hsyst_up = hists_tot_mc_syst_up.values()[0]
                    hsyst_down = hists_tot_mc_syst_down.values()[0]
                    syst_hists = (hsyst_up, hsyst_down)
                else:
                    syst_hists = None
                ratio_pad, hratio = plot_data_mc_ratio(canv, htot_data, htot_mc, syst_hists=syst_hists)

            #This is adopted in the AN
            if lepton_channel=="ele":
                _lepton_channel = "el"
            else:
                _lepton_channel = "mu"

            subpath = ""
            if "dir" in plot_def.keys():
                subpath = plot_def["dir"]

            #Set the plot metadata
            comments = ""
            comments = " chi2=%.2f" % htot_data.Chi2Test(htot_mc, "UW CHI2/NDF")
            if "fitpars" in plot_def.keys():
                comments += " fitpars=" + str(plot_def["fitpars"])
            pinfo = PlotMetaInfo(
                plotname + "_" + _lepton_channel,
                plot_def[lepton_channel + "cut"],
                str(weight),
                flist,
                subpath,
                comments
            )

            output_folder.savePlot(canv, pinfo)
            save_yield_table(merged_hists, htot_data, output_folder.get("yields/%s" % _lepton_channel), plotname)

            canv.Close() #Need to Close to prevent hang from ROOT because of multiple TPads etc
            del canv

            nplot += 1
            if pbar: pbar.update(nplot)

    if pbar: pbar.finish()

