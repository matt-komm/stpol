import FWCore.ParameterSet.Config as cms

process = cms.Process("OWNPARTICLES")

process.load("FWCore.MessageLogger.MessageLogger_cfi")
process.MessageLogger = cms.Service("MessageLogger",
       destinations = cms.untracked.vstring('cout'),
       debugModules = cms.untracked.vstring('bTagWeightProducer'),
       cout = cms.untracked.PSet(threshold = cms.untracked.string('DEBUG')),
)
process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(-1) )

process.source = cms.Source("PoolSource",
    # replace 'myfile.root' with the source file you want to use
    fileNames = cms.untracked.vstring(
        'file:output.root'
    )
)

process.bTagWeightProducer = cms.EDProducer('BTagSystematicsWeightProducer',
	src=cms.InputTag("goodJets"),
	nJets=cms.uint32(2),
	nTags=cms.uint32(1),
	effB=cms.double(0.9),
	effC=cms.double(0.2),
	effL=cms.double(0.1)
)

process.out = cms.OutputModule("PoolOutputModule",
    fileName = cms.untracked.string('bTagWeight.root')
)

  
process.p = cms.Path(process.bTagWeightProducer)

process.e = cms.EndPath(process.out)
