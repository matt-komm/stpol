#!/bin/env python
# Import necessary libraries and data
import os
import sys
from ROOT import *
from copy import copy
from plots.common.sample import Sample
from plots.common.utils import merge_cmds
from plots.common.colors import sample_colors_same
from plots.common.cross_sections import lumi_iso,lumi_antiiso

if len(sys.argv) < 2: 
    print "Usage: ./trainMVA.py ele/mu"
    sys.exit(1)

sample = sys.argv[1]
# Choose between electron / muon channel fitting
lumi=lumi_iso[sample]

#sample = "mu"
step3 = "step3_mva"
datadirs={}
datadirs["iso"] = "/".join((os.environ["STPOL_DIR"], step3, sample ,"iso", "nominal"))
datadirs["antiiso"] = "/".join((os.environ["STPOL_DIR"], step3, sample ,"antiiso", "nominal"))

flist=sum(merge_cmds.values(),[])

# Read in the file list from the output directory
samples = {}
for f in flist:
    samples[f] = Sample.fromFile(datadirs["iso"]+'/'+f+'.root', tree_name="Events_MVA")
samples['qcd'] = Sample.fromFile(datadirs['antiiso']+'/Single'+sample.title()+'.root', tree_name="Events_MVA")

# To compute accurate weight we need to load from the tree also the weights in question
weightString = "SF_total"
t={}
f={}
w={}

for key in flist+['qcd']:#samples.keys():
    #for key in klist:
    if key == 'T_t' or key == 'Tbar_t':
        continue
    if sample == "mu" and (key[-5:] == "BCtoE" or key[-10:] == "EMEnriched") or key[0:5] == "GJets":
        continue
    if sample == "ele" and key == "QCDMu":
        continue
    if key[0:6] == "Single":
        if sample == "ele" and key[6:] == "Mu":
            continue
        if sample == "mu" and key[6:] == "Ele":
            continue
    w[key]=1.
    t[key]=samples[key].getTree()
    if samples[key].isMC: 
        w[key]=samples[key].lumiScaleFactor(lumi)

signal=['T_t_ToLeptons','Tbar_t_ToLeptons']

# Create output file
outf = TFile('TMVA'+sample+'.root','RECREATE')

# Initialize TMVA factory
factory=TMVA.Factory("stop_"+sample,outf,"Transformations=I;N;D")

# Which particle do we use for pt, eta etc
prt='el'
if sample=='mu': prt='mu'

# Let's define what variables we want to use for signal discrimination
factory.AddVariable("top_mass",'D')
factory.AddVariable("eta_lj",'D')
factory.AddVariable("C",'D')
factory.AddVariable("met",'D')
factory.AddVariable("mt_"+prt,'D')
factory.AddVariable("bdiscr_bj",'D')
factory.AddVariable("bdiscr_lj",'D')
factory.AddVariable(prt+"_pt",'D')
factory.AddVariable(prt+"_charge",'I')
factory.AddVariable("pt_bj",'D')
factory.AddSpectator("cos_theta",'D')

# Now let's add signal and background trees with proper weights
for k in t.keys():
    print "Adding trees to MVA:",k
    if t[k].GetEntries():
        if k in signal:
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

"""
# We use categorized BDT
cat2=factory.BookMethod(TMVA.Types.kCategory,
                    "cat2",
                    "")

cat2.AddMethod(TCut("cos_theta < 0"),
              "top_mass:eta_lj:C:met:mt_"+prt+":bdiscr_bj:bdiscr_lj:pt_bj:"+prt+"_pt:"+prt+"_charge",
              TMVA.Types.kBDT,
              "Category2_BDT_lowCTH",
              "!H:!V:NTrees=2000:BoostType=Grad:Shrinkage=0.10:!UseBaggedGrad:nCuts=2000:nEventsMin=100:NNodesMax=5:UseNvars=4:PruneStrength=5:PruneMethod=CostComplexity:MaxDepth=6")

cat2.AddMethod(TCut("cos_theta >= 0"),
              "top_mass:eta_lj:C:met:mt_"+prt+":bdiscr_bj:bdiscr_lj:pt_bj:"+prt+"_pt:"+prt+"_charge",
              TMVA.Types.kBDT,
              "Category2_BDT_highCTH",
              "!H:!V:NTrees=2000:BoostType=Grad:Shrinkage=0.10:!UseBaggedGrad:nCuts=2000:nEventsMin=100:NNodesMax=5:UseNvars=4:PruneStrength=5:PruneMethod=CostComplexity:MaxDepth=6")

cat4=factory.BookMethod(TMVA.Types.kCategory,
                    "cat4",
                    "")

cat4.AddMethod(TCut("abs(eta_lj)<2.5 & cos_theta < 0"),
              "top_mass:eta_lj:C:met:mt_"+prt+":bdiscr_bj:bdiscr_lj:pt_bj:"+prt+"_pt:"+prt+"_charge",
              TMVA.Types.kBDT,
              "Category4_BDT_lowEta_lowCTH",
              "!H:!V:NTrees=2000:BoostType=Grad:Shrinkage=0.10:!UseBaggedGrad:nCuts=2000:nEventsMin=100:NNodesMax=5:UseNvars=4:PruneStrength=5:PruneMethod=CostComplexity:MaxDepth=6")

cat4.AddMethod(TCut("abs(eta_lj)<2.5 & cos_theta >= 0"),
              "top_mass:eta_lj:C:met:mt_"+prt+":bdiscr_bj:bdiscr_lj:pt_bj:"+prt+"_pt:"+prt+"_charge",
              TMVA.Types.kBDT,
              "Category4_BDT_lowEta_highCTH",
              "!H:!V:NTrees=2000:BoostType=Grad:Shrinkage=0.10:!UseBaggedGrad:nCuts=2000:nEventsMin=100:NNodesMax=5:UseNvars=4:PruneStrength=5:PruneMethod=CostComplexity:MaxDepth=6")

cat4.AddMethod(TCut("abs(eta_lj)>=2.5 & cos_theta < 0"),
              "top_mass:eta_lj:C:met:mt_"+prt+":bdiscr_bj:bdiscr_lj:pt_bj:"+prt+"_pt:"+prt+"_charge",
              TMVA.Types.kBDT,
              "Category4_BDT_highEta_lowCTH",
              "!H:!V:NTrees=2000:BoostType=Grad:Shrinkage=0.10:!UseBaggedGrad:nCuts=2000:nEventsMin=100:NNodesMax=5:UseNvars=4:PruneStrength=5:PruneMethod=CostComplexity:MaxDepth=6")

cat4.AddMethod(TCut("abs(eta_lj)>=2.5 & cos_theta >= 0"),
              "top_mass:eta_lj:C:met:mt_"+prt+":bdiscr_bj:bdiscr_lj:pt_bj:"+prt+"_pt:"+prt+"_charge",
              TMVA.Types.kBDT,
              "Category4_BDT_highEta_highCTH",
              "!H:!V:NTrees=2000:BoostType=Grad:Shrinkage=0.10:!UseBaggedGrad:nCuts=2000:nEventsMin=100:NNodesMax=5:UseNvars=4:PruneStrength=5:PruneMethod=CostComplexity:MaxDepth=6")
"""

factory.TrainAllMethods()
factory.TestAllMethods()
factory.EvaluateAllMethods()

outf.Close()
