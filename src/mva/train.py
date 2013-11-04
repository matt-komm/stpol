#!/usr/bin/env python

# Import the important parts from ROOT
from ROOT import TMVA,TCut,TFile

import json
import sys

def sample_name(fn):
    return fn.split("/")[-2]

#input directory
inpdir = sys.argv[1]
jobname = sys.argv[2]
varlist = map(lambda x: x.strip(), open("%s/vars.txt" % inpdir).readlines())
print varlist

xsweights = json.load(open("%s/input_summary.txt" % inpdir))
bgfiles = open("%s/bg.txt" % inpdir).readlines()
sigfiles = open("%s/sig.txt" % inpdir).readlines()

# Which file do we use to write our TMVA trainings
out = TFile('%s/TMVA.root' % inpdir, 'RECREATE')

factory = TMVA.Factory(jobname, out,
        'Transformations=I;N;D:V:DrawProgressBar=False'
)

# define variables that we'll use for training
for v in varlist:
    factory.AddVariable(v,'D')
factory.AddSpectator("lepton_id", "I")

flist = []
for fn in bgfiles+sigfiles:
    tf = TFile(fn.strip())
    tree = tf.Get("dataframe")

    flist.append(tf)
    xsweight = xsweights[sample_name(fn)]

    print sample_name(fn), xsweight

    if fn in bgfiles:
        factory.AddBackgroundTree(tree, xsweight)
    elif fn in sigfiles:
        factory.AddSignalTree(tree, xsweight)

# Set the per event weights string
factory.SetWeightExpression("1.0")
cut="1"
factory.PrepareTrainingAndTestTree(
    TCut(cut), TCut(cut),
    "SplitMode=Random:NormMode=None"
)

# Book the MVA method
#mva_args = "!H:!V:"\
#    "NTrees=2000:"\
#    "BoostType=Grad:"\
#    "Shrinkage=0.1:"\
#    "!UseBaggedGrad:"\
#    "nCuts=2000:"\
#    "NNodesMax=5:"\
#    "UseNvars=4:"\
#    "PruneStrength=5:"\
#    "PruneMethod=CostComplexity:"\
#    "MaxDepth=6"
mva_args = "NTrees=100"

lepton_cat = factory.BookMethod(
    TMVA.Types.kCategory,
    "lepton_flavour",
    ""
)

lepton_cat.AddMethod(
    TCut("abs(lepton_type)==13"),
    ":".join(varlist),
    TMVA.Types.kBDT,
    "BDT_mu",
    mva_args
)

lepton_cat.AddMethod(
    TCut("abs(lepton_type)==11"),
    ":".join(varlist),
    TMVA.Types.kBDT,
    "BDT_ele",
    mva_args
)

lepton_cat.AddMethod(
    TCut("abs(lepton_type)!=11 && abs(lepton_type)!=13"),
    ":".join(varlist),
    TMVA.Types.kBDT,
    "BDT_others",
    mva_args
)

# Train, test and evaluate them all
factory.TrainAllMethods()
factory.TestAllMethods()
factory.EvaluateAllMethods()

out.Close()
