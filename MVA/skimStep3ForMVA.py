#!/bin/env python
from ROOT import TFile,TTree
from plots.common.utils import *
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

merge_cmds = PhysicsProcess.get_merge_dict(lepton_channel=proc)

if len(sys.argv) == 3:
    flist=[dir+'/'+sys.argv[2]]
else:
    flist=get_file_list(merge_cmds,sys.argv[1])

cut = str(cutlist['2j1t']*cutlist['presel_ele'])
if '/mu/' in dir:
    cut = str(cutlist['2j1t']*cutlist['presel_mu'])

for f in flist:
    print "Starting:",f
    tf=TFile(f,'UPDATE')
    tf.cd("trees")
    t=tf.Get("trees/Events")
    t.AddFriend('trees/WJets_weights')
    ct=t.CopyTree(cut)
    ct.SetName("Events_MVA")
    ct.Write()
    tf.Close()

