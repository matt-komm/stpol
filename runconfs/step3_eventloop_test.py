import FWCore.ParameterSet.Config as cms
from runconfs.step3_eventloop_base_nocuts import *
process.fwliteInput.maxEvents = cms.int32(500000)

process.muonCuts.requireOneMuon = True
process.muonCuts.doVetoLeptonCut = True

process.eleCuts.requireOneElectron = False
process.eleCuts.doVetoLeptonCut = False

process.jetCuts.cutOnNJets = True
process.bTagCuts.cutOnNTags = False
process.jetCuts.nJetsMin = 2
process.jetCuts.nJetsMax = 2

process.mtMuCuts.doMTCut = False

process.HLTmu.saveHLTVars = False
process.HLTmu.doCutOnHLT = True

process.HLTele.saveHLTVars = False
process.HLTele.doCutOnHLT = False
