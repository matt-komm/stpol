import FWCore.ParameterSet.Config as cms

process = cms.Process("STPOLEFF")

process.load("FWCore.MessageService.MessageLogger_cfi")

process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(-1) )

process.source = cms.Source("PoolSource",
    fileNames = cms.untracked.vstring("")
)

#Command-line arguments
from SingleTopPolarization.Analysis.cmdlineParsing import enableCommandLineArguments
enableCommandLineArguments(process)

process.efficiencyAnalyzer = cms.EDAnalyzer('EfficiencyAnalyzer'
, histogrammableCounters = cms.untracked.vstring(["muPath", "elePath", "TotalEventsProcessed"])
, muPath = cms.untracked.vstring([
	"singleTopPathStep1MuPreCount", 
	"singleTopPathStep1MuPostCount", 
	"muPathPreCount",
	"muPathStepHLTsyncPostCount",
	"muPathOneIsoMuPostCount", 
	"muPathLooseMuVetoMuPostCount", 
	"muPathLooseEleVetoMuPostCount",
	"muPathNJetsPostCount",
	#"muPathMetMuSequencePostCount",
	"muPathMBTagsPostCount"
	]
)
, elePath = cms.untracked.vstring([
	"singleTopPathStep1MuPreCount", 
	"singleTopPathStep1ElePostCount", 
	"elePathPreCount",
	"elePathStepHLTsyncPostCount",
	"elePathOneIsoElePostCount", 
	"elePathLooseEleVetoElePostCount", 
	"elePathLooseMuVetoElePostCount",
	"elePathNJetsPostCount",
	#"elePathHasMETPostCount",
	"elePathMBTagsPostCount"
	]
)
, TotalEventsProcessed = cms.untracked.vstring(["PATTotalEventsProcessedCount", "STPOLSEL2TotalEventsProcessedCount"])
)

process.TFileService = cms.Service(
    "TFileService",
    fileName = cms.string("effHist.root"),
)

process.p = cms.Path(process.efficiencyAnalyzer)
