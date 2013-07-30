import FWCore.ParameterSet.Config as cms
from SingleTopPolarization.Analysis.runconfs.step3_eventloop_base_nocuts import *
process.fwliteInput.maxEvents = -1
process.fwliteInput.makeTree = False
print_process(process)
