import FWCore.ParameterSet.Config as cms

process = cms.Process("OWNPARTICLES")

process.load("FWCore.MessageLogger.MessageLogger_cfi")
process.MessageLogger = cms.Service("MessageLogger",
       destinations=cms.untracked.vstring('cout'),
       debugModules=cms.untracked.vstring('collCombiner'),
       cout=cms.untracked.PSet(threshold=cms.untracked.string('DEBUG')),
)

process.maxEvents = cms.untracked.PSet(
    input=cms.untracked.int32(-1)
)

process.source = cms.Source("PoolSource",
    # replace 'myfile.root' with the source file you want to use
    fileNames=cms.untracked.vstring(
        'file:myfile.root'
    )
)

process.combinedLeptons = cms.EDProducer(
    'CandRefCombiner',
    sources=cms.untracked.vstring(["goodSignalMuons", "goodSignalElectrons"]),
    minOut=cms.untracked.uint32(1),
    maxOut=cms.untracked.uint32(1),
)

process.lepAnalyzer = cms.EDAnalyzer(
  'CandOwnVectorSimpleAnalyzer',
  interestingCollection = cms.untracked.string("combinedLeptons")
)

process.lepAnalyzer2 = cms.EDAnalyzer(
  'SimpleEventAnalyzer',
  interestingCollection = cms.untracked.string("combinedLeptons")
)

process.out = cms.OutputModule("PoolOutputModule",
    fileName=cms.untracked.string('myOutputFile.root')
)

process.p = cms.Path(
  process.combinedLeptons *
  process.lepAnalyzer *
  process.lepAnalyzer2
)

process.e = cms.EndPath(process.out)

#Command-line arguments
from SingleTopPolarization.Analysis.cmdlineParsing import enableCommandLineArguments
enableCommandLineArguments(process)
