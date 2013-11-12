#!/usr/bin/env python

# Import the important parts from ROOT
try:
    import ROOT
except:
    pass

from ROOT import TMVA,TCut,TFile

import json
import sys

def sample_name(fn):
    return fn.split("/")[-2]

#inputs
inpdir = sys.argv[1]
jobname = sys.argv[2]
varlist = map(lambda x: x.strip(), open("%s/vars.txt" % inpdir).readlines())
specs = ["lepton_type"]
xsweights = json.load(open("%s/input_summary.txt" % inpdir))
bgfiles = open("%s/bg.txt" % inpdir).readlines()
sigfiles = open("%s/sig.txt" % inpdir).readlines()
trainfiles = open("%s/train.txt" % inpdir).readlines()

def file_type(fn):
    if fn in trainfiles:
        return TMVA.Types.kTraining
    else:
        return TMVA.Types.kTesting

#TMVA output file
out = TFile('%s/TMVA.root' % inpdir, 'RECREATE')

factory = TMVA.Factory(
    jobname, out,
    'Transformations=I;N:DrawProgressBar=False'
)

#define variables that we'll use for training
#currently all must be float (TMVA limitation)
for v in varlist:
    factory.AddVariable(v, "F")
for s in specs:
    factory.AddSpectator(s, "F")

flist = []
for fn in bgfiles+sigfiles:
    tf = TFile(fn.strip())
    tree = tf.Get("dataframe")

    flist.append(tf)
    xsweight = xsweights[sample_name(fn)]

    print sample_name(fn), xsweight

    if fn in bgfiles:
        factory.AddBackgroundTree(tree, xsweight, file_type(fn))
    elif fn in sigfiles:
        factory.AddSignalTree(tree, xsweight, file_type(fn))

# Set the per event weights string
factory.SetWeightExpression("1.0")
#cut="met>40 && ljet_pt>90"
cut="1.0"
factory.PrepareTrainingAndTestTree(
    TCut(cut), TCut(cut),
    "SplitMode=Block:NormMode=None:VerboseLevel=Debug"
)

# Book the MVA method
mva_args = ""\
    "H:VerbosityLevel=Debug:"\
    "NTrees=1000:"\
    "BoostType=Grad:"\
    "Shrinkage=0.1:"\
    "!UseBaggedGrad:"\
    "nCuts=2000:"\
    "nEventsMin=100:"\
    "NNodesMax=5:"\
    "UseNvars=4:"\
    "PruneStrength=5:"\
    "PruneMethod=CostComplexity:"\
    "MaxDepth=6"

#categorize by lepton flavour
lepton_cat = factory.BookMethod(
    TMVA.Types.kCategory,
    "lepton_flavour",
    ""
)

#muon events
lepton_cat.AddMethod(
    TCut("abs(lepton_type)==13.0"),
    ":".join(varlist),
    TMVA.Types.kBDT,
    "muon",
    mva_args
)

#electron events
lepton_cat.AddMethod(
    TCut("abs(lepton_type)==11.0"),
    ":".join(varlist),
    TMVA.Types.kBDT,
    "electron",
    mva_args
)

# Train, test and evaluate them all
factory.TrainAllMethods()
factory.TestAllMethods()
factory.EvaluateAllMethods()

out.Close()
