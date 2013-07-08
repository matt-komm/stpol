import FWCore.ParameterSet.Config as cms
import SingleTopPolarization.Analysis.eventCounting as eventCounting
import SingleTopPolarization.Analysis.sample_types as sample_types

def MuonSetup(process, conf = None):

    goodMuonCut = 'isPFMuon'
    goodMuonCut += ' && isGlobalMuon'
    goodMuonCut += ' && pt > 26.'
    goodMuonCut += ' && abs(eta) < 2.1'
    goodMuonCut += ' && normChi2 < 10.'
    goodMuonCut += ' && userFloat("track_hitPattern_trackerLayersWithMeasurement") > 5'
    goodMuonCut += ' && userFloat("globalTrack_hitPattern_numberOfValidMuonHits") > 0'
    goodMuonCut += ' && abs(dB) < 0.2'
    goodMuonCut += ' && userFloat("innerTrack_hitPattern_numberOfValidPixelHits") > 0'
    goodMuonCut += ' && numberOfMatchedStations > 1'
    goodMuonCut += ' && abs(userFloat("dz")) < 0.5'
    goodSignalMuonCut = goodMuonCut

    if conf.Muons.cutOnIso:
        if conf.Muons.reverseIsoCut:
        #Choose anti-isolated region
            goodSignalMuonCut += ' && userFloat("{0}") >= {1} && userFloat("{0}") < {2}'.format(
                conf.Muons.relIsoType,
                conf.Muons.relIsoCutRangeAntiIsolatedRegion[0],
                conf.Muons.relIsoCutRangeAntiIsolatedRegion[1]
                )
        #Choose isolated region
        else:
            goodSignalMuonCut += " && (userFloat('{0}') >= {1}) && (userFloat('{0}') < {2})".format(
                conf.Muons.relIsoType,
                conf.Muons.relIsoCutRangeIsolatedRegion[0],
                conf.Muons.relIsoCutRangeIsolatedRegion[1]
            )
    print "goodSignalMuonCut = %s" % goodSignalMuonCut

    looseVetoMuonCut = "isPFMuon"
    looseVetoMuonCut += " && (isGlobalMuon | isTrackerMuon)"
    looseVetoMuonCut += " && pt > 10"
    looseVetoMuonCut += " && abs(eta)<2.5"
    looseVetoMuonCut += " && userFloat('{0}') < {1}".format(conf.Muons.relIsoType, conf.Muons.looseVetoRelIsoCut)
    looseVetoMuonCut += " && !(%s)" % goodSignalMuonCut #Remove 'good signal muons from the veto collection'

    #---------------Trigger matching-------------------------
    process.muonTriggerMatchHLTMuons = cms.EDProducer("PATTriggerMatcherDRLessByR" # matching in DeltaR, sorting by best DeltaR
                                                      # matcher input collections
                                                      , src     = cms.InputTag( 'muonsWithIso' )
                                                      , matched = cms.InputTag( 'patTrigger' )
                                                      # selections of trigger objects
                                                      , matchedCuts = cms.string( 'type( "TriggerMuon" ) && path( "HLT_IsoMu24_eta2p1_v*" )' )
                                                      # selection of matches
                                                      , maxDPtRel   = cms.double( 0.5 ) # no effect here
                                                      , maxDeltaR   = cms.double( 0.5 )
                                                      , maxDeltaEta = cms.double( 0.2 ) # no effect here
                                                      # definition of matcher output
                                                      , resolveAmbiguities    = cms.bool( True )
                                                      , resolveByMatchQuality = cms.bool( True )
                                                      )

    process.muonsWithIsoWithTriggerMatch = cms.EDProducer("PATTriggerMatchMuonEmbedder",
                                                         src     = cms.InputTag( "muonsWithIso" ),
                                                         matches = cms.VInputTag( "muonTriggerMatchHLTMuons" )
                                                         )
    #--------------------------------------------------------

    process.goodSignalMuons = cms.EDFilter("CandViewSelector",
      src=cms.InputTag("muonsWithIsoWithTriggerMatch"), cut=cms.string(goodSignalMuonCut)
    )

    process.looseVetoMuons = cms.EDFilter("CandViewSelector",
      src=cms.InputTag("muonsWithIso"), cut=cms.string(looseVetoMuonCut)
    )

    process.oneIsoMu = cms.EDFilter(
        "PATCandViewCountFilter",
        src=cms.InputTag("goodSignalMuons"),
        minNumber=cms.uint32(1),
        maxNumber=cms.uint32(1),
    )
    process.singleIsoMu = cms.EDFilter("CandViewSelector", src=cms.InputTag("goodSignalMuons"), cut=cms.string(""))

    process.muonCount = cms.EDProducer(
        "CollectionSizeProducer<reco::Candidate>",
        src = cms.InputTag("goodSignalMuons")
    )

    #####################
    # Loose lepton veto #
    #####################
    #In Muon path we must have 0 loose muons (good signal muons removed) or electrons
    process.looseMuVetoMu = cms.EDFilter(
        "PATCandViewCountFilter",
        src=cms.InputTag("looseVetoMuons"),
        minNumber=cms.uint32(0),
        maxNumber=cms.uint32(0)
    )
    process.looseEleVetoMu = cms.EDFilter(
        "PATCandViewCountFilter",
        src=cms.InputTag("looseVetoElectrons"),
        minNumber=cms.uint32(0),
        maxNumber=cms.uint32(0),
    )

    #produce the muon and MET invariant transverse mass
    process.muAndMETMT = cms.EDProducer('CandTransverseMassProducer',
        collections=cms.untracked.vstring([conf.metSource, "goodSignalMuons"])
    )
    process.goodMETs = cms.EDFilter("CandViewSelector",
      src=cms.InputTag(conf.metSource), cut=cms.string("pt>%f" % conf.Muons.transverseMassCut)
    )

    process.metMuSequence = cms.Sequence(
        process.muAndMETMT*
        process.goodMETs
    )

    process.muonWeightsProducer = cms.EDProducer("MuonEfficiencyProducer",
        src=cms.InputTag("singleIsoMu"),
        dataRun=cms.string(conf.dataRun)
    )

    process.recoNuProducerMu = cms.EDProducer('ClassicReconstructedNeutrinoProducer',
        leptonSrc=cms.InputTag("singleIsoMu"),
        bjetSrc=cms.InputTag("btaggedJets"),
        metSrc=cms.InputTag("goodMETs" if conf.Muons.transverseMassType == conf.Leptons.WTransverseMassType.MET else conf.metSource),
    )

def MuonPath(process, conf):

    process.muPathPreCount = cms.EDProducer("EventCountProducer")

    process.efficiencyAnalyzerMu = cms.EDAnalyzer('EfficiencyAnalyzer'
    , histogrammableCounters = cms.untracked.vstring(["muPath"])
    , muPath = cms.untracked.vstring([
        "PATTotalEventsProcessedCount",
        "singleTopPathStep1MuPreCount",
        "singleTopPathStep1MuPostCount",
        "muPathPreCount",
        ]
    ))

    process.muPath = cms.Path(

        process.muPathPreCount *

        process.muIsoSequence *
        process.eleIsoSequence *

        #Add triggerMatching
        process.muonTriggerMatchHLTMuons *
        process.muonsWithIsoWithTriggerMatch *
        
        #Select one isolated muon and veto additional loose muon/electron
        process.goodSignalMuons *
        process.muonCount *
        process.looseVetoMuons *
        process.looseVetoElectrons *
        process.oneIsoMu *
        process.singleIsoMu *

        #process.looseMuVetoMu *
        #process.looseEleVetoMu *

        #Do general jet cleaning, PU-jet cleaning and select 2 good jets
        process.jetSequence *
        process.nJets *

        #Select mu and MET invariant transverse mass OR the MET
        process.metMuSequence *

        process.mBTags *

        #Reconstruct the neutrino, the top quark and calculate the cosTheta* variable
        process.topRecoSequenceMu
#        process.efficiencyAnalyzerMu
    )

    #Only do the parton identification in the signal channel
    if conf.isMC and sample_types.is_signal(conf.subChannel):
        process.muPath.insert(
            process.muPath.index(process.topRecoSequenceMu)+1,
            process.partonStudyCompareSequence
        )
    if conf.doDebug:
        process.goodSignalMuAnalyzer = cms.EDAnalyzer("SimpleMuonAnalyzer", interestingCollections=cms.untracked.VInputTag("muonsWithIso", "goodSignalMuons", "looseVetoMuons"))
        process.vetoEleAnalyzer = cms.EDAnalyzer("SimpleElectronAnalyzer", interestingCollections=cms.untracked.VInputTag("looseVetoElectrons"))
        process.muPrintOutSequence = cms.Sequence(process.goodSignalMuAnalyzer*process.vetoEleAnalyzer)
        process.muPath.insert(
            process.muPath.index(process.oneIsoMu),
            process.muPrintOutSequence
        )
        process.oneIsoMuID = cms.EDAnalyzer("EventIDAnalyzer", name=cms.untracked.string("oneIsoMuID"))
        process.muPath.insert(
            process.muPath.index(process.oneIsoMu)+1,
            process.oneIsoMuID
        )
        process.nJetID = cms.EDAnalyzer("EventIDAnalyzer", name=cms.untracked.string("nJetID"))
        process.muPath.insert(
            process.muPath.index(process.nJets)+1,
            process.nJetID
        )

    if conf.isMC:
      #Add muon scale factors
      process.muPath.insert(
            process.muPath.index(process.singleIsoMu)+1,
            process.muonWeightsProducer
        )

    if conf.isMC and not conf.isSherpa:
        process.decayTreeProducerMu = cms.EDProducer(
            'GenParticleDecayTreeProducer<pat::Muon>',
            src=cms.untracked.InputTag("singleIsoMu")
        )
        process.muPath.insert(
            process.muPath.index(process.singleIsoMu)+1,
            process.decayTreeProducerMu
        )


    #Count number of events passing the selection filters
    #eventCounting.countAfter(process, process.muPath,
    #    [
    #    ]
    #)