import FWCore.ParameterSet.Config as cms
from SingleTopPolarization.Analysis.selection_step2_cfg import SingleTopStep2, Config

Config.doMETSystShift = True
Config.bTagDiscriminant = Config.Jets.BTagDiscriminant.TCHP
Config.bTagWorkingPoint = Config.Jets.BTagWorkingPoint.TCHPT
process = SingleTopStep2()
