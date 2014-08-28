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
    return fn.split("/")[-3]

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

cuts = {
    "mu": "(hlt_mu == 1) && ((n_signal_mu==1) && (n_signal_ele==0) && (n_veto_mu==0) && (n_veto_ele==0))",
    "ele": "(hlt_ele == 1) && ((n_signal_mu==0) && (n_signal_ele==1) && (n_veto_mu==0) && (n_veto_ele==0))"
}

cut="(hlt==1) && (njets==2) && (ntags==1) && ((%s) || (%s))" %(cuts["mu"], cuts["ele"])

tempFile = TFile("%s/trees.root" % inpdir, "RECREATE")
for fn in sigfiles + bgfiles:
    tf = TFile(fn.strip())
    tree1 = tf.Get("dataframe")
    tempFile.cd()

    def getentries(nj, nt):
        return tree1.GetEntries("((%s) || (%s)) && (njets==%d) && (ntags==%d)" % (cuts["mu"], cuts["ele"], nj, nt))

    for (nj, nt) in [(2,1), (2, 0), (3, 2)]:
        c = "((%s) || (%s)) && (njets==%d) && (ntags==%d)" % (cuts["mu"], cuts["ele"], nj, nt)
        tree = tree1.CopyTree(c, "", getentries(2,1))
        tree.SetName("%s/%dJ/%dT" % (fn, nj, nt))
        tree.SetDirectory(tempFile)
        if tree.IsZombie():
            raise Exception("tree in %s was not proper: %s, %d" % (fn, tree))
        if tree.GetEntries()==0:
            print "tree was empty, skipping"
            continue
        tree.Write()

        flist.append(tf)
        xsweight = xsweights[sample_name(fn)]

        print sample_name(fn), xsweight, (nj, nt), tree.GetEntries()

        if fn in bgfiles:
            print "background type =", file_type(fn)
            factory.AddBackgroundTree(tree, xsweight, file_type(fn))
        elif fn in sigfiles:
            print "signal type =", file_type(fn)
            factory.AddSignalTree(tree, xsweight, file_type(fn))
        else:
            raise Exception("%s not in signal or background" % fn)
    tf.Close()

# Set the per event weights string
factory.SetWeightExpression("1.0")
#cut="met>40 && ljet_pt>90"


cut = ""
factory.PrepareTrainingAndTestTree(
    TCut(cut), TCut(cut),
    "NormMode=None:VerboseLevel=Debug"
)

# Book the MVA method
#mva_args = ""\
#    "H:VerbosityLevel=Debug:"\
#    "NTrees=50:"\
#    "BoostType=Grad:"\
#    "Shrinkage=0.1:"\
#    "!UseBaggedGrad:"\
#    "nCuts=200:"\
#    "SeparationType=CrossEntropy:"\
#    "NNodesMax=5:"\
#    "UseNvars=4:"\
#    "PruneStrength=7:"\
#    "PruneMethod=CostComplexity:"\
#    "MaxDepth=2"
mva_args = sys.argv[3]

#categorize by lepton flavour
lepton_cat = factory.BookMethod(
    TMVA.Types.kCategory,
    "lepton_flavour",
    ""
)

#muon events
lepton_cat.AddMethod(
    TCut("abs(lepton_type)==13"),
    ":".join(varlist),
    TMVA.Types.kBDT,
    "muon",
    mva_args
)

#electron events
lepton_cat.AddMethod(
    TCut("abs(lepton_type)==11"),
    ":".join(varlist),
    TMVA.Types.kBDT,
    "electron",
    mva_args
)


## Without categorization
#factory.BookMethod(
#    TMVA.Types.kBDT,
#    "BDT",
#    "!H:!V:NTrees=2000:BoostType=Grad:Shrinkage=0.1:!UseBaggedGrad:nCuts=2000:nEventsMin=100:NNodesMax=5:UseNvars=4:PruneStrength=5:PruneMethod=CostComplexity:MaxDepth=6"\
#)

# Train, test and evaluate them all
factory.TrainAllMethods()
factory.TestAllMethods()
factory.EvaluateAllMethods()

out.Close()
