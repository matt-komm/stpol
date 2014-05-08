import FWCore.ParameterSet.Config as cms
from SingleTopPolarization.Analysis import sample_types
import logging

def WeightSetup(process, conf):
    if not conf.isMC:
        raise ValueError("Weighting is defined only for MC!")

    process.weightSequence = cms.Sequence()
    if sample_types.is_ttbar(conf.subChannel):
        logging.info("Enabling top pt reweighting for subchannel %s" % conf.subChannel)
        channel = dict()
        channel["TTJets_FullLept"] = "FullLept"
        channel["TTJets_SemiLept"] = "SemiLept"

        #FIXME: general sample metadata mechanism
        for s in [
            "TTbar", "TTJets", "TTJets_MassiveBinDECAY",
            "TTJets_mass166_5", "TTJets_mass178_5",
            "TTJets_mass169_5", "TTJets_mass175_5",
            "TTJets_matchingdown", "TTJets_matchingup",
            "TTJets_scaleup", "TTJets_scaledown"
        ]:
            channel[s] = "FullSemiLept"

        process.ttbarTopWeight = cms.EDProducer(
            'TopPtReweightProducer',
            src=cms.InputTag("genParticles"),
            channel=cms.string(channel[conf.subChannel])
        )
        process.weightSequence += process.ttbarTopWeight

    process.puWeightProducer = cms.EDProducer('PUWeightProducer'
        , maxVertices = cms.uint32(50)
        , srcDistribution = cms.vdouble(conf.srcPUDistribution)
        , weightFileNominal=cms.FileInPath("data/pu_weights/data_PU_nominal.root")
        , weightFileUp=cms.FileInPath("data/pu_weights/data_PU_up.root")
        , weightFileDown=cms.FileInPath("data/pu_weights/data_PU_down.root")
    )
    process.weightSequence += process.puWeightProducer
