import FWCore.ParameterSet.Config as cms
import os

inFile = os.environ["TESTING_FILE"]

process = cms.Process("OWNPARTICLES")

process.load("FWCore.MessageLogger.MessageLogger_cfi")
process.MessageLogger=cms.Service("MessageLogger",
       destinations=cms.untracked.vstring('cout'),
       debugModules=cms.untracked.vstring('patJetsPuCleaned'),
       cout=cms.untracked.PSet(threshold=cms.untracked.string('DEBUG'))
)

process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(-1) )

process.source = cms.Source("PoolSource",
    # replace 'myfile.root' with the source file you want to use
    fileNames = cms.untracked.vstring(
        inFile
    )
)

process.patJetsWithOwnRef = cms.EDProducer('PatObjectOwnRefProducer<pat::Jet>',
    src=cms.InputTag("selectedPatJets")
)
process.patJetsPuCleaned = cms.EDProducer('CleanNoPUJetProducer',
#    jetSrc = cms.InputTag("patJetsWithOwnRef"),
    jetSrc = cms.InputTag("selectedPatJets"),
    PUidMVA = cms.InputTag("puJetMva", "fullDiscriminant", "PAT"),
    PUidFlag = cms.InputTag("puJetMva", "fullId", "PAT"),
    PUidVars = cms.InputTag("puJetId", "", "PAT"),
    isOriginal = cms.bool(True)

)
process.simpleAnalyzer = cms.EDAnalyzer(
	'SimpleEventAnalyzer',
    interestingCollections = cms.untracked.VInputTag([
        "selectedPatJets",
        "patJetsWithOwnRef",
    ]),
    maxObjects=cms.untracked.uint32(1)
)

process.out = cms.OutputModule("PoolOutputModule",
    fileName = cms.untracked.string('test.root')
)


process.p = cms.Path(
    process.patJetsWithOwnRef
    * process.simpleAnalyzer
    * process.patJetsPuCleaned
)

process.e = cms.EndPath(process.out)
