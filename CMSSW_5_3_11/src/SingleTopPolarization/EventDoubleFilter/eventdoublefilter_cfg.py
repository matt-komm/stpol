import FWCore.ParameterSet.Config as cms

process = cms.Process("Demo")

process.load("FWCore.MessageService.MessageLogger_cfi")

process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(-1) )

process.source = cms.Source("PoolSource",
    # replace 'myfile.root' with the source file you want to use
    fileNames = cms.untracked.vstring(
        'file:/home/joosep/singletop/stpol/patTuple.root'
    )
)

process.demo = cms.EDFilter('EventDoubleFilter'
, src = cms.InputTag("")
, max = cms.double(9999.0)
, min = cms.double(45)
)

process.p = cms.Path(process.demo)

from SingleTopPolarization.Analysis.cmdlineParsing import enableCommandLineArguments
enableCommandLineArguments(process)