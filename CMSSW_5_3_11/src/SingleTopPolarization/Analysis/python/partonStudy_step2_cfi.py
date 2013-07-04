import FWCore.ParameterSet.Config as cms

def PartonStudySetup(process, untaggedSrc="fwdMostLightJet"):
    process.cosThetaProducerTrueTop = cms.EDProducer('CosThetaProducer',
        topSrc=cms.InputTag("genParticleSelector", "trueTop"),
        jetSrc=cms.InputTag(untaggedSrc),
        leptonSrc=cms.InputTag("goodSignalLeptons")
    )

    process.cosThetaProducerTrueLepton = cms.EDProducer('CosThetaProducer',
        topSrc=cms.InputTag("recoTop"),
        jetSrc=cms.InputTag(untaggedSrc),
        leptonSrc=cms.InputTag("genParticleSelector", "trueLepton")
    )

    process.cosThetaProducerTrueJet = cms.EDProducer('CosThetaProducer',
        topSrc=cms.InputTag("recoTop"),
        jetSrc=cms.InputTag("genParticleSelector", "trueLightJet"),
        leptonSrc=cms.InputTag("goodSignalLeptons")
    )

    #Select the generated leptons associated with a t-quark
    process.genLeptonsT = cms.EDFilter("CandViewSelector",
        src=cms.InputTag("genParticles"),
        cut=cms.string(
            #Consider muons or electrons
            "(abs(pdgId()) == 13 || abs(pdgId()) == 11 ) \
             && abs((mother().pdgId()))==24" #The first mother is the "oldest" particle. In our case, we are looking for a top quark
        )
    )
    process.genLeptonsTCount = cms.EDProducer('CollectionSizeProducer<reco::Candidate>',
        src = cms.InputTag('genLeptonsT')
    )

    #Select the generated top quark, light jet and charged lepton
    process.genParticleSelector = cms.EDProducer('GenParticleSelector',
         src=cms.InputTag("genParticles")
    )

    process.hasGenLepton = cms.EDFilter(
        "PATCandViewCountFilter",
        src=cms.InputTag("genParticleSelector", "trueLepton"),
        minNumber=cms.uint32(1),
        maxNumber=cms.uint32(1),
    )

    process.cosThetaProducerTrueAll = cms.EDProducer('CosThetaProducer',
        topSrc=cms.InputTag("genParticleSelector", "trueTop"),
        jetSrc=cms.InputTag("genParticleSelector", "trueLightJet"),
        leptonSrc=cms.InputTag("genParticleSelector", "trueLepton")
    )

    process.matrixCreator = cms.EDAnalyzer('TransferMatrixCreator',
        src = cms.InputTag("cosTheta", "cosThetaLightJet"),
        trueSrc = cms.InputTag("cosThetaProducerTrueAll", "cosThetaLightJet")
    )

    process.leptonComparer = cms.EDAnalyzer('ParticleComparer',
        src = cms.InputTag("goodSignalLeptons"),
        trueSrc = cms.InputTag("genParticleSelector", "trueLepton"),
        maxMass=cms.untracked.double(.3)
    )

    process.jetComparer = cms.EDAnalyzer('ParticleComparer',
        src = cms.InputTag("untaggedJets"),
        trueSrc = cms.InputTag("genParticleSelector", "trueLightJet"),
        maxMass=cms.untracked.double(40.)
    )

    process.topComparer = cms.EDAnalyzer('ParticleComparer',
        src = cms.InputTag("recoTop"),
        trueSrc = cms.InputTag("genParticleSelector", "trueTop"),
        maxMass=cms.untracked.double(300.)
    )

    #This parton-study module is run for all samples in MC
    process.commonPartonSequence = cms.Sequence(
        process.genLeptonsT *
        process.genLeptonsTCount
    )

    #these parton-study samples are run only for t-channel MC
    process.partonStudyTrueSequence = cms.Sequence(
        process.genParticleSelector *
        process.hasGenLepton *
        process.cosThetaProducerTrueAll
    )

    #Creates histograms (only available via TFileService)
    process.partonStudyCompareSequence = cms.Sequence(
        process.hasGenLepton *

        #These need reconstructed/selected jets, leptons, tops
        process.cosThetaProducerTrueTop *
        process.cosThetaProducerTrueLepton *
        process.cosThetaProducerTrueJet
        #process.matrixCreator *
        #process.leptonComparer *
        #process.jetComparer *
        #process.topComparer
    )
