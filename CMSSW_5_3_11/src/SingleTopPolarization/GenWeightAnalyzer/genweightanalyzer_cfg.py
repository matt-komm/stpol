import FWCore.ParameterSet.Config as cms

process = cms.Process("Demo")

process.load("FWCore.MessageService.MessageLogger_cfi")
process.MessageLogger.cerr.FwkReport.reportEvery = 50000

process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(-1) )

process.source = cms.Source("PoolSource",
    fileNames = cms.untracked.vstring(
        'file:/hdfs/local/joosep/stpol/step2_WJets_sherpa_Jun7/WD_WJets_sherpa_nominal/res/output_117_2_hef.root'
    )
)

process.demo = cms.EDAnalyzer('GenWeightAnalyzer'
)

process.TFileService = cms.Service("TFileService",
    fileName = cms.string("histo.root"),
    closeFileFast = cms.untracked.bool(True)
)


process.p = cms.Path(process.demo)
