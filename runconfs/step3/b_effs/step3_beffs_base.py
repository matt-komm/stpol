import FWCore.ParameterSet.Config as cms
from runconfs.step3_eventloop_base_nocuts import *
process.fwliteInput.maxEvents = -1
process.fwliteInput.makeTree = False
print_process(process)