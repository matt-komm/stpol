import FWCore.ParameterSet.Config as cms
from SingleTopPolarization.Analysis.preselection_step2_cfg import SingleTopStep2Preselection, Config

Config.onGrid = False #use cmdline arguments, see selection_step2_cfg for details
process = SingleTopStep2Preselection()
