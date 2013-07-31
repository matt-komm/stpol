#!/bin/env python

# Enable logging module
import logging
logging.basicConfig(level=logging.WARNING)

# import modules needed for argument parsing
import sys
import os
import argparse
from copy import copy

# Parse command line arguments
parser = argparse.ArgumentParser(
    description='Train MVA with variable evaluation'
)
parser.add_argument(
    "-c",
    "--channel", type=str, required=True, choices=["mu", "ele"], dest="channel", default=None,
    help="the lepton channel to use"
)
parser.add_argument(
    "-i",
    "--indir", type=str, required=False, default=(os.environ["STPOL_DIR"] + "/mva_input"),
    help="the input directory, which is expected to contain the subdirectories: mu/ele"
)
parser.add_argument(
    '-d',
    '--debug', required=False, default=False, action='store_true', dest='debug',
    help='Enable debug printout'
)
parser.add_argument(
    '-l',
    '--lumitag', required=False, default='83a02e9_Jul22', type=str, dest='lumitag',
    help='Luminosity tag for total integrated lumi'
)
parser.add_argument(
    '-v',
    '--var', required=False, default=[], action='append', type=str, dest="rej_var",
    help='Variable to remove from MVA training'
)
parser.add_argument(
    '-r',
    '--rank', required=False, default=[], action='append', type=str, dest="rank_var",
    help='Variable to use in training for rank cumulation'
)
args = parser.parse_args()

logger = logging.getLogger('trainMVAs.py')

if args.debug:
    logger.setLevel(logging.DEBUG)

rVar=args.rej_var
cVar=args.rank_var

if len(rVar) and len(cVar):
    logger.error('Cannot set exclusion and cumulation variables together')
    sys.exit(1)

# Get list of samples and variables to be used for training
from sampleList import *

# Import toolkit items for sample reading, scaling, cutting etc
from plots.common.sample import Sample
from plots.common.cuts import Weights
from plots.common.cross_sections import lumis

# Import the important parts from ROOT
from ROOT import TFile,TTree,TMVA,TCut

proc = args.channel

# Which luminosity we use
lumi = lumis[args.lumitag]['iso'][proc]

flist = []
for i in ['sig','bg']:
    for j in ['train','eval']:
        flist += mvaFileList[i][j]

logger.debug('Used file list: %s',str(flist))

# Read in the samples
samples = {}
for f in flist:
    samples[f] = Sample.fromFile(args.indir+'/%s/%s.root' % (proc,f), tree_name='Events_MVA')

# Set the weight expression
weightString = str(Weights.total(proc) *
    Weights.wjets_madgraph_shape_weight() *
    Weights.wjets_madgraph_flat_weight())

# Which file do we use to write our TMVA trainings
ext=''
if len(rVar):
    ext='_sans'
    for v in rVar:
        ext+='_'+v

if len(cVar):
    ext='_with'
    for v in cVar:
        ext+='_'+v

out = TFile('TMVA%s%s.root' % (proc,ext),'RECREATE')

def trainMVA(**kwds):
    """
    Method trains the MVA.

    Arguments:
        varlist - list of variables to be used for training
        proc - process that is used. Should be either 'ele' or 'mu'
        weight - weight string to use
        rej_var - possibly a variable to remove
        rank_var - variables to be used instead of varlist
    """
    proc = kwds.get('proc',0)
    if not proc:
        logger.error('No process defined, aborting MVA training')
        return -1

    vlist=kwds.get('varlist',varList[proc])
    rVar=kwds.get('rej_var',[])
    cVar=kwds.get('rank_var',[])
    ext=''
    mname='BDT'
    if len(rVar):
        ext='_sans'
        for v in rVar:
            vlist.remove(v)
            ext+='_'+v
        mname+=ext
    if len(cVar):
        ext='_with'
        for v in cVar:
            ext+='_'+v
        vlist=cVar
        mname+=ext

    factory = TMVA.Factory('stop_'+proc,out,'Transformations=I;N;D')
    wstring = kwds.get('weight','1.0')

    # define variables that we'll use for training
    for v in vlist:
        factory.AddVariable(v,'D')

    # Add the training and testing trees to the factory
    for s in mvaFileList['bg']['train']:
        factory.AddBackgroundTree(samples[s].getTree(),samples[s].lumiScaleFactor(lumi),TMVA.Types.kTraining)

    for s in mvaFileList['bg']['eval']:
        factory.AddBackgroundTree(samples[s].getTree(),samples[s].lumiScaleFactor(lumi),TMVA.Types.kTesting)

    for s in mvaFileList['sig']['train']:
        factory.AddSignalTree(samples[s].getTree(),samples[s].lumiScaleFactor(lumi),TMVA.Types.kTraining)

    for s in mvaFileList['sig']['eval']:
        factory.AddSignalTree(samples[s].getTree(),samples[s].lumiScaleFactor(lumi),TMVA.Types.kTesting)

    # Set the per event weights string
    factory.SetWeightExpression(wstring)
    factory.PrepareTrainingAndTestTree(
        TCut(), TCut(),
        "SplitMode=Block:NormMode=None::V"
    )

    # Book the MVA method
    factory.BookMethod(
        TMVA.Types.kBDT,
        mname,
        "!H:!V:"\
        "NTrees=2000:"\
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
    )

    # Train, test and evaluate them all
    factory.TrainAllMethods()
    factory.TestAllMethods()
    factory.EvaluateAllMethods()

# First, train the main BDT with all variables
trainMVA(proc=proc,weight=weightString,varlist=varList[proc],rej_var=rVar,rank_var=cVar)
out.Close()
