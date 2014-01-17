#!/usr/bin/env python
import pandas
import ROOT
import numpy
import sys
import os

infile = sys.argv[1]
outfile = sys.argv[2]
varname = os.path.basename(infile).split(".")[0]
df = pandas.read_csv(infile)

cols = df.columns

hists = {}

for c in cols:
    ns = c.split("__")
    name = ns[0]
    sample = "__".join(ns[1:])
    if not sample in hists.keys():
        hists[sample] = {}
    hists[sample][name] = numpy.array(df[c])

ofi = ROOT.TFile(outfile, "RECREATE")
ofi.cd()
for sample in hists.keys():
    edges = hists[sample]["edges"]
    bins = hists[sample]["bins"]
    errs = hists[sample]["errs"]
    #print(edges)
    #print(bins)
    #print(errs)
    #print(varname, sample)
    hi = ROOT.TH1D(varname + "__" + sample, sample, edges.size-1, edges)
    for i in range(1, edges.size):
        hi.SetBinContent(i, bins[i-1])
        hi.SetBinError(i, errs[i-1])
    hi.Write()
ofi.Close()
