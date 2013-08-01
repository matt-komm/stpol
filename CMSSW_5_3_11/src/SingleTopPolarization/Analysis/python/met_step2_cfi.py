import FWCore.ParameterSet.Config as cms
from SingleTopPolarization.Analysis.met_phi_corr_cfg import calculateMetPhiCorrectedMET
from SingleTopPolarization.Analysis.utils import *

def metSequence(process, conf, prefix, met_src, lepton_src):
    seqCorr = calculateMetPhiCorrectedMET(process, prefix, conf, met_src)
    goodMETs = cms.EDFilter("CandViewSelector",
        src=cms.InputTag(
            prep(prefix, "phiCorrMETs") if conf.doMETSystShift else met_src
        ),
        cut=cms.string("pt>%f" % conf.Leptons.transverseMassDef)
    )

    MTW = cms.EDProducer(
        'CandTransverseMassProducer',
        collections=cms.untracked.vstring([
            prep(prefix, "goodMETs"),
            lepton_src
        ])
    )

    seq = cms.Sequence(
        seqCorr *
        goodMETs *
        MTW
    )

    goodMETdest = sa(process, prefix, "goodMETs", goodMETs)
    sa(process, prefix, "MTW", MTW)
    sa(process, prefix, "metSequence", seq)
    return goodMETdest


