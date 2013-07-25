#!/bin/env python
# Import necessary libraries and data
import os
import sys
from ROOT import *
from copy import copy
from plots.common.sample import Sample
from plots.common.utils import *
from plots.common.colors import sample_colors_same
from plots.common.cross_sections import lumis
from plots.common.cuts import *
from plots.common.plot_defs import qcdScale

if len(sys.argv) < 2: 
    print "Usage: ./trainMVA.py ele/mu"
    sys.exit(1)

proc = sys.argv[1]
# Choose between electron / muon channel fitting
step3_ver="83a02e9_Jul22"
step3 = "/home/mario/Summer13/stpol/step3_new"
lumi=lumis[step3_ver]["iso"][proc]

merge_cmds = PhysicsProcess.get_merge_dict(lepton_channel=proc)
flist = get_file_list(
   merge_cmds,
   step3 + "/%s/mc/iso/nominal/Jul15/" % proc
)
flist += get_file_list(
    {'QCD': merge_cmds['data']},
    step3 + "/%s/data/antiiso/Jul15/" % proc
)

# Read in the file list from the output directory
samples = {}
for f in flist:
    samples[f] = Sample.fromFile(f, tree_name="Events_MVA")

# To compute accurate weight we need to load from the tree also the weights in question
#weightString = str(Weights.total(proc))
# Temporary patch until proper step3 is available
weightString = "1.0"

t={}
f={}
w={}

for key in flist:
    w[key]=1.
    t[key]=samples[key].getTree()
    if samples[key].isMC: 
        w[key]=samples[key].lumiScaleFactor(lumi)
    if 'data' in key and proc=='ele':
        w[key]=qcdScale[proc]['presel']

signal=['T_t_ToLeptons','Tbar_t_ToLeptons']

# Create output file
outf = TFile('TMVA'+proc+'.root','RECREATE')

# Initialize TMVA factory
factory=TMVA.Factory("stop_"+proc,outf,"Transformations=I;N;D")

# Which particle do we use for pt, eta etc
prt='el'
if proc=='mu': prt='mu'

# Let's define what variables we want to use for signal discrimination
factory.AddVariable("top_mass",'D')
factory.AddVariable("eta_lj",'D')
factory.AddVariable("C",'D')
factory.AddVariable("met",'D')
factory.AddVariable("mt_"+prt,'D')
factory.AddVariable("mass_bj",'D')
factory.AddVariable("mass_lj",'D')
factory.AddVariable("bdiscr_bj",'D')
factory.AddVariable("bdiscr_lj",'D')
factory.AddVariable(prt+"_pt",'D')
factory.AddVariable(prt+"_charge",'I')
factory.AddVariable("pt_bj",'D')
factory.AddSpectator("cos_theta",'D')

# Now let's add signal and background trees with proper weights
for k in t.keys():
    print "Adding trees to MVA:",k
    sig = False
    for s in signal:
        if s in k:
            sig = True
    if t[k].GetEntries():
        if sig:
            factory.AddSignalTree(t[k],w[k])
        else:
            factory.AddBackgroundTree(t[k],w[k])

# Define what is used as per-event weight
factory.SetWeightExpression(weightString)

# Prepare training and testing
factory.PrepareTrainingAndTestTree(TCut(),TCut(),
               "NormMode=None:"\
               "NTrain_Signal=20000:"\
               "NTrain_Background=100000:"\
               "V")

# Now let's book an MVA method
factory.BookMethod(TMVA.Types.kBDT,
                   "BDT",
                   "!H:!V:NTrees=2000:BoostType=Grad:Shrinkage=0.1:!UseBaggedGrad:nCuts=2000:nEventsMin=100:NNodesMax=5:UseNvars=4:PruneStrength=5:PruneMethod=CostComplexity:MaxDepth=6"\
                   )

#factory.BookMethod(TMVA.Types.kBDT,
#                   "BDT_stop",
#                   "!H:!V:NTrees=300:BoostType=AdaBoost:SeparationType=GiniIndex:nCuts=-1:PruneMethod=CostComplexity:PruneStrength=1.:NNodesMax=20:MaxDepth=30:AdaBoostBeta=0.2"\
#                  )

factory.TrainAllMethods()
factory.TestAllMethods()
factory.EvaluateAllMethods()

outf.Close()
