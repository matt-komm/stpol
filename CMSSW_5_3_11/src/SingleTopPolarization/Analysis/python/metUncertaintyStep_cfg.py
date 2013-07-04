#Does the met uncertaintiy calculation using the official tool as documented in
#https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuidePATTools#MET_Systematics_Tools
import FWCore.ParameterSet.Config as cms
from FWCore.ParameterSet.VarParsing import VarParsing
from SingleTopPolarization.Analysis.config_step2_cfg import Config

options = VarParsing('analysis')
options.register ('globalTag', Config.globalTagMC,
          VarParsing.multiplicity.singleton,
          VarParsing.varType.string,
          "Global tag"
)
options.parseArguments()

process = cms.Process("STPOLSEL1B")
process.load("Configuration.Geometry.GeometryIdeal_cff")
process.load("Configuration.StandardSequences.FrontierConditions_GlobalTag_cff")
from Configuration.AlCa.autoCond import autoCond
process.GlobalTag.globaltag = cms.string(options.globalTag)
process.load("Configuration.StandardSequences.MagneticField_cff")

process.load("FWCore.MessageLogger.MessageLogger_cfi")
process.MessageLogger.cerr.FwkReport.reportEvery = 1000
process.MessageLogger.cerr.threshold = cms.untracked.string("INFO")
process.options = cms.untracked.PSet(wantSummary=cms.untracked.bool(True))

process.source = cms.Source("PoolSource",
    # replace 'myfile.root' with the source file you want to use
    fileNames=cms.untracked.vstring("")
)
process.source.fileNames = cms.untracked.vstring(options.inputFiles)
process.maxEvents = cms.untracked.PSet(input = cms.untracked.int32(options.maxEvents))

#Embed the reference to the original jet in the jets, which is constant during the propagation
process.patJetsWithOwnRef = cms.EDProducer('PatObjectOwnRefProducer<pat::Jet>',
    src=cms.InputTag("selectedPatJets")
)

#Note: this module causes a large memory increase when crossing the file boundary
#Reason - unknown, solution: limit processing to ~1 file.
from PhysicsTools.PatUtils.tools.metUncertaintyTools import runMEtUncertainties
runMEtUncertainties(process,
     electronCollection=cms.InputTag("electronsWithID"),
     photonCollection=None,
     muonCollection=cms.InputTag("muonsWithID"),
     tauCollection="", # "" means emtpy, None means cleanPatTaus
     jetCollection=cms.InputTag("patJetsWithOwnRef"),
#     jetCollection=cms.InputTag("selectedPatJets"),
     addToPatDefaultSequence=False
)
process.metUncertaintyPath = cms.Path(
    process.patJetsWithOwnRef *
    process.metUncertaintySequence
)

process.out = cms.OutputModule("PoolOutputModule",
    dropMetaData=cms.untracked.string("DROPPED"),
    fileName=cms.untracked.string('out_step1B.root'),
     SelectEvents=cms.untracked.PSet(
         SelectEvents=cms.vstring([])
     ),
    outputCommands=cms.untracked.vstring(
        #'drop *',
        'keep *',
        'drop patJets_*__STPOLSEL1B',
        'drop recoPFCandidates_pfCandsNotInJet__STPOLSEL1B',
        'drop patJets_selectedPatJets__PAT',
        'drop *_pfCandidateToVertexAssociation__STPOLSEL1B',
        'drop recoVertexs_selectedPrimaryVertexHighestPtTrackSumForPFMEtCorrType0__STPOLSEL1B',
        'drop recoVertexsToManyrecoTracksWithQuantityfloatAssociation_trackToVertexAssociation__STPOLSEL1B',
        'drop *_selectedVerticesForPFMEtCorrType0__STPOLSEL1B',
        'keep patJets_smearedPatJetsWithOwnRef__STPOLSEL1B',
        'keep patJets_smearedPatJetsWithOwnRefResDown__STPOLSEL1B',
        'keep patJets_smearedPatJetsWithOwnRefResUp__STPOLSEL1B',
        'keep patJets_shiftedPatJetsWithOwnRefEnUpForCorrMEt__STPOLSEL1B',
        'keep patJets_shiftedPatJetsWithOwnRefEnDownForCorrMEt__STPOLSEL1B',
        'drop recoPFCandidates_*_pfCandidates_PAT',
        'drop recoPFMETs_pfMET__PAT',
        'drop recoPFMETs_pfMet__RECO',
        'drop recoGenMETs_genMetTrue__SIM',
        'drop recoPFCandidates_particleFlow__RECO',
        'drop recoConversions_allConversions__RECO',
        'drop recoVertexCompositeCandidates_generalV0Candidates_*_RECO',
        'drop recoTracks_generalTracks__RECO',
        'drop recoBeamSpot_offlineBeamSpot__RECO',
        'drop recoMuons_muons__RECO',
    )
)
process.out.fileName = cms.untracked.string(options.outputFile)
process.outpath = cms.EndPath(process.out)
