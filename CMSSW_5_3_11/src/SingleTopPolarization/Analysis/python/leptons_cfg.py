import FWCore.ParameterSet.Config as cms

def LeptonSetup(process, conf):
    process.muonBeforeSelectionSequence = cms.Sequence()

    if conf.Muons.reverseIsoCut:
        logging.info("Using reversed isolation definition for muons, changing muon source from %s to 'muonsWithIDAll'")
        conf.Muons.source = "muonsWithIDAll"

    process.muonsWithIso = cms.EDProducer(
      'MuonIsolationProducer',
      leptonSrc = cms.InputTag(conf.Muons.source),
      rhoSrc = cms.InputTag("kt6PFJets", "rho"),
      dR = cms.double(0.4)
    )
    process.muonBeforeSelectionSequence += process.muonsWithIso

    if conf.Electrons.reverseIsoCut:
        logging.info("Using reversed isolation definition for electrons, changing electron source from %s to 'electronsWithIDAll'")
        conf.Electrons.source = "electronsWithIDAll"

    process.electronBeforeSelectionSequence = cms.Sequence()
    process.electronsWithIso = cms.EDProducer(
      'ElectronIsolationProducer',
      leptonSrc = cms.InputTag(conf.Electrons.source),
      rhoSrc = cms.InputTag("kt6PFJets", "rho"),
      dR = cms.double(0.3)
    )
    process.electronBeforeSelectionSequence += process.electronsWithIso
    process.electronsWithCorrectedEcalIso = cms.EDProducer(
        'CorrectedEcalIsoElectronProducer',
        src=cms.InputTag("electronsWithIso"),
        isMC=cms.bool(conf.isMC)
    )
    process.electronBeforeSelectionSequence += process.electronsWithCorrectedEcalIso

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
         sources=cms.untracked.vstring(["singleIsoMu", "singleIsoEle"]),
             maxOut=cms.untracked.uint32(1),
             minOut=cms.untracked.uint32(1)
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
