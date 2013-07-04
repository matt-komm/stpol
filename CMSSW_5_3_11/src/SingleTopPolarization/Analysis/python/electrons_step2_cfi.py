import FWCore.ParameterSet.Config as cms
import SingleTopPolarization.Analysis.eventCounting as eventCounting

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
    #goodElectronCut += "&& (0.0 < electronID('mvaTrigV0') < 1.0)"
    goodSignalElectronCut = goodElectronCut
    if conf.Electrons.cutWWlnuj:
        if conf.Electrons.reverseIsoCut:
            goodSignalElectronCut += ' && userFloat("{0}") >= {1} && userFloat("{0}") < {2}'.format(
                conf.Electrons.relIsoType,
                conf.Electrons.relIsoCutRangeAntiIsolatedRegion[0],
                conf.Electrons.relIsoCutRangeAntiIsolatedRegion[1]
                )
        else:
            goodSignalElectronCut += """
            && ( (abs(eta) < 0.8 && electronID('mvaTrigV0') > 0.913 && userFloat('{0}') < 0.105) ||
            ( abs(eta) > 0.8 && abs(eta) < 1.479 && electronID('mvaTrigV0') > 0.964 && userFloat('{0}') < 0.178 ) ||
            ( abs(eta) > 1.479 && electronID('mvaTrigV0') > 0.899 && userFloat('{0}') < 0.150 ) )""".format(conf.Electrons.relIsoType)

    if conf.Electrons.cutOnMVA:
        if conf.Electrons.reverseIsoCut:
            goodSignalElectronCut += " && (electronID('mvaTrigV0') > 0.0) && (electronID('mvaTrigV0') < %f)" % conf.Electrons.mvaCutAntiIso
        else:
            goodSignalElectronCut += " && (electronID('mvaTrigV0') > %f)" % conf.Electrons.mvaCut


    goodSignalElectronCut += " && abs(userFloat('dxy')) < 0.02"
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


    looseVetoElectronCut = "%s > 20.0" % conf.Electrons.pt
    looseVetoElectronCut += " && (abs(eta) < 2.5)"
    looseVetoElectronCut += " && (electronID('mvaTrigV0') > %f)" % 0.1
    looseVetoElectronCut += " && (userFloat('{0}') < {1})".format(conf.Electrons.relIsoType, conf.Electrons.looseVetoRelIsoCut)

    #Loose veto electrons must not overlap with good signal electrons
    looseVetoElectronCut += " && !(%s)" % goodSignalElectronCut

    print "goodSignalElectronCut={0}".format(goodSignalElectronCut)
    print "looseVetoElectronCut={0}".format(looseVetoElectronCut)

    process.goodSignalElectrons = cms.EDFilter("CandViewSelector",
      src=cms.InputTag("elesWithIso"), cut=cms.string(goodSignalElectronCut)
    )

    process.looseVetoElectrons = cms.EDFilter("CandViewSelector",
      src=cms.InputTag("elesWithIso"), cut=cms.string(looseVetoElectronCut)
    )

    process.oneIsoEle = cms.EDFilter(
        "PATCandViewCountFilter",
        src=cms.InputTag("goodSignalElectrons"),
        minNumber=cms.uint32(1),
        maxNumber=cms.uint32(1),
    )

    #Make a new named collection that contains the ONLY isolated(or anti-isolated) electron
    process.singleIsoEle = cms.EDFilter("CandViewSelector", src=cms.InputTag("goodSignalElectrons"), cut=cms.string(""))

    process.electronCount = cms.EDProducer(
        "CollectionSizeProducer<reco::Candidate>",
        src = cms.InputTag("goodSignalElectrons")
    )

    #If loose veto electrons don't have any overlap with signal electrons, there must be none
    process.looseEleVetoEle = cms.EDFilter(
        "PATCandViewCountFilter",
        src=cms.InputTag("looseVetoElectrons"),
        minNumber=cms.uint32(0),
        maxNumber=cms.uint32(0),
    )
    process.looseMuVetoEle = cms.EDFilter(
        "PATCandViewCountFilter",
        src=cms.InputTag("looseVetoMuons"),
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
        process.oneIsoEleIDs = cms.EDAnalyzer('EventIDAnalyzer', name=cms.untracked.string("IDoneIsoEle"))
        process.eleVetoIDs = cms.EDAnalyzer('EventIDAnalyzer', name=cms.untracked.string("IDeleVeto"))
        process.metIDS = cms.EDAnalyzer('EventIDAnalyzer', name=cms.untracked.string("MET"))
        process.NJetIDs = cms.EDAnalyzer('EventIDAnalyzer', name=cms.untracked.string("NJet"))
        process.electronAnalyzer = cms.EDAnalyzer('SimpleElectronAnalyzer', interestingCollections=cms.untracked.VInputTag("elesWithIso"))
        process.electronVetoAnalyzer = cms.EDAnalyzer('SimpleElectronAnalyzer', interestingCollections=cms.untracked.VInputTag("looseVetoElectrons"))
        process.metAnalyzer = cms.EDAnalyzer('SimpleMETAnalyzer', interestingCollections=cms.untracked.VInputTag(conf.metSource))

"""
Configures the electron path with full selection.
channel:    'sig' - runs on signal (t-channel or tbar channel). Generator level comparisons are turned on.
            'bkg' - runs on background (anything else). Generator level comparisons turned off.
"""
def ElectronPath(process, conf):
    process.elePathPreCount = cms.EDProducer("EventCountProducer")

    process.efficiencyAnalyzerEle = cms.EDAnalyzer('EfficiencyAnalyzer'
    , histogrammableCounters = cms.untracked.vstring(["elePath"])
    , elePath = cms.untracked.vstring([
        "PATTotalEventsProcessedCount",
        "singleTopPathStep1ElePreCount",
        "singleTopPathStep1ElePostCount",
        "elePathPreCount",
        "elePathStepHLTsyncElePostCount",
        "elePathOneIsoElePostCount",
        "elePathLooseEleVetoElePostCount",
        "elePathLooseMuVetoElePostCount",
        "elePathNJetsPostCount",
        "elePathMetEleSequencePostCount",
        "elePathMBTagsPostCount"
        ]
    ))

    process.elePath = cms.Path(

        process.elePathPreCount *

        process.stepHLTsyncEle *

        process.muIsoSequence *
        process.eleIsoSequence *

        process.goodSignalElectrons *
        process.electronCount *
        process.looseVetoElectrons *
        process.oneIsoEle *
        process.singleIsoEle *

        process.looseEleVetoEle *
        process.looseVetoMuons *
        process.looseMuVetoEle *

        process.jetSequence *
        process.nJets *

        process.metEleSequence *
        process.goodSignalLeptons *

        process.mBTags *

        process.topRecoSequenceEle
#        process.efficiencyAnalyzerEle
    )

    #Insert debugging modules for printout
    if conf.doDebug:
        process.elePath.insert(
            process.elePath.index(process.oneIsoEle)+1,
            process.oneIsoEleIDs
        )
        process.elePath.insert(
            process.elePath.index(process.oneIsoEle),
            process.electronAnalyzer
        )
        process.elePath.insert(
            process.elePath.index(process.looseEleVetoEle),
            process.electronVetoAnalyzer
        )
        process.elePath.insert(
            process.elePath.index(process.looseEleVetoEle)+1,
            process.eleVetoIDs
        )
        process.elePath.insert(
            process.elePath.index(process.metEleSequence)+1,
            process.metIDS
        )
        process.elePath.insert(
            process.elePath.index(process.nJets)+1,
            process.NJetIDs
        )
        process.elePath.insert(
            process.elePath.index(process.metEleSequence),
            process.metAnalyzer
        )

    if conf.isMC:
        process.elePath.insert(
            process.elePath.index(process.singleIsoEle)+1,
            process.electronWeightsProducer
            )

    #Produce the electron parentage decay tree string
    if conf.isMC and not conf.isSherpa:
        process.decayTreeProducerEle = cms.EDProducer(
            'GenParticleDecayTreeProducer<pat::Electron>',
            src=cms.untracked.InputTag("singleIsoEle")
        )
        process.elePath.insert(
            process.elePath.index(process.singleIsoEle)+1,
            process.decayTreeProducerEle
        )

    if conf.isMC and conf.channel == conf.Channel.signal:
        #Put the parton level study after the top reco sequence.
        process.elePath.insert(
            process.elePath.index(process.topRecoSequenceEle)+1,
            process.partonStudyCompareSequence
            )

    eventCounting.countAfter(process, process.elePath,
        [
        "stepHLTsyncEle",
        "oneIsoEle",
        "looseEleVetoEle",
        "looseMuVetoEle",
        "metEleSequence",
        "nJets",
        "mBTags"
        ]
    )
