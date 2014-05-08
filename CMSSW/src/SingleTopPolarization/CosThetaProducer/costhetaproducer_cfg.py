import FWCore.ParameterSet.Config as cms

process = cms.Process("OWNPARTICLES")

process.load("FWCore.MessageService.MessageLogger_cfi")

process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(-1) )

process.source = cms.Source("PoolSource",
    # replace 'myfile.root' with the source file you want to use
    fileNames = cms.untracked.vstring(
        'file:myfile.root'
    )
)

process.combinedLeptons = cms.EDProducer(
    'CandRefCombiner',
    sources=cms.untracked.vstring(["goodSignalMuons", "goodSignalElectrons"]),
    minOut=cms.untracked.uint32(1),
    maxOut=cms.untracked.uint32(1),
)

process.cosThetaProducer = cms.EDProducer('CosThetaProducer',
	topSrc=cms.InputTag("recoTop"),
	jetSrc=cms.InputTag("bTagsTCHPtight"),
	leptonSrc=cms.InputTag("combinedLeptons")
)

process.out = cms.OutputModule("PoolOutputModule",
    fileName = cms.untracked.string('myOutputFile.root')
)

  
process.p = cms.Path(
	process.combinedLeptons *
	process.cosThetaProducer
)

process.e = cms.EndPath(process.out)

#Command-line arguments
from SingleTopPolarization.Analysis.cmdlineParsing import enableCommandLineArguments
enableCommandLineArguments(process)
