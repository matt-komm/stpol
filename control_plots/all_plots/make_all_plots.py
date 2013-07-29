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
from plots.common.legend import *
from plots.common.sample_style import Styling
from plots.common.hist_plots import plot_data_mc_ratio
from plots.common.plot_defs import *
import plots.common.pretty_names as pretty_names
from plots.common.histogram import calc_int_err
from plots.common.utils import *
from plots.common.data_mc import data_mc_plot
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
            canv, merged_hists = data_mc_plot(samples, plot_def, pd, proc, lumi)

            yield_out_dir = "out_" + proc

            # #Create the dir if it doesn't exits
            # try:
            #     os.mkdir(yield_out_dir)
            # except OSError:
            #     pass
            # yf = open(yield_out_dir+'/%s_%s.yield' % (pd, proc), 'w')
            #htot = ROOT.TH1F('htot'+pd,'htot'+pd,plot_range[0],plot_range[1],plot_range[2])
            #htot.Sumw2()

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

            comments = ""
            #comments = " chi2=%.2f" % chi2
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

