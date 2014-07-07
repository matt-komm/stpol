import FWCore.ParameterSet.Config as cms

process = cms.Process("OWNPARTICLES")

process.load("FWCore.MessageService.MessageLogger_cfi")

process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(-1) )

process.source = cms.Source("PoolSource",
    # replace 'myfile.root' with the source file you want to use
    fileNames = cms.untracked.vstring(
        '/store/mc/Summer12_DR53X/TToBMuNu_t-channel_TuneZ2star_8TeV-comphep/AODSIM/PU_S10_START53_V7A-v1/0000/062EC597-0AF9-E111-AFED-00237DDCBEA4.root'
    )
)

process.genParticleSelectorCompHep = cms.EDProducer('GenParticleSelectorCompHep',
    src=cms.InputTag("genParticles"),
)

process.out = cms.OutputModule("PoolOutputModule",
    fileName = cms.untracked.string('myOutputFile.root')
)

  
process.p = cms.Path(process.genParticleSelectorCompHep)

process.e = cms.EndPath(process.out)
