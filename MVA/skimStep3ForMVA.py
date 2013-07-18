#!/bin/env python
from ROOT import TFile,TTree
from plots.common.utils import merge_cmds
import sys

if len(sys.argv) < 2:
    print "Usage: skimStep3ForMVA.py dir_containing_root_files"
    sys.exit(1)

flist=[]
del merge_cmds['data']
if len(sys.argv) == 3:
    flist=[sys.argv[2]]
else:
    flist=sum(merge_cmds.values(),[])

flist.append('SingleEle')
flist.append('SingleMu')

dir=sys.argv[1]
print "Using:",dir
basecut = 'deltaR_bj > 0.3 & deltaR_lj > 0.3 & n_jets == 2 & n_tags == 1 & n_veto_ele == 0 & n_veto_mu == 0 & rms_lj < 0.025 & pt_lj > 40 & pt_bj > 40'
mucut = basecut+' & n_muons == 1 & mu_pt > 26 '
elecut = basecut+' & n_eles == 1 & el_pt > 30 & ( (HLT_Ele27_WP80_v8 == 1 ) || (HLT_Ele27_WP80_v9 == 1) || (HLT_Ele27_WP80_v10==1) || (HLT_Ele27_WP80_v11==1) )'
cut = elecut
if '/mu/' in dir:
    cut = mucut

for f in flist:
    print "Starting:",f
    tf=TFile(dir+'/'+f+'.root','UPDATE')
    tf.cd("trees")
    t=tf.Get("trees/Events")
    ct=t.CopyTree(cut)
    ct.SetName("Events_MVA")
    ct.Write()
    tf.Close()

