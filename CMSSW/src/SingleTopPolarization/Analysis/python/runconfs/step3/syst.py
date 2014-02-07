import FWCore.ParameterSet.Config as cms
from base_nocuts import *

process.muonCuts.doVetoLeptonCut = cms.bool(True)
process.eleCuts.doVetoLeptonCut = cms.bool(True)

process.jetCuts.cutOnNJets = cms.bool(True)
process.jetCuts.applyRmsLj = cms.bool(True)
process.jetCuts.applyEtaLj = cms.bool(False)
process.jetCuts.nJetsMin = cms.int32(2)
process.jetCuts.nJetsMax = cms.int32(2)

process.bTagCuts.cutOnNTags  = cms.bool(True)
process.bTagCuts.nTagsMin = cms.int32(1)
process.bTagCuts.nTagsMax = cms.int32(1)

process.topCuts.applyMassCut = cms.bool(True)

process.weights.doWeights = cms.bool(True)
process.weights.doWeightSys = cms.bool(True)

process.genParticles.doGenParticles = cms.bool(options.isMC)
process.bEfficiencyCalcs.doBEffCalcs = cms.bool(False)

if(options.lepton=="mu"):
    process.muonCuts.isoCut = cms.double(0.3)
    process.muonCuts.isoCutHigh = cms.double(0.5)
