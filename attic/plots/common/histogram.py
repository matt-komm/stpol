#!/usr/bin/env python
"""
Some histogram utility functions
"""
from utils import mkdir_p, escape
from utils import filter_alnum
from cross_sections import xs as sample_xs_map

import rootpy
from rootpy.io.file import File

import re, copy

import logging
logger = logging.getLogger(__name__)

import ROOT


def norm(hist, setName=False):
    integral, err = calc_int_err(hist)
    if integral>0:
        if setName:
            hist.SetTitle(hist.GetTitle() + " I=%.2E #pm %.1E" % (integral, err))
        hist.Scale(1.0/integral)
    else:
        logger.error("Histogram integral was 0: %s" % hist.GetName())

def calc_int_err(hist):
    err = ROOT.Double()
    integral = hist.IntegralAndError(1, hist.GetNbinsX(), err)
    return (integral, err)

def sum_err(hist):
    return sum([y for y in hist.yerravg()])

def unique_name(var, cut, weight):
    cut_str = cut if cut is not None else "NOCUT"
    weight_str = weight if weight is not None else "NOWEIGHT"
    return filter_alnum(var + "_" + cut_str + "_" + weight_str)

##DEPRECATED

# class HistMetaData:
#     def __init__(self, **kwargs):
#         for k, v in kwargs.items():
#             setattr(self, k, v)

#     def __str__(self):
#         s = ""
#         for k, v in self.__dict__.items():
#             s += " %s: %s," %(k, v)
#         return s[:-1]

# class HistCollection:
#     """
#     A class that manages saving and loading a collection of histograms to and from the disk.
#     """
#     def __init__(self, hists, metadata={}, name="coll", fi=None):
#         self.name = name
#         self.hists = copy.deepcopy(hists)
#         self.metadata = metadata
#         for k, v in self.hists.items():
#             if k not in self.metadata.keys():
#                 self.metadata[k] = HistMetaData()
#         self.fi = fi
#         logger.debug("Created HistCollection with name %s, hists %s" % (name, str(hists)))

#     # def __del__(self):
#     #     if self.fi:
#     #         logger.debug("Closing file %s of HistCollection" % self.fi.GetPath())
#     #         self.fi.Close()

#     def get(self, hname):
#         return self.hists[hname], self.metadata[hname]

#     def save(self, out_dir):
#         """
#         Saves this HistCollection to files out_dir/hists__{name}.root and out_dir/hists__{name}.pickle.
#         The root file contains the histograms, while the .pickle file contains the histogram metadata.
#         The out_dir is created if it doesn't exist.
#         The TFile will have a directory structure corresponding to the '/'-separated keys of the input dictionary,
#         so hists["A/B/C"] = TH1F("myhist", ...) => TFile.Get("A/B/C/myhist"))

#         out_dir - a string indicating the output directory
#         """
#         mkdir_p(out_dir) #recursively create the directory
#         histo_file = out_dir + "/%s.root" % escape(self.name)
#         fi = File(histo_file, "RECREATE")
#         if not fi:
#             raise Exception("Couldn't open file for writing")
#         logger.info("Saving histograms to ROOT file %s" % histo_file)
#         hists = copy.deepcopy(self.hists)
#         for hn, h in hists.items():
#             dirn = "/".join(hn.split("/")[:-1])
#             fi.cd()
#             try:
#                 d = fi.Get(dirn)
#             except rootpy.io.DoesNotExist:
#                 d = fi.mkdir(dirn, recurse=True)
#             d.cd()
#             h.SetName(hn.split("/")[-1])
#             h.SetDirectory(d)
#             #md.hist_path = h.GetPath()

#         mdpath = histo_file.replace(".root", ".pickle")
#         logger.info("Saving metadata to pickle file %s" % mdpath)
#         pickle.dump(self.metadata, open(mdpath, "w"))
#         fi.Write()
#         fi.Close()
#         return

#     @staticmethod
#     def load(fname):
#         fi = File(fname)
#         name = re.match(".*/(.*)\.root", fname).group(1)
#         logger.info("Opened file %s" % fi.GetPath())
#         metadata = pickle.load(open(fname.replace(".root", ".pickle")))
#         hists = {}
#         for path, dirs, hnames in fi.walk():
#             if len(hnames)>0:
#                 for hn in hnames:
#                     if path:
#                         hname = path + "/" + hn
#                     else:
#                         hname = hn
#                     logger.debug("Getting %s" % hname)
#                     hists[hname] = fi.Get(hname)

#                     md = metadata[hname]
#         return HistCollection(hists, metadata, name, fi)
