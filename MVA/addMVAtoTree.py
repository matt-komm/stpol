#!/bin/env python
from ROOT import *
from plots.common.utils import *
import sys
from array import array

if len(sys.argv) < 2:
        print "Usage: addMVAtoTree.py dir_containing_root_files"
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

# Create reader and relate variables
reader = TMVA.Reader()
varlist = ['top_mass','eta_lj','C','met','mt_'+prt,'mass_bj','mass_lj','bdiscr_bj','bdiscr_lj',prt+'_pt',prt+'_charge','pt_bj']
speclist = ['cos_theta']
vars={}
for v in varlist:
    vars[v] = array('f',[0])
    reader.AddVariable( v, vars[v] )

for s in speclist:
    vars[s] = array('f',[0])
    reader.AddSpectator( s, vars[s] )

# Book the MVA's
mvalist = [ 'BDT', 'BDT_stop']
mva={}
for m in mvalist:
    reader.BookMVA(m,"weights/stop_"+proc+"_"+m+".weights.xml")
    mva[m] = array('f',[0])

# Run over files and add all the MVA's to the trees
for f in flist:
    print "Starting:",f
    tf=TFile(f,'UPDATE')
    t=tf.Get("trees/Events_MVA")
    branch={}
    for v in varlist+speclist:
        t.SetBranchAddress(v,vars[v])
    for m in mvalist:
        branch[m]=t.Branch('mva_'+m,mva[m],'mva_'+m+'/F')
    for i in range(t.GetEntries()):
        t.GetEntry(i)
        for m in mvalist:
            mva[m][0] = reader.EvaluateMVA(m)
            branch[m].Fill()
    tf.cd('trees')
    t.Write('',TObject.kOverwrite)
    tf.Close()

