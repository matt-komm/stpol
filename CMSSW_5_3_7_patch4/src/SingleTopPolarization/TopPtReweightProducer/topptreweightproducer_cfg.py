import FWCore.ParameterSet.Config as cms

process = cms.Process("OWNPARTICLES")

process.load("FWCore.MessageService.MessageLogger_cfi")

process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(100) )

process.source = cms.Source("PoolSource",
    # replace 'myfile.root' with the source file you want to use
    fileNames = cms.untracked.vstring(
        'file:/hdfs/cms/store/user/joosep/TTJets_SemiLeptMGDecays_8TeV-madgraph/stpol_step1_05_20_a2437d6e0ca7eba657ba43c9c2371fff8f88e5ba/d6f3c092e0af235d8b18254ddb07959c/output_Skim_1_1_kpp.root'
    )
)

process.load("FWCore.MessageLogger.MessageLogger_cfi")
process.MessageLogger = cms.Service("MessageLogger",
       destinations=cms.untracked.vstring('cout'),
       debugModules=cms.untracked.vstring('*'),
       cout=cms.untracked.PSet(threshold=cms.untracked.string('DEBUG')),
)

process.myProducerLabel = cms.EDProducer(
    'TopPtReweightProducer',
    src=cms.InputTag("genParticles")
)

process.out = cms.OutputModule("PoolOutputModule",
    fileName = cms.untracked.string('myOutputFile.root')
)


process.p = cms.Path(process.myProducerLabel)

process.e = cms.EndPath(process.out)
