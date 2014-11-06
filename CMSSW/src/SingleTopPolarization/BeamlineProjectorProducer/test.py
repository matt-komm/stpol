import FWCore.ParameterSet.Config as cms
process = cms.Process("TEST")

process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(10) )
process.source = cms.Source ("PoolSource",
    fileNames=cms.untracked.vstring(
        "root://xrootd.unl.edu//store/mc/Summer12_DR53X/TToLeptons_t-channel_8TeV-powheg-tauola/AODSIM/PU_S10_START53_V7A-v1/0000/0034258A-D7DE-E111-BEE3-00261834B529.root"
    )
)

process.genParticleSelector = cms.EDProducer('GenParticleSelectorPowheg',
    src=cms.InputTag("genParticles")
)
process.hasGenLepton = cms.EDFilter(
    "PATCandViewCountFilter",
    src=cms.InputTag("genParticleSelector", "trueLepton"),
    minNumber=cms.uint32(1),
    maxNumber=cms.uint32(1),
)
process.beamlineProjector=cms.EDProducer("BeamlineProjectorProducer",
    src=cms.VInputTag(
        cms.InputTag("genParticleSelector","trueLightJet")
    )
)

process.multiCosTheta=cms.EDProducer("MultiCosThetaProducer",
    ljLeptonTopCosTheta=cms.PSet(
        restFrame=cms.InputTag("genParticleSelector","trueTop"),
        particles=cms.VInputTag(cms.InputTag("genParticleSelector","trueLepton"),cms.InputTag("genParticleSelector","trueLightJet"))
    ),
    lqBeamlineLeptonTopCosTheta=cms.PSet(
        restFrame=cms.InputTag("genParticleSelector","trueTop"),
        particles=cms.VInputTag(cms.InputTag("genParticleSelector","trueLepton"),cms.InputTag("beamlineProjector","trueLightJet-genParticleSelector"))
    ),
    wHelicityCosTheta=cms.PSet(
        restFrame=cms.InputTag("genParticleSelector","trueWboson"),
        particles=cms.VInputTag(cms.InputTag("genParticleSelector","trueLepton"),cms.InputTag("genParticleSelector","trueTop"))
    )
)

process.p0 = cms.Path(process.genParticleSelector*process.hasGenLepton*process.beamlineProjector*process.multiCosTheta)

process.out= cms.OutputModule("PoolOutputModule",
    splitLevel=cms.untracked.int32(99),
    fileName=cms.untracked.string("test.root"),
    SelectEvents=cms.untracked.PSet(
        SelectEvents=cms.vstring('p0')
    )
)

process.outpath = cms.EndPath(process.out)
