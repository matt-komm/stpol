import FWCore.ParameterSet.Config as cms
import logging

logger = logging.getLogger("Leptons")
def LeptonSetup(process, conf):
    process.muonBeforeSelectionSequence = cms.Sequence()

    if conf.Muons.reverseIsoCut:
        logger.info("Using reversed isolation definition for muons, changing muon source from %s to 'muonsWithIDAll'")
        conf.Muons.source = "muonsWithIDAll"

    process.muonsWithIso = cms.EDProducer(
      'MuonIsolationProducer',
      leptonSrc = cms.InputTag(conf.Muons.source),
      rhoSrc = cms.InputTag("kt6PFJets", "rho"),
      dR = cms.double(0.4)
    )
    process.muonBeforeSelectionSequence += process.muonsWithIso

    if conf.Electrons.reverseIsoCut:
        logger.info("Using reversed isolation definition for electrons, changing electron source from %s to 'electronsWithIDAll'")
        conf.Electrons.source = "electronsWithIDAll"

    process.electronBeforeSelectionSequence = cms.Sequence()
    process.electronsWithIso = cms.EDProducer(
      'ElectronIsolationProducer',
      leptonSrc = cms.InputTag(conf.Electrons.source),
      rhoSrc = cms.InputTag("kt6PFJets", "rho"),
      dR = cms.double(0.3)
    )

    process.electronBeforeSelectionSequence += process.electronsWithIso

    process.electronsWithLooseID = cms.EDProducer(
        'ElectronLooseIDProducer',
        src = cms.InputTag("electronsWithIso")
        )
    process.electronBeforeSelectionSequence += process.electronsWithLooseID

    process.electronsWithCorrectedEcalIso = cms.EDProducer(
        'CorrectedEcalIsoElectronProducer',
        src=cms.InputTag("electronsWithLooseID"),
        isMC=cms.bool(conf.isMC)
    )
    process.electronBeforeSelectionSequence += process.electronsWithCorrectedEcalIso

    #---------------Trigger matching-------------------------
    process.electronTriggerMatchHLTElectrons = cms.EDProducer("PATTriggerMatcherDRLessByR" # matching in DeltaR, sorting by best DeltaR
                                                          # matcher input collections
                                                          , src     = cms.InputTag( 'electronsWithCorrectedEcalIso' )
                                                          , matched = cms.InputTag( 'patTrigger' )
                                                          # selections of trigger objects
                                                          , matchedCuts = cms.string('type("TriggerElectron") && path("%s" )' % conf.Electrons.triggerPath)
                                                          # selection of matches
                                                          , maxDPtRel   = cms.double( 0.5 ) # no effect here
                                                          , maxDeltaR   = cms.double( 0.5 )
                                                          , maxDeltaEta = cms.double( 0.2 ) # no effect here
                                                          # definition of matcher output
                                                          , resolveAmbiguities    = cms.bool( True )
                                                          , resolveByMatchQuality = cms.bool( True )
                                                          )

    process.electronsWithTriggerMatch = cms.EDProducer("PATTriggerMatchElectronEmbedder",
                                                          src     = cms.InputTag( "electronsWithCorrectedEcalIso" ),
                                                          matches = cms.VInputTag( "electronTriggerMatchHLTElectrons" )
                                                          )
    process.electronBeforeSelectionSequence += process.electronTriggerMatchHLTElectrons*process.electronsWithTriggerMatch

    process.muonTriggerMatchHLTMuons = cms.EDProducer("PATTriggerMatcherDRLessByR" # matching in DeltaR, sorting by best DeltaR
                                                      # matcher input collections
                                                      , src     = cms.InputTag( 'muonsWithIso' )
                                                      , matched = cms.InputTag( 'patTrigger' )
                                                      # selections of trigger objects
                                                      , matchedCuts = cms.string('type("TriggerMuon") && path("%s")' % conf.Muons.triggerPath)
                                                      # selection of matches
                                                      , maxDPtRel   = cms.double( 0.5 ) # no effect here
                                                      , maxDeltaR   = cms.double( 0.5 )
                                                      , maxDeltaEta = cms.double( 0.2 ) # no effect here
                                                      # definition of matcher output
                                                      , resolveAmbiguities    = cms.bool( True )
                                                      , resolveByMatchQuality = cms.bool( True )
                                                      )

    process.muonsWithTriggerMatch = cms.EDProducer("PATTriggerMatchMuonEmbedder",
                                                         src     = cms.InputTag("muonsWithIso"),
                                                         matches = cms.VInputTag( "muonTriggerMatchHLTMuons" )
                                                         )
    process.muonBeforeSelectionSequence += process.muonTriggerMatchHLTMuons * process.muonsWithTriggerMatch
    #-------------------------------------------------------

    process.looseVetoMuCount = cms.EDProducer(
        "CollectionSizeProducer<reco::Candidate>",
        src = cms.InputTag("looseVetoMuons")
    )

    process.looseVetoElectronCount = cms.EDProducer(
        "CollectionSizeProducer<reco::Candidate>",
        src = cms.InputTag("looseVetoElectrons")
    )

    process.muonCount = cms.EDProducer(
        "CollectionSizeProducer<reco::Candidate>",
        src = cms.InputTag("goodSignalMuons")
    )

    process.electronCount = cms.EDProducer(
        "CollectionSizeProducer<reco::Candidate>",
        src = cms.InputTag("goodSignalElectrons")
    )

    #Make a new named collection that contains the ONLY isolated(or anti-isolated) electron(muon)
    process.singleIsoEle = cms.EDFilter("CandViewSelector", src=cms.InputTag("goodSignalElectrons"), cut=cms.string(""))
    process.singleIsoMu = cms.EDFilter("CandViewSelector", src=cms.InputTag("goodSignalMuons"), cut=cms.string(""))

    #Combine the found electron/muon to a single collection
    process.goodSignalLeptons = cms.EDProducer(
         'CandRefCombiner',
         sources=cms.vstring(["singleIsoMu", "singleIsoEle"]),
         maxOut=cms.uint32(1),
         minOut=cms.uint32(1),
         logErrors=cms.bool(False)
    )

    process.leptonPath = cms.Path(
        process.muonBeforeSelectionSequence *
        process.electronBeforeSelectionSequence *
        process.goodSignalMuons *
        process.muonCount *
        process.goodSignalElectrons *
        process.electronCount *
        process.singleIsoEle *
        process.singleIsoMu *
        process.goodSignalLeptons *
        process.looseVetoMuons *
        process.looseVetoElectrons *
        process.looseVetoMuCount *
        process.looseVetoEleCount
    )
