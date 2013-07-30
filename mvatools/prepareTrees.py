#!/bin/env python

# Enable logging module
import logging
logging.basicConfig(level=logging.WARNING)

# import modules needed for argument parsing
import sys
import os
import argparse
import shutil

# Parse command line arguments
parser = argparse.ArgumentParser(
    description = 'Prepare test and training trees by skimming them'
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
        "-o",
        "--outdir", type=str, required=False, default=(os.environ["STPOL_DIR"] + "/mva_input"),
        help="the output directory"
)
parser.add_argument(
        '-d',
        '--debug', required=False, default=False, action='store_true', dest='debug',
        help='Enable debug printout'
)
args = parser.parse_args()

logger = logging.getLogger('prepareTrees')

if args.debug:
        logger.setLevel(logging.DEBUG)

proc = args.channel

# Get list of samples and variables to be used for training
from sampleList import *

# Import toolkit items for sample reading, scaling, cutting etc
from plots.common.sample import Sample

# Import the important parts from ROOT
from ROOT import TFile,TTree,TObject

flist = []
for i in ['sig','bg']:
        for j in ['train','eval']:
                    flist += mvaFileList[i][j]

logger.debug('Used file list: %s',str(flist))

cut = str(cuts[proc])
logger.debug('Cut used in skim: %s' % cut)

# Create output directory
try: 
    os.makedirs(args.outdir+'/%s' % proc)
except Exception as e:
    if not os.path.exists(args.outdir+'/%s' % proc):
        raise e

logger.debug('Using output directory as: %s/%s' % (args.outdir,proc))

for f in flist:
    logger.debug('Start skimming: %s' % f)
    shutil.copy2(args.indir+'/%s/mc/iso/nominal/Jul15/%s.root' % (proc,f),args.outdir+'/%s/%s.root' % (proc,f))
    tf=TFile(args.outdir+'/%s/%s.root' % (proc,f),'UPDATE')
    tin=tf.Get('trees/Events')
    tin.AddFriend('trees/WJets_weights')
    tout=tin.CopyTree(cut)
    tout.SetName('Events_MVA')
    tf.cd('trees')
    tout.Write("", TObject.kOverwrite)
    logger.debug('Output tree contains %d events' % tout.GetEntries())
    tf.Close()
