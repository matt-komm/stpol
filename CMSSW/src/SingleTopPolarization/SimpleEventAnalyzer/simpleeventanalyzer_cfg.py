import FWCore.ParameterSet.Config as cms

process = cms.Process("Demo")

process.load("FWCore.MessageLogger.MessageLogger_cfi")
process.MessageLogger = cms.Service("MessageLogger",
       destinations=cms.untracked.vstring(
                                              'cout',
                    ),
       cout=cms.untracked.PSet(
        threshold=cms.untracked.string('DEBUG')
        ),
)
process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(-1) )
process.options   = cms.untracked.PSet( wantSummary = cms.untracked.bool(True) )
process.source = cms.Source("PoolSource",
    fileNames = cms.untracked.vstring(
        'file:/hdfs/cms/store/user/jpata/T_t-channel_TuneZ2star_8TeV-powheg-tauola/stpol_v3_1/33f82354a36574c1158b3181d92c6119/step1_Skim_10_1_TYz.root'
#        'file:/hdfs/local/stpol/joosep/FEFF01BD-87DC-E111-BC9E-003048678F8E.root'
    )
)

#process.simpleAnalyzer = cms.EDAnalyzer(
#	'SimpleMuonAnalyzer',
#	interestingCollections = cms.untracked.VInputTag(["muonsWithID", "shiftedMuonsWithIDenDown"])
#)

process.simpleAnalyzer = cms.EDAnalyzer(
	'SimpleEventAnalyzer',
    interestingCollections = cms.untracked.VInputTag([

        "selectedPatJets",
#        "smearedPatJets",
#        "smearedPatJetsResUp",
#        "smearedPatJetsResDown",
#
#        "selectedPatMuons",
#        "shiftedPatMuonsEnDown",
#        "shiftedPatMuonsEnUp",
#
#        "selectedPatElectrons",
#        "shiftedPatElectronsEnDown",
#        "shiftedPatElectronsEnUp"
    ]),
    maxObjects=cms.untracked.uint32(1)
)

process.p = cms.Path(process.simpleAnalyzer)
