import FWCore.ParameterSet.Config as cms

process = cms.Process("OWNPARTICLES")

#process.load("FWCore.MessageService.MessageLogger_cfi")
process.load("FWCore.MessageLogger.MessageLogger_cfi")
process.MessageLogger = cms.Service("MessageLogger",
       destinations   = cms.untracked.vstring(
                                              'cout',
                    ),
       debugModules   = cms.untracked.vstring('recoNuProducer'),
       cout       = cms.untracked.PSet(
                       threshold = cms.untracked.string('DEBUG') 
        ),
)

process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(-1) )

process.source = cms.Source("PoolSource",
    # replace 'myfile.root' with the source file you want to use
    fileNames = cms.untracked.vstring(
        'file:myfile.root'
    )
)

process.recoNuProducer = cms.EDProducer('ReconstructedNeutrinoProducer',
	leptonSrc = cms.InputTag("goodSignalMuons"),
	bjetSrc = cms.InputTag("bTagsTCHPtight"),
	metSrc = cms.InputTag("patMETs"),

)

process.out = cms.OutputModule("PoolOutputModule",
    fileName = cms.untracked.string('myOutputFile.root')
)

  
process.p = cms.Path(process.recoNuProducer)

process.e = cms.EndPath(process.out)


from SingleTopPolarization.Analysis.cmdlineParsing import enableCommandLineArguments
enableCommandLineArguments(process)