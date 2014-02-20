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

process.options = cms.untracked.PSet(wantSummary=cms.untracked.bool(True))

# Producers
process.vertexCollectionSizeProducer = cms.EDProducer('CollectionSizeProducer<reco::Vertex>',
	src = cms.InputTag("offlinePrimaryVertices")
)

# Path
process.p = cms.Path(
    process.vertexCollectionSizeProducer
#                    *process.photonCollectionSizeProducer
)

process.out = cms.OutputModule("PoolOutputModule",
    fileName = cms.untracked.string('myOutputFile.root')
)

process.e = cms.EndPath(process.out)

#Command-line arguments
from SingleTopPolarization.Analysis.cmdlineParsing import enableCommandLineArguments
enableCommandLineArguments(process)
