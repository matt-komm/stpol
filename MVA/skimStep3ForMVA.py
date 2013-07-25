#!/bin/env python
from ROOT import TFile,TTree
from plots.common.utils import *
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

basecut = 'n_jets == 2 & n_tags == 1 & n_veto_ele == 0 & n_veto_mu == 0 & rms_lj < 0.025 & pt_lj > 40 & pt_bj > 40'
mucut = basecut+' & n_muons == 1 '
elecut = basecut+' & n_eles == 1 '
cut = elecut
if '/mu/' in dir:
    cut = mucut

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

