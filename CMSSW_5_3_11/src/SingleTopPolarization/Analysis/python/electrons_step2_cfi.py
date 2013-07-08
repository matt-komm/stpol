import FWCore.ParameterSet.Config as cms
import SingleTopPolarization.Analysis.eventCounting as eventCounting
import SingleTopPolarization.Analysis.sample_types as sample_types

import re
#Remove the excess whitespace from formatting
def clean_whitespace(s):
    return re.sub( '\s+', ' ', s).strip()

"""
This method sets up the electron channel lepton selection.
isMC - run on MC (vs. run on data)
mvaCut - the electron multivariate ID cut (electrons with MVA<cut pass as signal electrons)
doDebug - enable various debugging printout modules
metType - choose either between 'MtW' for the W transverse mass or 'MET' for a simple MET cut
reverseIsoCut - 'True' to choose the anti-isolated leptons, 'False' to choose isolated leptons
"""
def ElectronSetup(process, conf):

    goodElectronCut = "%s>30" % conf.Electrons.pt
    goodElectronCut += " && (abs(eta) < 2.5)"
    goodElectronCut += " && !(1.4442 < abs(superCluster.eta) < 1.5660)"
    goodElectronCut += " && passConversionVeto() "
    goodSignalElectronCut = goodElectronCut

    #Sanity cut
    goodSignalElectronCut += " && (electronID('mvaTrigV0') > 0.0)"
    if not conf.Electrons.reverseIsoCut:
        #Latest MVA ID WP-s
        #https://twiki.cern.ch/twiki/bin/viewauth/CMS/MultivariateElectronIdentification#Training_of_the_MVA
        goodSignalElectronCut += " && ((abs(eta)>0.0 && abs(eta) < 0.8 && (electronID('mvaTrigV0') > %f))" % 0.94
        goodSignalElectronCut += " || (abs(eta)>0.8 && abs(eta) < 1.479 && (electronID('mvaTrigV0') > %f))" % 0.85
        goodSignalElectronCut += " || (abs(eta)>1.479 && abs(eta) < 1.479 && (electronID('mvaTrigV0') > %f)))" % 0.92

    #Impact parameter dropped because using MVA ID
    #https://hypernews.cern.ch/HyperNews/CMS/get/egamma-elecid/72.html
    #goodSignalElectronCut += " && abs(userFloat('dxy')) < 0.02"
    goodSignalElectronCut += " && userInt('gsfTrack_trackerExpectedHitsInner_numberOfHits') <= 0"

    if conf.Electrons.cutOnIso:
        if conf.Electrons.reverseIsoCut:
        #Choose anti-isolated region
            goodSignalElectronCut += ' && userFloat("{0}") >= {1} && userFloat("{0}") < {2}'.format(
                conf.Electrons.relIsoType,
                conf.Electrons.relIsoCutRangeAntiIsolatedRegion[0],
                conf.Electrons.relIsoCutRangeAntiIsolatedRegion[1]
                )
        #Choose isolated region
        else:
            goodSignalElectronCut += ' && userFloat("{0}") >= {1} && userFloat("{0}") < {2}'.format(
                conf.Electrons.relIsoType,
                conf.Electrons.relIsoCutRangeIsolatedRegion[0],
                conf.Electrons.relIsoCutRangeIsolatedRegion[1]
            )

    #Trigger preselection emulation
    #https://twiki.cern.ch/twiki/bin/viewauth/CMS/MultivariateElectronIdentification#Training_of_the_MVA
    goodSignalElectronCut += " && (\
            (abs(superCluster.eta()) < 1.479 && \
            sigmaIetaIeta() < 0.014 && \
            hadronicOverEm() < 0.15 && \
            dr03TkSumPt()/pt() < 0.2 && \
            dr03EcalRecHitSumEt()/pt() < 0.2 && \
            dr03HcalTowerSumEt()/pt() < 0.2 && \
            userInt('gsfTrack_trackerExpectedHitsInner_numberOfHitsLost') == 0) || \
            (abs(superCluster.eta()) >= 1.479 && \
            sigmaIetaIeta() < 0.035 && \
            hadronicOverEm() < 0.10 && \
            dr03TkSumPt()/pt() < 0.2 && \
            dr03EcalRecHitSumEt()/pt < 0.2 && \
            dr03HcalTowerSumEt()/pt < 0.2 && \
            userInt('gsfTrack_trackerExpectedHitsInner_numberOfHitsLost') == 0)\
        )"
    goodSignalElectronCut = clean_whitespace(goodSignalElectronCut)

    looseVetoElectronCut = "%s > 20.0" % conf.Electrons.pt
    looseVetoElectronCut += " && (abs(superCluster().eta()) < 2.5)"

    #Veto cut based ID: https://twiki.cern.ch/twiki/bin/view/CMS/EgammaCutBasedIdentification
    cutBasedLooseID = " && \
        (abs(superCluster().eta()) < 1.479 && (\
            abs(deltaEtaSuperClusterTrackAtVtx()) < 0.007 && \
            abs(deltaPhiSuperClusterTrackAtVtx()) < 0.8 && \
            sigmaIetaIeta() < 0.01 && \
            hadronicOverEm() < 0.15 && \
            userFloat('dxy') < 0.04 && \
            userFloat('dz') < 0.2 \
        )) || (\
        abs(superCluster().eta())>1.479 && abs(superCluster().eta())<2.5 && (\
            abs(deltaEtaSuperClusterTrackAtVtx()) < 0.01 && \
            abs(deltaPhiSuperClusterTrackAtVtx()) < 0.7 && \
            sigmaIetaIeta() < 0.03 && \
            userFloat('dxy') < 0.04 && \
            userFloat('dz') < 0.2 \
        ))"
    looseVetoElectronCut += cutBasedLooseID
    looseVetoElectronCut += " && (userFloat('{0}') < {1})".format(conf.Electrons.relIsoType, conf.Electrons.looseVetoRelIsoCut)
    looseVetoElectronCut = clean_whitespace(looseVetoElectronCut)

    #Loose veto electrons must not overlap with good signal electrons
    looseVetoElectronCut += " && !(%s)" % goodSignalElectronCut

    print "goodSignalElectronCut={0}".format(goodSignalElectronCut)
    print "looseVetoElectronCut={0}".format(looseVetoElectronCut)

    process.goodSignalElectrons = cms.EDFilter("CandViewSelector",
      src=cms.InputTag("electronsWithCorrectedEcalIso"), cut=cms.string(goodSignalElectronCut)
    )

    process.looseVetoElectrons = cms.EDFilter("CandViewSelector",
      src=cms.InputTag("electronsWithCorrectedEcalIso"),
      cut=cms.string(looseVetoElectronCut)
    )

    process.oneIsoEle = cms.EDFilter(
        "PATCandViewCountFilter",
        src=cms.InputTag("goodSignalElectrons"),
        minNumber=cms.uint32(1),
        maxNumber=cms.uint32(1),
    )
    process.noIsoMu = cms.EDFilter(
        "PATCandViewCountFilter",
        src=cms.InputTag("goodSignalMuons"),
        minNumber=cms.uint32(0),
        maxNumber=cms.uint32(0),
    )


    # Scale factors #
    process.electronWeightsProducer = cms.EDProducer("ElectronEfficiencyProducer",
        src = cms.InputTag("singleIsoEle")
    )

    #####################
    # MET/MtW cutting   #
    #####################
    process.goodMETsEle = cms.EDFilter("CandViewSelector",
      src=cms.InputTag(conf.metSource), cut=cms.string("pt>%f" % conf.Electrons.transverseMassCut)
    )
    process.eleAndMETMT = cms.EDProducer('CandTransverseMassProducer',
        collections=cms.untracked.vstring([conf.metSource, "goodSignalElectrons"])
    )

    process.metEleSequence = cms.Sequence(
        process.eleAndMETMT *
        process.goodMETsEle
    )
    #Either use MET cut or MtW cut
    if conf.Electrons.transverseMassType == conf.Leptons.WTransverseMassType.MET:
        if conf.Leptons.cutOnTransverseMass:
            process.hasMETEle = cms.EDFilter("PATCandViewCountFilter",
                src = cms.InputTag("goodMETsEle"),
                minNumber = cms.uint32(1),
                maxNumber = cms.uint32(1)
            )
    elif conf.Electrons.transverseMassType == conf.Leptons.WTransverseMassType.MtW:
        if conf.Leptons.cutOnTransverseMass:
            process.hasEleMETMT = cms.EDFilter('EventDoubleFilter',
                src=cms.InputTag("eleAndMETMT"),
                min=cms.double(conf.Electrons.transverseMassCut),
                max=cms.double(9999999)
            )

    process.recoNuProducerEle = cms.EDProducer('ClassicReconstructedNeutrinoProducer',
        leptonSrc=cms.InputTag("singleIsoEle"),
        bjetSrc=cms.InputTag("btaggedJets"),

        #either patMETs if cutting on ele + MET transverse mass or goodMETs if cutting on patMETs->goodMets pt
        metSrc=cms.InputTag(conf.metSource if conf.Electrons.transverseMassType == conf.Leptons.WTransverseMassType.MET else conf.metSource),
    )

    if conf.doDebug:
        process.electronAnalyzer = cms.EDAnalyzer('SimpleElectronAnalyzer', interestingCollections=cms.untracked.VInputTag("electronsWithIso"))
        process.electronVetoAnalyzer = cms.EDAnalyzer('SimpleElectronAnalyzer', interestingCollections=cms.untracked.VInputTag("looseVetoElectrons"))
        process.metAnalyzer = cms.EDAnalyzer('SimpleMETAnalyzer', interestingCollections=cms.untracked.VInputTag(conf.metSource))

def ElectronPath(process, conf):
    process.elePathPreCount = cms.EDProducer("EventCountProducer")

    process.efficiencyAnalyzerEle = cms.EDAnalyzer('EfficiencyAnalyzer'
    , histogrammableCounters = cms.untracked.vstring(["elePath"])
    , elePath = cms.untracked.vstring([
            "PATTotalEventsProcessedCount",
            "singleTopPathStep1ElePreCount",
            "singleTopPathStep1ElePostCount",
            "elePathPreCount",
        ]
    ))

    process.elePath = cms.Path(
        process.elePathPreCount *
        process.oneIsoEle *
        process.noIsoMu *
        process.jetSequence *
        process.nJets *
        process.metEleSequence *
        process.mBTags *
        process.topRecoSequenceEle
    )

    #Insert debugging modules for printout
    if conf.doDebug:

        process.elePath.insert(
            process.elePath.index(process.oneIsoEle),
            process.electronAnalyzer
        )
        process.elePath.insert(
            process.elePath.index(process.metEleSequence),
            process.metAnalyzer
        )

    if conf.isMC:
        process.elePath.insert(
            process.elePath.index(process.oneIsoEle)+1,
            process.electronWeightsProducer
            )

    #Produce the electron parentage decay tree string
    if conf.isMC and not conf.isSherpa:
        process.decayTreeProducerEle = cms.EDProducer(
            'GenParticleDecayTreeProducer<pat::Electron>',
            src=cms.untracked.InputTag("singleIsoEle")
        )
        process.elePath.insert(
            process.elePath.index(process.oneIsoEle)+1,
            process.decayTreeProducerEle
        )

    if conf.isMC and sample_types.is_signal(conf.subChannel):
        #Put the parton level study after the top reco sequence.
        process.elePath.insert(
            process.elePath.index(process.topRecoSequenceEle)+1,
            process.partonStudyCompareSequence
            )

    #eventCounting.countAfter(process, process.elePath,
    #    [
    #    ]
    #)
