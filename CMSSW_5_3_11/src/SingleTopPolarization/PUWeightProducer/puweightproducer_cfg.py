import FWCore.ParameterSet.Config as cms
import SingleTopPolarization.Analysis.pileUpDistributions as pileUpDistributions

process = cms.Process("OWNPARTICLES")

process.load("FWCore.MessageLogger.MessageLogger_cfi")

process = cms.Process("OWNPARTICLES")

process.load("FWCore.MessageLogger.MessageLogger_cfi")
process.MessageLogger = cms.Service("MessageLogger",
       destinations=cms.untracked.vstring('cout'),
       debugModules=cms.untracked.vstring('puWeightProducer'),
       cout=cms.untracked.PSet(threshold=cms.untracked.string('DEBUG')),
)
process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(100) )

process.source = cms.Source("PoolSource",
    fileNames = cms.untracked.vstring(
        #'file:/hdfs/cms/store/user/jpata/TTJets_MassiveBinDECAY_TuneZ2star_8TeV-madgraph-tauola/stpol_Feb8_FastSimValidation/243fe90abe1b1cf7bc2119dc7c0b2e28/output_Skim_100_1_pVx.root',
        'file:/hdfs/cms/store/user/jpata/TTJets_MassiveBinDECAY_TuneZ2star_8TeV-madgraph-tauola/stpol_Feb8_FastSimValidation_v2_FSIM/243fe90abe1b1cf7bc2119dc7c0b2e28/output_Skim_noSlim_99_2_aN4.root'
    )
)

process.puWeightProducer = cms.EDProducer('PUWeightProducer'
    , maxVertices = cms.uint32(50)
    , srcDistribution = cms.vdouble(pileUpDistributions.S7)
    , destDistribution = cms.vdouble(pileUpDistributions.data)
)

process.out = cms.OutputModule("PoolOutputModule",
    fileName = cms.untracked.string('myOutputFile.root')
)


process.p = cms.Path(process.puWeightProducer)

process.e = cms.EndPath(process.out)
