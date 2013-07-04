import FWCore.ParameterSet.Config as cms

def WeightSetup(process, conf):
    if not conf.isMC:
        raise ValueError("Weighting is defined only for MC!")

    process.weightSequence = cms.Sequence()
    if conf.subChannel.lower() == "ttbar":
        channel = dict()
        channel["TTJets_FullLept"] = "FullLept"
        channel["TTJets_SemiLept"] = "FullLept"
        channel["TTbar"] = "FullSemiLept"
        process.ttbarTopWeight = cms.EDProducer(
            'TopPtReweightProducer',
            src=cms.InputTag("genParticles"),
            channel=channel[conf.subProcess]
        )
        process.weightSequence += process.ttbarTopWeight

    process.puWeightProducer = cms.EDProducer('PUWeightProducer'
        , maxVertices = cms.uint32(50)
        , srcDistribution = cms.vdouble(conf.srcPUDistribution)
        , destDistribution = cms.vdouble(conf.destPUDistribution)
    )
    process.weightSequence += process.puWeightProducer
