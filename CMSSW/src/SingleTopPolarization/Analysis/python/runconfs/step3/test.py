import FWCore.ParameterSet.Config as cms
from SingleTopPolarization.Analysis.runconfs.step3.base_nocuts import *
process.fwliteInput.maxEvents = cms.int32(50000)

process.muonCuts.requireOneMuon = False
process.muonCuts.doVetoLeptonCut = False

process.eleCuts.requireOneElectron = False
process.eleCuts.doVetoLeptonCut = False

process.jetCuts.cutOnNJets = False
process.bTagCuts.cutOnNTags = False
process.jetCuts.nJetsMin = 2
process.jetCuts.nJetsMax = 2

process.HLTmu.saveHLTVars = False
process.HLTmu.doCutOnHLT = False

process.HLTele.saveHLTVars = False
process.HLTele.doCutOnHLT = False
