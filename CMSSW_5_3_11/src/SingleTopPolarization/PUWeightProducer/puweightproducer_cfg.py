import FWCore.ParameterSet.Config as cms
import SingleTopPolarization.Analysis.pileUpDistributions as pileUpDistributions
from SingleTopPolarization.Analysis.test_files import testfiles

def setup_test_process(name="TEST", debug_modules="*"):
    process = cms.Process(name)
    process.load("FWCore.MessageLogger.MessageLogger_cfi")
    process = cms.Process(name)

    process.load("FWCore.MessageLogger.MessageLogger_cfi")
    process.MessageLogger = cms.Service("MessageLogger",
           destinations=cms.untracked.vstring('cout'),
           debugModules=cms.untracked.vstring(debug_modules),
           cout=cms.untracked.PSet(threshold=cms.untracked.string('DEBUG')),
    )
    process.maxEvents = cms.untracked.PSet(input=cms.untracked.int32(-1))
    process.options = cms.untracked.PSet(wantSummary=cms.untracked.bool(True))

    process.source = cms.Source("PoolSource",
        fileNames = cms.untracked.vstring(testfiles['step1']['signal'])
    )
    return process

process = setup_test_process()
process.puWeightProducer = cms.EDProducer('PUWeightProducer'
    , maxVertices = cms.uint32(50)
    , srcDistribution = cms.vdouble(pileUpDistributions.S7)
    , weightFileNominal=cms.FileInPath("data/pu_weights/data_PU_nominal.root")
    , weightFileUp=cms.FileInPath("data/pu_weights/data_PU_up.root")
    , weightFileDown=cms.FileInPath("data/pu_weights/data_PU_down.root")
)

process.out = cms.OutputModule("PoolOutputModule",
    fileName = cms.untracked.string('out.root')
)


process.p = cms.Path(process.puWeightProducer)

process.e = cms.EndPath(process.out)
