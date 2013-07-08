import FWCore.ParameterSet.Config as cms

process = cms.Process("OWNPARTICLES")

process.load("FWCore.MessageService.MessageLogger_cfi")

process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(-1) )

process.source = cms.Source("PoolSource",
    fileNames = cms.untracked.vstring(
        'file:/home/joosep/singletop/stpol2/testing/step1/ttbar/out_step1_numEvent100_Skim.root'
    )
)

process.load("FWCore.MessageLogger.MessageLogger_cfi")
process.MessageLogger = cms.Service("MessageLogger",
       destinations=cms.untracked.vstring('cout'),
       debugModules=cms.untracked.vstring('*'),
       cout=cms.untracked.PSet(threshold=cms.untracked.string('INFO')),
)

process.electronsWithCorrectedEcalIso = cms.EDProducer(
    'CorrectedEcalIsoElectronProducer',
    src=cms.InputTag("electronsWithID"),
    isMC=cms.bool(True)
)

process.eleAnalyzer = cms.EDAnalyzer(
    'SimpleElectronAnalyzer',
    interestingCollections=cms.untracked.VInputTag(
        ["electronsWithID", "electronsWithCorrectedEcalIso"]
    )
)

process.out = cms.OutputModule("PoolOutputModule",
    fileName = cms.untracked.string('myOutputFile.root')
)


process.p = cms.Path(
    process.electronsWithCorrectedEcalIso*
    process.eleAnalyzer
)

process.e = cms.EndPath(process.out)
