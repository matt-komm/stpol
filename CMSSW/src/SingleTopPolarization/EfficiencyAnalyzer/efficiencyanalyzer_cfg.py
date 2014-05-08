import FWCore.ParameterSet.Config as cms
from FWCore.ParameterSet.VarParsing import VarParsing

process = cms.Process("Demo")

process.load("FWCore.MessageService.MessageLogger_cfi")

process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(-1) )

options = VarParsing('analysis')
options.parseArguments()
process.source = cms.Source("PoolSource",
    # replace 'myfile.root' with the source file you want to use
    fileNames = cms.untracked.vstring(options.inputFiles)
)

process.maxEvents = cms.untracked.PSet(
  input = cms.untracked.int32(options.maxEvents)
)

process.load("FWCore.MessageLogger.MessageLogger_cfi")
process.MessageLogger.cerr.FwkReport.reportEvery = 10000

process.efficiencyAnalyzer = cms.EDAnalyzer('EfficiencyAnalyzer',
    histogrammableCounters = cms.untracked.vstring(["all", "step1mu", "step1ele", "step2mu", "step2ele"]),
    all = cms.untracked.vstring([
        "PATTotalEventsProcessedCount",
        "STPOLSEL2TotalEventsProcessedCount",
    ]),
    step1mu = cms.untracked.vstring([
        "singleTopPathStep1MuPreCount",
        "singleTopPathStep1MuPostCount"
    ]),
    step1ele = cms.untracked.vstring([
        "singleTopPathStep1ElePreCount",
        "singleTopPathStep1ElePostCount"
    ]),
    step2mu = cms.untracked.vstring([
        "muPathPreCount",
        "muPathStepHLTsyncMuPostCount",
        "muPathOneIsoMuPostCount",
        "muPathLooseEleVetoMuPostCount",
        "muPathLooseMuVetoMuPostCount",
        "muPathNJetsPostCount",
        "muPathMBTagsPostCount",
        "muPathMetMuSequencePostCount"
    ]),
    step2ele = cms.untracked.vstring([
        "elePathPreCount",
        "elePathStepHLTsyncElePostCount",
        "elePathOneIsoElePostCount",
        "elePathLooseEleVetoElePostCount",
        "elePathLooseMuVetoElePostCount",
        "elePathNJetsPostCount",
        "elePathMBTagsPostCount",
        "elePathMetEleSequencePostCount"
    ])
)

process.TFileService = cms.Service(
    "TFileService",
    fileName = cms.string("histo.root"),
)



process.p = cms.Path(process.efficiencyAnalyzer)
