import FWCore.ParameterSet.Config as cms
from runconfs.step3.base_nocuts import *

process.muonCuts.requireOneMuon = False
process.muonCuts.doVetoLeptonCut = False
process.muonCuts.cutOnIso = cms.bool(False)
process.eleCuts.requireOneElectron = False
process.eleCuts.doVetoLeptonCut = False

process.jetCuts.cutOnNJets = False
process.bTagCuts.cutOnNTags = False

process.topCuts.applyMassCut = cms.bool(False)
process.weights.doWeights = cms.bool(True)
process.weights.doWeightSys = cms.bool(False)

process.metCuts.doMTCut = False

process.HLTmu.saveHLTVars = False
process.HLTmu.doCutOnHLT = False

process.HLTele.saveHLTVars = False
process.HLTele.doCutOnHLT = False

process.genParticles.doGenParticles = cms.bool(True)
process.bEfficiencyCalcs.doBEffCalcs = cms.bool(False)
