import FWCore.ParameterSet.Config as cms
from SingleTopPolarization.Analysis.selection_step2_cfg import SingleTopStep2, Config

Config.doMETSystShift = False
Config.bTagDiscriminant = Config.Jets.BTagDiscriminant.CSV
Config.bTagWorkingPoint = Config.Jets.BTagWorkingPoint.CSVT
process = SingleTopStep2()
