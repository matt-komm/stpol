import FWCore.ParameterSet.Config as cms
from SingleTopPolarization.Analysis.met_phi_corr_cfg import calculateMetPhiCorrectedMET
from SingleTopPolarization.Analysis.utils import *

def metSequence(process, conf, prefix, met_src, lepton_src):
    #seqCorr = calculateMetPhiCorrectedMET(process, prefix, conf, met_src)
    #met_name = prep(prefix, "phiCorrMETs") if conf.doMETSystShift else met_src
    goodMETs = cms.EDFilter("CandViewSelector",
        src=cms.InputTag(met_src),
        cut=cms.string("pt>%f" % conf.Leptons.transverseMassDef)
    )
    print("goodMETs=", goodMETs)

    MTW = cms.EDProducer(
        'CandTransverseMassProducer',
        collections=cms.untracked.vstring([
            prep(prefix, "goodMETs"),
            lepton_src
        ])
    )

    seq = cms.Sequence(
        goodMETs *
        MTW
    )

    #Set the met processes as attributes to the main process
    goodMETdest = sa(process, prefix, "goodMETs", goodMETs)
    sa(process, prefix, "MTW", MTW)
    sa(process, prefix, "metSequence", seq)

    return goodMETdest


