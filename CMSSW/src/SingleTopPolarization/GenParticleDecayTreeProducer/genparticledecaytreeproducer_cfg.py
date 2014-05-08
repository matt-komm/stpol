import FWCore.ParameterSet.Config as cms

process = cms.Process("OWNPARTICLES")

process.load("FWCore.MessageService.MessageLogger_cfi")

process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(-1) )

process.source = cms.Source("PoolSource",
    # replace 'myfile.root' with the source file you want to use
    fileNames = cms.untracked.vstring(
        'file:output_85_1_Xhc.root'
    )
)

process.decayTreeProd = cms.EDProducer(
    'GenParticleDecayTreeProducer',
    src=cms.untracked.InputTag("muonsWithID")
)

process.out = cms.OutputModule("PoolOutputModule",
    fileName = cms.untracked.string('myOutputFile.root')
)


process.p = cms.Path(process.decayTreeProd)

process.e = cms.EndPath(process.out)
