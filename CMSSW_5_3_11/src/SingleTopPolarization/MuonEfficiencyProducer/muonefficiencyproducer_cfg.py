import FWCore.ParameterSet.Config as cms

process = cms.Process("OWNPARTICLES")

process.load("FWCore.MessageLogger.MessageLogger_cfi")
process.MessageLogger = cms.Service("MessageLogger",
       destinations = cms.untracked.vstring('cout'),
       debugModules = cms.untracked.vstring('muonEffProducer'),
       cout = cms.untracked.PSet(threshold = cms.untracked.string('DEBUG')),
)

process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(-1) )

process.source = cms.Source("PoolSource",
    # replace 'myfile.root' with the source file you want to use
    fileNames = cms.untracked.vstring(
        'file:myfile.root'
    )
)

process.muonEffProducer = cms.EDProducer('MuonEfficiencyProducer'
)

process.out = cms.OutputModule("PoolOutputModule",
    fileName = cms.untracked.string('myOutputFile.root')
)

  
process.p = cms.Path(process.muonEffProducer)

process.e = cms.EndPath(process.out)
