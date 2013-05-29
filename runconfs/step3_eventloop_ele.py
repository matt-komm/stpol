import FWCore.ParameterSet.Config as cms
from runconfs.step3_eventLoop_cfg import *

process.fwliteInput.maxEvents = cms.int32(500000)
process.fwliteInput.outputEvery = cms.uint32(5000)

process.HLTele.doCutOnHLT = cms.bool(True)
process.eleCuts.requireOneElectron = cms.bool(True)
process.eleCuts.doVetoLeptonCut = cms.bool(True)

process.HLTmu.doCutOnHLT = cms.bool(False)
process.muonCuts.requireOneMuon = cms.bool(False)

process.jetCuts.cutOnNJets = cms.bool(True)
process.jetCuts.nJetsMin = cms.int32(0)
process.jetCuts.nJetsMax = cms.int32(3)
process.bTagCuts.nTagsMin = cms.int32(0)
process.bTagCuts.nTagsMax = cms.int32(2)

process.weights.doWeights = cms.bool(True)
process.weights.doWeightSys = cms.bool(True)
