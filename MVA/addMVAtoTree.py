#!/bin/env python
from ROOT import *
from plots.common.utils import merge_cmds
import sys
from array import array

if len(sys.argv) < 2:
        print "Usage: addMVAtoTree.py dir_containing_root_files"
        sys.exit(1)

flist=[]
del merge_cmds['data']

if len(sys.argv) == 3:
    flist=[sys.argv[2]]
else:
    flist=sum(merge_cmds.values(),[])

dir=sys.argv[1]
print "Using:",dir

prt = 'el'
sample = 'ele'
if '/mu/' in dir:
    prt = 'mu'
    sample = 'mu'
    flist.append('SingleMu')
else:
    flist.append('SingleEle')


# Create reader and relate variables
reader = TMVA.Reader()
varlist = ['top_mass','eta_lj','C','met','mt_'+prt,'bdiscr_bj','bdiscr_lj',prt+'_pt',prt+'_charge','pt_bj']
speclist = ['cos_theta']
vars={}
for v in varlist:
    vars[v] = array('f',[0])
    reader.AddVariable( v, vars[v] )

for s in speclist:
    vars[s] = array('f',[0])
    reader.AddSpectator( s, vars[s] )

# Book the MVA's
mvalist = [ 'BDT', 'cat4', 'cat2' ]
mva={}
for m in mvalist:
    reader.BookMVA(m,"weights/stop_"+sample+"_"+m+".weights.xml")
    mva[m] = array('f',[0])

# Run over files and add all the MVA's to the trees
for f in flist:
    print "Starting:",f
    tf=TFile(dir+'/'+f+'.root','UPDATE')
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

