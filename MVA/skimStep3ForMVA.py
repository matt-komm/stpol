#!/bin/env python
from ROOT import TFile,TTree,TObject
from plots.common.utils import *
from plots.common.cuts import Cuts
from plots.common.plot_defs import cutlist
import sys

if len(sys.argv) < 2:
    print "Usage: skimStep3ForMVA.py dir_containing_root_files"
    sys.exit(1)

dir=sys.argv[1]

prt = 'el'
proc = 'ele'
if '/mu/' in dir:
    prt = 'mu'
    proc = 'mu'

physics_processes = PhysicsProcess.get_proc_dict(lepton_channel=proc)
merge_cmds = PhysicsProcess.get_merge_dict(physics_processes)

if len(sys.argv) == 3:
    flist=[dir+'/'+sys.argv[2]]
else:
    flist=get_file_list(merge_cmds,sys.argv[1])

cut = str(cutlist['2j1t']*cutlist['presel_ele']*Cuts.met)
if '/mu/' in dir:
    cut = str(cutlist['2j1t']*cutlist['presel_mu']*Cuts.mt_mu)

for f in flist:
    print "Starting:",f
    tf=TFile(f,'UPDATE')
    t=tf.Get("trees/Events")
    t.AddFriend('trees/WJets_weights')
    print cut
    ct=t.CopyTree(cut)
    print t, ct
    print t.GetEntries(), ct.GetEntries()
    ct.SetName("Events_MVAwQCD")
    tf.cd("trees")
    ct.Write("", TObject.kOverwrite)
    tf.Close()
