#!/bin/env python

# Enable logging module
import logging
logging.basicConfig(level=logging.WARNING)

# import modules needed for argument parsing
import sys
import os
import argparse

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
    "--indir", type=str, required=False, default=(os.environ["STPOL_DIR"] + "/step3_latest"),
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
args = parser.parse_args()

logger = logging.getLogger('evaluateVarsAndTrain')

if args.debug:
    logger.setLevel(logging.DEBUG)

# Get list of samples and variables to be used for training
from sampleList import *

# Import toolkit items for sample reading, scaling, cutting etc
from plots.common.sample import Sample
from plots.common.cuts import Cut,Cuts,Weights
from plots.common.cross_sections import lumis

# Import the important parts from ROOT
from ROOT import TFile,TTree,TMVA

# Which luminosity we use
lumi = lumis[args.lumitag]['iso'][args.channel]

flist = []
for i in ['sig','bg']:
    for j in ['train','eval']:
        flist += mvaFileList[i][j]

logger.debug('Used file list: %s',str(flist))

# Read in the samples
samples = {}
for f in flist:
    samples[f] = Sample.fromFile(args.indir+'/'+f+'.root')

# Set the weight expression
weightString = str(Weights.total(proc) *
    Weights.wjets_madgraph_shape_weight() *
    Weights.wjets_madgraph_flat_weight())


