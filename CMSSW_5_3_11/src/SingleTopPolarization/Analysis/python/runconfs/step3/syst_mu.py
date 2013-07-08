import FWCore.ParameterSet.Config as cms
from base_nocuts import *
process.muonCuts.requireOneMuon = cms.bool(True)
process.muonCuts.requireOneElectron = cms.bool(False)
process.muonCuts.cutOnIso = cms.bool(True)
process.muonCuts.doVetoLeptonCut = cms.bool(True)

process.jetCuts.cutOnNJets = cms.bool(True)
process.jetCuts.applyRmsLj = cms.bool(False)
process.jetCuts.applyEtaLj = cms.bool(False)
process.jetCuts.nJetsMin = cms.int32(2)
process.jetCuts.nJetsMax = cms.int32(2)

process.bTagCuts.cutOnNTags  = cms.bool(True)
process.bTagCuts.nTagsMin = cms.int32(1)
process.bTagCuts.nTagsMax = cms.int32(1)

process.topCuts.applyMassCut = cms.bool(True)
process.weights.doWeights = cms.bool(True)
process.weights.doWeightSys = cms.bool(False)

process.mtMuCuts.doMTCut = cms.bool(False)

process.HLTmu.cutOnHLT = cms.bool(True)

process.genParticles.doGenParticles = cms.bool(options.isMC)
process.bEfficiencyCalcs.doBEffCalcs = cms.bool(False)
