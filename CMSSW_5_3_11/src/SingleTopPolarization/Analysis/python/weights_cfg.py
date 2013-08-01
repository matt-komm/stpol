import FWCore.ParameterSet.Config as cms

def WeightSetup(process, conf):
    if not conf.isMC:
        raise ValueError("Weighting is defined only for MC!")

    process.weightSequence = cms.Sequence()
    if conf.subChannel.lower() == "ttbar":
        channel = dict()
        channel["TTJets_FullLept"] = "FullLept"
        channel["TTJets_SemiLept"] = "SemiLept"
        channel["TTbar"] = "FullSemiLept"
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
