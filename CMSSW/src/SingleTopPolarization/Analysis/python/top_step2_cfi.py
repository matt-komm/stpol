import FWCore.ParameterSet.Config as cms

def TopRecoSetup(process, conf, leptonSource="goodSignalLeptons", bTagSource="highestBTagJet", untaggedJetSource="lowestBTagJet"):
    #Reconstruct the 4-momentum of the top quark by adding the momenta of the b-jet, the neutrino and the charged lepton

    #Combine the METs to a single collection
    process.goodMETs = cms.EDProducer(
         'CandRefCombiner',
         sources=cms.vstring(["muGoodMETs", "eleGoodMETs"]),
         maxOut=cms.uint32(1),
         minOut=cms.uint32(1),
         logErrors=cms.bool(True)
    )


    #Combine the neutrino collections produced in the electron and muon paths, taking exactly 1 neutrino per event
    process.recoNu = cms.EDProducer(
         'CandRefCombiner',
         sources=cms.vstring(["recoNuProducerMu", "recoNuProducerEle"]),
         maxOut=cms.uint32(1),
         minOut=cms.uint32(1),
         logErrors=cms.bool(False)
    )

    process.recoTop = cms.EDProducer('SimpleCompositeCandProducer',
        sources=cms.VInputTag(["recoNu", bTagSource, leptonSource])
    )

    process.topCount = cms.EDProducer('CollectionSizeProducer<reco::Candidate>',
        src = cms.InputTag('recoTop')
    )

    process.cosTheta = cms.EDProducer('CosThetaProducer',
        topSrc=cms.InputTag("recoTop"),
        jetSrc=cms.InputTag(untaggedJetSource),
        leptonSrc=cms.InputTag("goodSignalLeptons"),
        Ecm=cms.double(8000)
    )

    process.topRecoSequenceMu = cms.Sequence(
        process.goodMETs *
        process.recoNuProducerMu *
        process.recoNu *
        process.recoTop *
        process.topCount *
        process.cosTheta
    )

    process.topRecoSequenceEle = cms.Sequence(
        process.goodMETs *
        process.recoNuProducerEle *
        process.recoNu *
        process.recoTop *
        process.topCount *
        process.cosTheta
    )
