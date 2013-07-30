#!/bin/env python
from ROOT import TFile,TH1F
from sampleList import varList

# Enable logging module
import logging
logging.basicConfig(level=logging.WARNING)

# Read command line arguments
import sys
from copy import copy
import argparse
parser = argparse.ArgumentParser(
    description='Checks the MVA efficiency against variable removal'
)
parser.add_argument(
    "-c",
    "--channel", type=str, required=True, choices=["mu", "ele"], dest="channel", default=None,
    help="the lepton channel to use"
)
parser.add_argument(
    '-v',
    '--var', required=False, default=[], action='append', type=str, dest="rej_var",
    help='Variable to remove from MVA training'
)
parser.add_argument(
    '-e',
    '--eff', type=float, required=False, dest='efficiency', default=0.3,
    help='Efficiency of signal to check at'
)
parser.add_argument(
    '-d',
    '--debug', required=False, default=False, action='store_true', dest='debug',
    help='Enable debug printout'
)
args = parser.parse_args()

logger = logging.getLogger('checkRanking')

if args.debug:
    logger.setLevel(logging.DEBUG)

proc = args.channel
eff  = args.efficiency
bin  = int(eff*100)+1
rVars = args.rej_var

logger.debug('Proc: %s, eff %1.3f, bin used: %d' % (proc,eff,bin))

rej={}
base=''
vlist=copy(varList[proc])

if len(rVars):
    base='_sans'
    for v in rVars:
        base+='_%s' % v
        vlist.remove(v)

# Let's read in the baseline BDT for comparison
f=TFile('TMVA%s%s.root' % (proc,base))

rej['base']=f.Get('Method_BDT/BDT%s/MVA_BDT%s_rejBvsS' % (base,base)).GetBinContent(bin)
f.Close()

diff = {}
for v in vlist:
    if base == '':
        base='_sans'
    logger.debug('file:TMVA%s%s_%s.root' % (proc,base,v))
    f=TFile('TMVA%s%s_%s.root' % (proc,base,v))
    logger.debug('object: Method_BDT/BDT%s_%s/MVA_BDT%s_%s_rejBvsS' % (base,v,base,v))
    rej[v]=f.Get('Method_BDT/BDT%s_%s/MVA_BDT%s_%s_rejBvsS' % (base,v,base,v)).GetBinContent(bin)
    diff[v]=rej[v]-rej['base']
    logger.debug('%s: %f' % (v,diff[v]))

rank=sorted(diff.items(), key=lambda x: x[1])
print rank[0][0]
