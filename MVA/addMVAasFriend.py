#!/bin/env python
from ROOT import *
from plots.common.utils import *
import sys
from array import array

if len(sys.argv) < 2:
        print "Usage: addMVAtoTree.py root file"
        sys.exit(1)

f=sys.argv[1]

prt = 'el'
proc = 'ele'
if '/mu/' in f:
    prt = 'mu'
    proc = 'mu'

# Create reader and relate variables
reader = TMVA.Reader()
varlist = ['top_mass','eta_lj','C','met','mt_'+prt,'mass_bj','mass_lj',prt+'_pt','pt_bj']
speclist = []
vars={}
for v in varlist:
    vars[v] = array('f',[0])
    reader.AddVariable( v, vars[v] )

for s in speclist:
    vars[s] = array('f',[0])
    reader.AddSpectator( s, vars[s] )

# Book the MVA's
mvalist = [ 'BDT']
mva={}
for m in mvalist:
    reader.BookMVA(m,"weights/stop_"+proc+"_"+m+".weights.xml")
    mva[m] = array('f',[0])

# Run over files and add all the MVA's to the trees
print "Starting:",f
tf=TFile(f,'UPDATE')
t=tf.Get("trees/Events")
tf.cd('trees')
mt=TTree("MVA","MVA")
t.SetBranchStatus("*",0)
branch={}
for v in varlist+speclist:
    t.SetBranchStatus(v,1)
    t.SetBranchAddress(v,vars[v])
for m in mvalist:
    branch[m]=mt.Branch('mva_'+m,mva[m],'mva_'+m+'/F')
for i in range(t.GetEntries()):
    t.GetEntry(i)
    for m in mvalist:
        mva[m][0] = reader.EvaluateMVA(m)
        branch[m].Fill()
        mt.Fill()
mt.Write('',TObject.kOverwrite)
tf.Close()

