import FWCore.ParameterSet.Config as cms

def PartonStudySetup(process):
    #Select the generated top quark, light jet and charged lepton
    process.genParticleSelector = cms.EDProducer('GenParticleSelectorCompHep',
         src=cms.InputTag("genParticles")
    )

#    process.recoTrueTop = cms.EDProducer('SimpleCompositeCandProducer',
#        sources=cms.VInputTag(cms.InputTag("genParticleSelector", "trueNeutrino"),
#                     cms.InputTag("genParticleSelector", "trueBJet"),
#                     cms.InputTag("genParticleSelector", "trueLepton"))
#	 )

    process.cosThetaProducerTrueAll = cms.EDProducer('CosThetaProducer',
        topSrc=cms.InputTag("genParticleSelector", "trueTop"),
        jetSrc=cms.InputTag("genParticleSelector", "trueLightJet"),
        leptonSrc=cms.InputTag("genParticleSelector", "trueLepton"),
        Ecm=cms.double(8000)
    )

    process.cosThetaProducerWHelicityTrueAll = cms.EDProducer('CosThetaProducer',
        topSrc=cms.InputTag("genParticleSelector", "trueWboson"),
        jetSrc=cms.InputTag("genParticleSelector", "trueTop"),
        leptonSrc=cms.InputTag("genParticleSelector", "trueLepton"),
        Ecm=cms.double(8000)
    )

    #these parton-study samples are run only for t-channel MC
    process.partonStudyTrueSequence = cms.Sequence(
        process.genParticleSelector *
#        process.recoTrueTop *
        process.cosThetaProducerWHelicityTrueAll *
        process.cosThetaProducerTrueAll
    )

    process.partonStudyCompareSequence = cms.Sequence(
    )
