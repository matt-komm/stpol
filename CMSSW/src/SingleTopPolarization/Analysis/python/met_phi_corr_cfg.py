#!/usr/bin/env python
"""
Based on the recipe in https://twiki.cern.ch/twiki/bin/view/CMSPublic/WorkBookMetAnalysis#MET_x_y_Shift_Correction_for_mod
"""
from SingleTopPolarization.Analysis.test_files import testfiles
from SingleTopPolarization.Analysis.utils import *

import FWCore.ParameterSet.Config as cms

def sd(x,y):
    return cms.PSet(tag=cms.untracked.string(x), quantity=cms.untracked.string(y))

def ntp_p4(coll):
    ntp = cms.EDProducer(
        "CandViewNtpProducer2",
        src = cms.InputTag(coll),
        variables = cms.VPSet(
            sd("Pt", "pt"),
            sd("Eta", "eta"),
            sd("Phi", "phi"),
            sd("Mass", "mass"),
        )
    )
    return ntp

def calculateMetPhiCorrectedMET(process, prefix, conf, src):
    process.load("JetMETCorrections.Type1MET.pfMETsysShiftCorrections_cfi")

    if conf.isMC:
        process.pfMEtSysShiftCorr.parameter = process.pfMEtSysShiftCorrParameters_2012runAvsNvtx_mc
    else:
        process.pfMEtSysShiftCorr.parameter = process.pfMEtSysShiftCorrParameters_2012runAvsNvtx_data

    selectedVerticesForMETCorr = process.selectedVerticesForMEtCorr.clone(
        src=cms.InputTag("goodOfflinePrimaryVertices"),
    )
    systShiftMETCorr = process.pfMEtSysShiftCorr.clone(
        src=cms.InputTag(src),
        srcVertices = cms.InputTag(prep(prefix, "selectedVerticesForMETCorr")),
    )

    prod = cms.EDProducer("CorrectedPATMETProducer",
        src = cms.InputTag(src),
        applyType1Corrections = cms.bool(True),
        srcType1Corrections = cms.VInputTag(
            cms.InputTag(
            prep(prefix, "systShiftMETCorr")
            )
        ),
        type0Rsoft = cms.double(0.6),
        applyType2Corrections = cms.bool(False),
        srcCHSSums = cms.VInputTag(cms.InputTag("pfchsMETcorr","type0")),
        applyType0Corrections = cms.bool(False)
    )
    seq = cms.Sequence(
        selectedVerticesForMETCorr *
        systShiftMETCorr *
        prod
    )
    sa(process, prefix, "systShiftMETCorr", systShiftMETCorr)
    sa(process, prefix, "selectedVerticesForMETCorr", selectedVerticesForMETCorr)
    sa(process, prefix, "phiCorrMETs", prod)
    sa(process, prefix, "metPhiCorrSequence", seq)
    return seq


if __name__=="__main__":
    met = "patType1CorrectedPFMet"
    process = cms.Process("STPOLMETPHICORR")
    process.corrSeq = calculateMetPhiCorrectedMET(process, "ele", met)
    process.load("FWCore.MessageService.MessageLogger_cfi")
    process.MessageLogger.cerr.FwkReport.reportEvery = 1000
    process.MessageLogger.cerr.threshold = cms.untracked.string("INFO")

    process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(-1) )

    process.source = cms.Source("PoolSource",
        fileNames = cms.untracked.vstring(
            testfiles["step1"]["signal"]
        )
    )

    process.corrPath = cms.Path(
        process.corrSeq
    )

    process.ntpPath = cms.Path()
    process.ntpMET1 = ntp_p4(met)
    process.ntpMET2 = ntp_p4("phiCorrMET")
    process.ntpPath += (
        process.ntpMET1 *
        process.ntpMET2
    )

    process.out = cms.OutputModule("PoolOutputModule",
        dropMetaData=cms.untracked.string("DROPPED"),
        splitLevel=cms.untracked.int32(99),
        fileName = cms.untracked.string('met_corr.root'),
        outputCommands=cms.untracked.vstring(
            'drop *',
            'keep float_*_*_*',
            'keep double_*_*_*',
            'keep floats_*_*_*',
            'keep doubles_*_*_*',
        )
    )
    process.e = cms.EndPath(process.out)

    process.options = cms.untracked.PSet(wantSummary=cms.untracked.bool(True))

