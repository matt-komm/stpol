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
        '-d',
        '--debug', required=False, default=False, action='store_true', dest='debug',
        help='Enable debug printout'
)
args = parser.parse_args()

logger = logging.getLogger('plorROC')
if args.debug:
        logger.setLevel(logging.DEBUG)

from sampleList import varRank
from ROOT import TFile,TH1F,THStack,TLegend,TCanvas,gStyle,kFALSE
from copy import copy

proc = args.channel

cur=[]
base='_with'
name='roc'
hist={}
leg=TLegend(0.1,0.1,0.4,0.6)
c=TCanvas('c','c')
col=0
gStyle.SetOptStat(kFALSE)
gStyle.SetOptTitle(kFALSE)
for v in varRank[proc]:
    cur+=[v]
    base+='_%s' % v
    name+='_%s' % v
    col+=1
    f=TFile('TMVA%s%s.root' % (proc, base))
    h=f.Get('Method_BDT/BDT%s/MVA_BDT%s_rejBvsS' % (base,base))
    hist[v]=copy(h)
    hist[v].SetName(name)
    hist[v].SetLineColor(col)
    sm='same'
    if v==varRank[proc][0]:
        sm=''
    hist[v].Draw('l'+sm)
    leg.AddEntry(hist[v],v,'l')

leg.Draw('goff BATCH')
c.SaveAs('ROCs.png')
