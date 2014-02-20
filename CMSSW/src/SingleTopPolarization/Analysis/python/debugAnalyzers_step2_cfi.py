import FWCore.ParameterSet.Config as cms

def DebugAnalyzerSetup(process):
   process.oneIsoMuIDs = cms.EDAnalyzer('EventIDAnalyzer',
       name=cms.untracked.string("oneIsoMu")
   )

   process.nJetIDs = cms.EDAnalyzer('EventIDAnalyzer',
       name=cms.untracked.string("nJetIDs")
   )

   process.goodMuonsAnalyzer = cms.EDAnalyzer(
       'SimpleMuonAnalyzer',
       interestingCollections = cms.untracked.VInputTag(["goodSignalMuons"])
   )

   process.selectedPatElectronsAnalyzer = cms.EDAnalyzer(
       'SimpleElectronAnalyzer',
       interestingCollections = cms.untracked.VInputTag(["electronsWithID"])
   )

   process.goodElectronsAnalyzer = cms.EDAnalyzer(
       'SimpleElectronAnalyzer',
       interestingCollections = cms.untracked.VInputTag(["goodSignalElectrons"])
   )

   process.selectedPatMuonsAnalyzer = cms.EDAnalyzer(
       'SimpleMuonAnalyzer',
       interestingCollections = cms.untracked.VInputTag(["muonsWithID"])
   )

   process.eleAnalyzer = cms.EDAnalyzer(
       'SimpleEventAnalyzer',
       interestingCollections = cms.untracked.VInputTag(["selectedPatElectrons"])
   )

   process.patJetsAnalyzer = cms.EDAnalyzer(
       'SimpleJetAnalyzer',
       interestingCollections = cms.untracked.VInputTag(["selectedPatJets"])
   )

   process.goodJetsPreAnalyzer = cms.EDAnalyzer(
       'SimpleJetAnalyzer',
       interestingCollections = cms.untracked.VInputTag(["smearedJets"])
   )
   process.goodJetsPostAnalyzer = cms.EDAnalyzer(
       'SimpleJetAnalyzer',
       interestingCollections = cms.untracked.VInputTag(["goodJets"])
   )

   process.dumpContent = cms.EDAnalyzer('EventContentAnalyzer')
