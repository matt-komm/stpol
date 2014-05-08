#!/bin/env python
from ROOT import *

import logging
logging.basicConfig(level=logging.WARNING)

from plots.common.utils import *
import sys
from array import array
from copy import copy

import argparse
parser = argparse.ArgumentParser(
   description='Add the MVA friend tree with BDT values'
)
parser.add_argument(
   '-d',
   '--debug', required=False, default=False, action='store_true', dest='debug',
   help='Enable debug printout'
)
parser.add_argument(
   "-f",
   "--file", type=str, required=True, dest="fname", default=None,
   help="the root file to use"
)
parser.add_argument(
   "-c",
   "--channel", type=str, required=False, choices=["mu", "ele"], dest="channel", default=None,
   help="the lepton channel to use"
)
args = parser.parse_args()
if not args.channel:
    if "/mu/" in args.fname:
        args.channel = "mu"
    elif "/ele/" in args.fname:
        args.channel = "ele"
    else:
        raise ValueError("channel not specified: %", args.fname)

logger = logging.getLogger('addMVAasFriend.py')

if args.debug:
    logger.setLevel(logging.DEBUG)

proc = args.channel
fname = args.fname

from sampleList import varRank

# Create reader and relate variables
reader = {}
varlist = varRank[proc]
vars={}
mvalist=[]
vlist=[]
vlistMva={}
base='BDT_with'
for v in varlist:
    vars[v] = array('f',[0])
    base+='_%s' % v
    mvalist+=[base]
    vlist+=[v]
    vlistMva[base]=copy(vlist)

# Book the MVA's
mva={}
for m in mvalist:
    reader[m] = TMVA.Reader()
    mva[m] = array('f',[0])
    for v in vlistMva[m]:
        reader[m].AddVariable(v,vars[v])
    reader[m].BookMVA(m,"weights/stop_"+proc+"_"+m+".weights.xml")

# Run over files and add all the MVA's to the trees
logger.info("Starting: %s" % fname)
tf=TFile(fname,'UPDATE')
t=tf.Get("trees/Events")
tf.cd('trees')
mt=TTree("MVA","MVA")
t.SetBranchStatus("*",0)
branch={}
for v in varlist:
    t.SetBranchStatus(v,1)
    t.SetBranchAddress(v,vars[v])
for m in mvalist:
    branch[m]=mt.Branch('mva_'+m,mva[m],'mva_'+m+'/F')
for i in range(t.GetEntries()):
    t.GetEntry(i)
    for m in mvalist:
        calc = True
        for v in varlist:
            if not vars[v][0] == vars[v][0]:
               calc = False
        if calc:
            mva[m][0] = reader[m].EvaluateMVA(m)
        else:
            mva[m][0] = float('nan')
        logger.debug('i: %d, mva: %1.3f, vars: %s' % (i,mva[m][0],str(vars)))
    mt.Fill()
mt.Write('',TObject.kOverwrite)
tf.Close()

