#!/bin/env python
import sys, os
import ROOT
from plots.common.cuts import Cuts
from plots.common.sample import Sample
from plots.common.utils import merge_cmds, merge_hists
from array import *

if len(sys.argv) < 3:
    print "use: python add_iso_shapesys_weight.py intree.root lepton_channel"
    sys.exit(1)

infile = sys.argv[1]
lepton_channel = sys.argv[2]

step3 =  os.environ['STPOL_DIR'] + "/step3_aug22/" + lepton_channel
#step3 =  os.environ['STPOL_DIR'] + "/test_trees"

#indir_mc = "/".join((step3, lepton_channel,"mc","iso","nominal","Jul15"))
indir_mc = step3

if lepton_channel == "mu":
    iso = "mu_iso"

if lepton_channel == "ele":
    iso = "el_iso"

input = indir_mc + "/" + infile
print "Opening input file: " + input
f = ROOT.TFile(input,"UPDATE")

t = f.Get("trees/Events")
f.cd('trees')
wt = ROOT.TTree("iso_shapesys_weights","iso_shapesys_weights")

t.SetBranchStatus("*",0)
t.SetBranchStatus(iso,1)
isoref = array('f',[0])
t.SetBranchAddress(iso, isoref)
#t.AddBranchToCache(iso,ROOT.kTRUE)

iso_weight_ref = array('f',[0])
branch = wt.Branch("iso_shapesys_weight",iso_weight_ref,"iso_shapesys_weight" + "/F")

for i in range(t.GetEntries()):
 #   t.LoadTree(i)
    t.GetEntry(i)
    lep_iso = isoref[0]

    if lepton_channel == "ele":
        if lep_iso >= 0 and lep_iso < 0.015:
            iso_weight = 1.07
        elif lep_iso >= 0.015 and lep_iso < 0.05:
            iso_weight = 1.17
        elif lep_iso > 0.05:
            iso_weight = 1.22
        else:
            iso_weight = 0.0

    if lepton_channel == "mu":
        if lep_iso >= 0 and lep_iso < 0.015:
            iso_weight = 1.05
        elif lep_iso >= 0.015 and lep_iso < 0.05:
            iso_weight = 1.04
        elif lep_iso > 0.05:
            iso_weight = 1.12
        else:
            iso_weight = 0.0
    
    iso_weight_ref[0] = iso_weight
    if i % 50000 == 0:
        print "Processing event nr: " + str(i)
        print "iso_weight = " + str(iso_weight)
    wt.Fill()

wt.Write('', ROOT.TObject.kOverwrite)
print "Finished filling tree in " + infile
f.Close

