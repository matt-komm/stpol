import logging
logging.basicConfig(level=logging.INFO)
import FWCore.ParameterSet.Config as cms
import SingleTopPolarization.Analysis.eventCounting as eventCounting
from SingleTopPolarization.Analysis.config_step2_cfg import Config

from FWCore.ParameterSet.VarParsing import VarParsing
import SingleTopPolarization.Analysis.pileUpDistributions as pileUpDistributions
from SingleTopPolarization.Analysis.weights_cfg import WeightSetup
import SingleTopPolarization.Analysis.sample_types as sample_types

#FIXME
nanval = '-10000000000'

#utility function for creating a VPSet for CandViewNTupleProducer2
def ntupleCollection(items):
    varVPSet = cms.VPSet()
    for item in items:
        pset = cms.untracked.PSet(
            tag=cms.untracked.string(item[0]),
            quantity=cms.untracked.string(item[1])
        )
        varVPSet.append(pset)
    return varVPSet


def SingleTopStep2():

    options = VarParsing('analysis')
    options.register ('subChannel', 'T_t',
              VarParsing.multiplicity.singleton,
              VarParsing.varType.string,
              "The sample that you are running on")
    options.register ('reverseIsoCut', False,
              VarParsing.multiplicity.singleton,
              VarParsing.varType.bool,
              "Consider anti-isolated region")
    options.register ('doDebug', False,
              VarParsing.multiplicity.singleton,
              VarParsing.varType.bool,
              "Turn on debugging messages")
    options.register ('isMC', True,
              VarParsing.multiplicity.singleton,
              VarParsing.varType.bool,
              "Run on MC"
    )
    options.register ('doGenParticlePath', True,
              VarParsing.multiplicity.singleton,
              VarParsing.varType.bool,
              "Run the gen particle paths (only works on specific MC)"
    )
    options.register ('globalTag', Config.globalTagMC,
              VarParsing.multiplicity.singleton,
              VarParsing.varType.string,
              "Global tag"
    )
    options.register ('srcPUDistribution', "S10",
              VarParsing.multiplicity.singleton,
              VarParsing.varType.string,
              "Source pile-up distribution"
    )
    options.register ('destPUDistribution', "data",
              VarParsing.multiplicity.singleton,
              VarParsing.varType.string,
              "destination pile-up distribution"
    )

    options.register ('isComphep', False,
              VarParsing.multiplicity.singleton,
              VarParsing.varType.bool,
              "Use CompHep-specific processing")

    options.register ('isSherpa', False,
              VarParsing.multiplicity.singleton,
              VarParsing.varType.bool,
              "Use sherpa-specific processing")

    options.register ('systematic', "",
              VarParsing.multiplicity.singleton,
              VarParsing.varType.string,
              "Apply Systematic variation")

    options.register ('dataRun', "RunABCD",
              VarParsing.multiplicity.singleton,
              VarParsing.varType.string,
              "A string Run{A,B,C,D} to specify the data period")

    options.register(
             'doSync', False,
             VarParsing.multiplicity.singleton,
             VarParsing.varType.bool,
             "Synchronization exercise"
    )

    options.parseArguments()


    if options.isMC:
        Config.srcPUDistribution = pileUpDistributions.distributions[options.srcPUDistribution]

    Config.Leptons.reverseIsoCut = options.reverseIsoCut
    Config.subChannel = options.subChannel
    Config.doDebug = options.doDebug
    Config.isMC = options.isMC
    Config.doSkim = options.doSync or not sample_types.is_signal(Config.subChannel)
    Config.isCompHep = options.isComphep or "comphep" in Config.subChannel
    Config.isSherpa = options.isSherpa or "sherpa" in Config.subChannel
    Config.systematic = options.systematic
    Config.doSync = options.doSync

    print "Systematic: ",Config.systematic

    if Config.isMC and not Config.doSync:
        logging.info("Changing jet source from %s to smearedPatJetsWithOwnRef" % Config.Jets.source)
        Config.Jets.source = "smearedPatJetsWithOwnRef"

        if Config.systematic in ["ResUp", "ResDown"]:
             logging.info("Changing jet source from %s to smearedPatJetsWithOwnRef%s" % (Config.Jets.source, Config.systematic))
             Config.Jets.source = "smearedPatJetsWithOwnRef"+Config.systematic
             logging.info("Changing MET source from %s to patType1CorrectedPFMetJet%s" % (Config.metSource, Config.systematic))
             Config.metSource = "patType1CorrectedPFMetJet"+Config.systematic
        elif Config.systematic in ["EnUp", "EnDown"]:
             logging.info("Changing jet source from %s to shiftedPatJetsWithOwnRef%sForCorrMEt" % (Config.Jets.source, Config.systematic))
             Config.Jets.source = "shiftedPatJetsWithOwnRef"+Config.systematic+"ForCorrMEt"
             logging.info("Changing MET source from %s to patType1CorrectedPFMetJet%s" % (Config.metSource, Config.systematic))
             Config.metSource = "patType1CorrectedPFMetJet"+Config.systematic
        elif Config.systematic in ["UnclusteredEnUp", "UnclusteredEnDown"]:
             logging.info("Changing MET source from %s to patType1CorrectedPFMet%s" % (Config.metSource, Config.systematic))
             Config.metSource = "patType1CorrectedPFMet"+Config.systematic

    print "Configuration"
    print Config._toStr()

    print Config.Jets._toStr()
    print Config.Muons._toStr()
    print Config.Electrons._toStr()
    print ""

    process = cms.Process("STPOLSEL2")
    eventCounting.countProcessed(process)

    process.load("Configuration.Geometry.GeometryIdeal_cff")
    process.load("Configuration.StandardSequences.FrontierConditions_GlobalTag_cff")
    from Configuration.AlCa.autoCond import autoCond
    process.GlobalTag.globaltag = cms.string(options.globalTag)
    process.load("Configuration.StandardSequences.MagneticField_cff")

    if Config.doDebug:
        process.load("FWCore.MessageLogger.MessageLogger_cfi")
        process.MessageLogger = cms.Service("MessageLogger",
               destinations=cms.untracked.vstring('cout', 'debug'),
               debugModules=cms.untracked.vstring('*'),
               cout=cms.untracked.PSet(threshold=cms.untracked.string('INFO')),
               debug=cms.untracked.PSet(threshold=cms.untracked.string('DEBUG')),
        )
        logging.basicConfig(level=logging.DEBUG)
    else:
        process.load("FWCore.MessageLogger.MessageLogger_cfi")
        process.MessageLogger.cerr.FwkReport.reportEvery = 1000
        process.MessageLogger.cerr.threshold = cms.untracked.string("INFO")
        logging.basicConfig(level=logging.DEBUG)

    process.maxEvents = cms.untracked.PSet(input=cms.untracked.int32(options.maxEvents))

    process.options = cms.untracked.PSet(wantSummary=cms.untracked.bool(True))

    process.source = cms.Source("PoolSource",
        fileNames=cms.untracked.vstring(options.inputFiles),
        cacheSize = cms.untracked.uint32(50*1024*1024),
    )

    print options


    #-------------------------------------------------
    # Jets
    #-------------------------------------------------

    from SingleTopPolarization.Analysis.jets_step2_cfi import JetSetup
    JetSetup(process, Config)

    #-------------------------------------------------
    # Leptons
    #-------------------------------------------------


    from SingleTopPolarization.Analysis.muons_step2_cfi import MuonSetup
    MuonSetup(process, Config)

    from SingleTopPolarization.Analysis.electrons_step2_cfi import ElectronSetup
    ElectronSetup(process, Config)

    process.looseVetoMuCount = cms.EDProducer(
        "CollectionSizeProducer<reco::Candidate>",
        src = cms.InputTag("looseVetoMuons")
    )

    process.looseVetoEleCount = cms.EDProducer(
        "CollectionSizeProducer<reco::Candidate>",
        src = cms.InputTag("looseVetoElectrons")
    )

    process.decayTreeProducerMu = cms.EDProducer(
        'GenParticleDecayTreeProducer',
        src=cms.untracked.InputTag("singleIsoMu")
    )
    process.decayTreeProducerEle = cms.EDProducer(
        'GenParticleDecayTreeProducer',
        src=cms.untracked.InputTag("singleIsoEle")
    )

    #-----------------------------------------------
    # Top reco and cosine calcs
    #-----------------------------------------------

    from SingleTopPolarization.Analysis.top_step2_cfi import TopRecoSetup
    TopRecoSetup(process, Config)

    process.allEventObjects = cms.EDProducer(
         'CandRefCombiner',
         sources=cms.vstring(["goodJets", "goodSignalLeptons", Config.metSource]),
         maxOut=cms.uint32(9999),
         minOut=cms.uint32(0),
         logErrors=cms.bool(False)
    )

    process.hadronicEventObjects = cms.EDProducer(
         'CandRefCombiner',
         sources=cms.vstring(["goodJets"]),
         maxOut=cms.uint32(9999),
         minOut=cms.uint32(0),
         logErrors=cms.bool(False)
    )

    process.allEventObjectsWithNu = cms.EDProducer(
         'CandRefCombiner',
         sources=cms.vstring([
             "goodJets", "goodSignalLeptons",
             Config.metSource, "recoNuProducer"
         ]),
         maxOut=cms.uint32(9999),
         minOut=cms.uint32(0),
         logErrors=cms.bool(False)
    )

    process.eventShapeVars = cms.EDProducer(
        'EventShapeVarsProducer',
        src = cms.InputTag("allEventObjects")
    )

    process.eventShapeVarsWithNu = cms.EDProducer(
        'EventShapeVarsProducer',
        src = cms.InputTag("allEventObjectsWithNu")
    )

    #Vector sum of all reconstructed objects
    process.shat = cms.EDProducer('SimpleCompositeCandProducer',
        sources=cms.VInputTag(["allEventObjects"
        ])
    )

    #Hadronic final state
    process.ht = cms.EDProducer('SimpleCompositeCandProducer',
        sources=cms.VInputTag(["hadronicEventObjects"])
    )

    process.shatNTupleProducer = cms.EDProducer(
        "CandViewNtpProducer2",
        src = cms.InputTag("shat"),
        lazyParser = cms.untracked.bool(True),
        prefix = cms.untracked.string(""),
        #eventInfo = cms.untracked.bool(True),
        variables = ntupleCollection(
            [
                ["Pt", "pt"],
                ["Eta", "eta"],
                ["Phi", "phi"],
                ["Mass", "mass"],
            ]
      )
    )

    process.htNTupleProducer = process.shatNTupleProducer.clone(
        src = cms.InputTag("ht")
    )

    process.eventShapeSequence = cms.Sequence(
        process.allEventObjects
        * process.hadronicEventObjects
        * process.eventShapeVars
        * process.allEventObjectsWithNu
        * process.eventShapeVarsWithNu
        * process.shat
        * process.ht
        * process.shatNTupleProducer
        * process.htNTupleProducer
    )

    #-----------------------------------------------
    # Treemaking
    #-----------------------------------------------

    process.recoTopNTupleProducer = cms.EDProducer(
        "CandViewNtpProducer2",
        src = cms.InputTag("recoTop"),
        lazyParser = cms.untracked.bool(True),
        prefix = cms.untracked.string(""),
        #eventInfo = cms.untracked.bool(True),
        variables = ntupleCollection(
            [
                ["Pt", "pt"],
                ["Eta", "eta"],
                ["Phi", "phi"],
                ["Mass", "mass"],
            ]
      )
    )
    process.recoNuNTupleProducer = cms.EDProducer(
        "CandViewNtpProducer2",
        src = cms.InputTag("recoNu"),
        lazyParser = cms.untracked.bool(True),
        prefix = cms.untracked.string(""),
        #eventInfo = cms.untracked.bool(True),
        variables = ntupleCollection(
            [
                ["Pt", "pt"],
                ["Eta", "eta"],
                ["Phi", "phi"],
                ["Px", "p4().Px()"],
                ["Py", "p4().Py()"],
                ["Pz", "p4().Pz()"],
            ]
      )
    )

    process.recoWNTupleProducer = cms.EDProducer(
        "CandViewNtpProducer2",
        src = cms.InputTag("recoW"),
        lazyParser = cms.untracked.bool(True),
        prefix = cms.untracked.string(""),
        variables = ntupleCollection(
            [
                ["Pt", "pt"],
                ["Eta", "eta"],
                ["Phi", "phi"],
                ["Mass", "mass"],
            ]
      )
    )

    process.trueNuNTupleProducer = process.recoNuNTupleProducer.clone(
        src=cms.InputTag("genParticleSelector", "trueNeutrino", "STPOLSEL2"),
    )
    process.trueWNTupleProducer = process.recoTopNTupleProducer.clone(
        src=cms.InputTag("genParticleSelector", "trueWboson", "STPOLSEL2"),
    )
    process.trueTopNTupleProducer = process.recoTopNTupleProducer.clone(
        src=cms.InputTag("genParticleSelector", "trueTop", "STPOLSEL2"),
    )
    process.patMETNTupleProducer = cms.EDProducer(
        "CandViewNtpProducer2",
        src = cms.InputTag("goodMETs"),
        lazyParser = cms.untracked.bool(True),
        prefix = cms.untracked.string(""),
        variables = ntupleCollection(
            [
                ["Pt", "pt"],
                ["Eta", "eta"],
                ["Phi", "phi"],
                ["Px", "p4().Px()"],
                ["Py", "p4().Py()"],
                ["Pz", "p4().Pz()"],
            ]
      )
    )

    process.trueLeptonNTupleProducer = process.recoTopNTupleProducer.clone(
        src=cms.InputTag("genParticleSelector", "trueLepton", "STPOLSEL2"),
    )

    process.trueLightJetNTupleProducer = process.recoTopNTupleProducer.clone(
        src=cms.InputTag("genParticleSelector", "trueLightJet", "STPOLSEL2"),
    )

    def userfloat(key):
        return "? hasUserFloat('{0}') ? userFloat('{0}') : {1}".format(key, nanval)

    def userint(key):
        return "? hasUserInt('{0}') ? userInt('{0}') : {1}".format(key, nanval)

    process.goodSignalMuonsNTupleProducer = cms.EDProducer(
        "CandViewNtpProducer2",
        src = cms.InputTag("goodSignalMuons"),
        lazyParser = cms.untracked.bool(True),
        prefix = cms.untracked.string(""),
        #eventInfo = cms.untracked.bool(True),
        variables = ntupleCollection(
            [
                ["Pt", "pt"],
                ["Eta", "eta"],
                ["Phi", "phi"],
                ["relIso", userfloat(Config.Muons.relIsoType)],
                ["Charge", "charge"],
                ["genPdgId", "? genParticlesSize() > 0 ? genParticle(0).pdgId() : {0}".format(nanval)],
                ["motherGenPdgId", "? genParticlesSize() > 0 ? genParticle(0).mother(0).pdgId() : {0}".format(nanval)],
                ["normChi2", "? globalTrack().isNonnull() ? normChi2 : {0}".format(nanval)],
                ["trackhitPatterntrackerLayersWithMeasurement", userfloat("track_hitPattern_trackerLayersWithMeasurement")],
                ["globalTrackhitPatternnumberOfValidMuonHits", userfloat("globalTrack_hitPattern_numberOfValidMuonHits")],
                ["innerTrackhitPatternnumberOfValidPixelHits", userfloat("innerTrack_hitPattern_numberOfValidPixelHits")],
                ["db", "dB"],
                ["dz", userfloat("dz")],
                ["numberOfMatchedStations", "numberOfMatchedStations"],
                ["triggerMatch", "? triggerObjectMatchesByPath('{0}').size()==1 ? triggerObjectMatchByPath('{0}').hasPathLastFilterAccepted() : {1}".format(Config.Muons.triggerPath, nanval)],
            ]
      )
    )

    process.isoMuonsNTP = process.goodSignalMuonsNTupleProducer.clone(
        src=cms.InputTag("muonsWithIso")
    )

    process.allMuonsNTP = process.goodSignalMuonsNTupleProducer.clone(
        src=cms.InputTag("muonsWithIDAll")
    )

    process.goodSignalElectronsNTupleProducer = cms.EDProducer(
        "CandViewNtpProducer2",
        src = cms.InputTag("goodSignalElectrons"),
        lazyParser = cms.untracked.bool(True),
        prefix = cms.untracked.string(""),
        #eventInfo = cms.untracked.bool(True),
        variables = ntupleCollection(
                [
                    ["Pt", "%s" % Config.Electrons.pt],
                    ["Eta", "eta"],
                    ["Phi", "phi"],
                    ["relIso", userfloat(Config.Electrons.relIsoType)],
                    ["mvaID", "electronID('mvaTrigV0')"],
                    ["Charge", "charge"],
                    ["superClustereta", "superCluster.eta"],
                    ["passConversionVeto", "passConversionVeto()"],
                    ["gsfTracktrackerExpectedHitsInnernumberOfHits", userint('gsfTrack_trackerExpectedHitsInner_numberOfHits')],
                    ["triggerMatch", "? triggerObjectMatchesByPath('{0}').size()==1 ? triggerObjectMatchByPath('{0}').hasPathLastFilterAccepted() : {1}".format(Config.Electrons.triggerPath, nanval)],
                    ["genPdgId", "? genParticlesSize() > 0 ? genParticle(0).pdgId() : {0}".format(nanval)],
                    ["motherGenPdgId", "? genParticlesSize() > 0 ? genParticle(0).mother(0).pdgId() : {0}".format(nanval)],
                ]
      )
    )

    process.isoElectronsNTP = process.goodSignalElectronsNTupleProducer.clone(
        src=cms.InputTag("electronsWithIso")
    )

    process.allElectronsNTP = process.goodSignalElectronsNTupleProducer.clone(
        src=cms.InputTag("electronsWithIDAll")
    )

    process.goodJetsNTupleProducer = cms.EDProducer(
        "CandViewNtpProducer2",
        src = cms.InputTag("goodJets"),
        lazyParser = cms.untracked.bool(True),
        prefix = cms.untracked.string(""),
        eventInfo = cms.untracked.bool(False),
        variables = ntupleCollection(
                [
                    ["Pt", "pt"],
                    ["Eta", "eta"],
                    ["Phi", "phi"],
                    ["Mass", "mass"],
                    #["bDiscriminator", "bDiscriminator('%s')" % Config.Jets.bTagDiscriminant],
                    ["bDiscriminatorTCHP", "bDiscriminator('%s')" % Config.Jets.BTagDiscriminant.TCHP],
                    ["bDiscriminatorCSV", "bDiscriminator('%s')" % Config.Jets.BTagDiscriminant.CSV],
                    ["rms", userfloat('rms')],
                    ["partonFlavour", "partonFlavour()"],
                    ["area", "jetArea()"],

                    #These require PFCandidates to be present (huge collection)
                    #["n90", "n90()"],
                    #["n60", "n60()"],

                    #["genJetFlavour", "? genJet()>0 ? (genJet()->pdgId()) : 0"], #FIXME
                    ["deltaR", userfloat('deltaR')],

                    ["numberOfDaughters", "numberOfDaughters"],
                    ["neutralHadronEnergy", "neutralHadronEnergy"],
                    ["HFHadronEnergy", "HFHadronEnergy"],
                    ["chargedEmEnergyFraction", "chargedEmEnergyFraction"],
                    ["neutralEmEnergyFraction", "neutralEmEnergyFraction"],
                    ["chargedHadronEnergyFraction", "chargedHadronEnergyFraction"],
                    ["chargedMultiplicity", "chargedMultiplicity"],
                    ["nParticles", userfloat('nParticles')],
                    ["puMva", userfloat('mva')],
                    ["nCharged", userfloat('nCharged')],
                    ["nNeutral", userfloat('nNeutral')],
                ]
        )
    )
    process.lowestBTagJetNTupleProducer = process.goodJetsNTupleProducer.clone(src=cms.InputTag("lowestBTagJet"))
    process.highestBTagJetNTupleProducer = process.goodJetsNTupleProducer.clone(src=cms.InputTag("highestBTagJet"))

    process.treeSequenceNew = cms.Sequence(
        process.patMETNTupleProducer *
        process.recoTopNTupleProducer *
        process.recoNuNTupleProducer *
        process.recoWNTupleProducer *
        process.trueTopNTupleProducer *
        process.trueNuNTupleProducer *
        process.trueWNTupleProducer *
        process.trueLeptonNTupleProducer *
        process.trueLightJetNTupleProducer *
        process.goodJetsNTupleProducer *
        process.lowestBTagJetNTupleProducer *
        process.highestBTagJetNTupleProducer *
        process.goodSignalMuonsNTupleProducer *
        process.goodSignalElectronsNTupleProducer *
        process.isoMuonsNTP *
        process.isoElectronsNTP
    )
    #-----------------------------------------------
    # Flavour analyzer
    #-----------------------------------------------

    Config.doWJetsFlavour = Config.isMC and sample_types.is_wjets(Config.subChannel) and not Config.isSherpa
    if Config.doWJetsFlavour:
        process.flavourAnalyzer = cms.EDProducer('FlavourAnalyzer',
            genParticles = cms.InputTag('genParticles'),
            generator = cms.InputTag('generator'),
            genJets = cms.InputTag('selectedPatJets', 'genJets'),
            saveGenJets = cms.bool(False),
            savePDFInfo = cms.bool(True)
        )



    #-----------------------------------------------
    # Paths
    #-----------------------------------------------

    from SingleTopPolarization.Analysis.hlt_step2_cfi import HLTSetup
    HLTSetup(process, Config)

    from SingleTopPolarization.Analysis.leptons_cfg import LeptonSetup
    LeptonSetup(process, Config)

    if Config.isMC:
        WeightSetup(process, Config)


    if Config.isMC and options.doGenParticlePath:
        if Config.isCompHep:
            from SingleTopPolarization.Analysis.partonStudy_comphep_step2_cfi import PartonStudySetup
        else:
            from SingleTopPolarization.Analysis.partonStudy_step2_cfi import PartonStudySetup
        PartonStudySetup(process)
        process.partonPath = cms.Path()

        #NOTE: this path will REJECT events not having a true t-channel lepton
        if sample_types.is_signal(Config.subChannel):
            logging.warning("Using signal-only sequence 'process.partonStudyTrueSequence' on subChannel=%s" % Config.subChannel)
            process.partonPath += process.partonStudyTrueSequence

    from SingleTopPolarization.Analysis.muons_step2_cfi import MuonPath
    MuonPath(process, Config)

    from SingleTopPolarization.Analysis.electrons_step2_cfi import ElectronPath
    ElectronPath(process, Config)

    if Config.isMC:
        process.muPath += process.weightSequence
        process.elePath += process.weightSequence

    if Config.isMC and sample_types.is_signal(Config.subChannel):
        process.muPath += process.partonStudyCompareSequence
        process.elePath += process.partonStudyCompareSequence

    process.treePath = cms.Path(
        process.treeSequenceNew
    )

    process.eventVarsPath = cms.Path(
        process.eventShapeSequence
    )

    #enable embedding the gen-level weight, which is relevant for the Sherpa sample
    if Config.isMC:
        process.genWeightProducer = cms.EDProducer("GenWeightProducer")
        process.eventVarsPath += process.genWeightProducer

    if Config.doWJetsFlavour:
        process.treePath += process.flavourAnalyzer


    #-----------------------------------------------
    # Outpath
    #-----------------------------------------------
    process.out = cms.OutputModule("PoolOutputModule",
        dropMetaData=cms.untracked.string("DROPPED"),
        splitLevel=cms.untracked.int32(99),
        fileName=cms.untracked.string(options.outputFile),
         SelectEvents=cms.untracked.PSet(
             SelectEvents=cms.vstring(["*"])
         ),
        outputCommands=cms.untracked.vstring(
            'drop *',
            #'keep *',
            'keep edmMergeableCounter_*__*',
            'keep *_generator__*',
            #'keep *_genParticles__*', #hack for powheg PDF sets
            'keep edmTriggerResults_TriggerResults__*',
            'keep *_flavourAnalyzer_*_STPOLSEL2',
            'keep floats_*_*_STPOLSEL2',
            'keep double_*__STPOLSEL2',
            'keep float_*__STPOLSEL2',
            'keep double_*_*_STPOLSEL2',
            'keep float_*_*_STPOLSEL2',
            'keep int_*__STPOLSEL2',
            'keep int_*_*_STPOLSEL2',
            'keep int_*_*_*',
            'keep String_*_*_*', #the decay trees
            'keep *_pdfInfo1_*_STPOLSEL2',
            'keep *_pdfInfo2_*_STPOLSEL2',
            'keep *_pdfInfo3_*_STPOLSEL2',
            'keep *_pdfInfo4_*_STPOLSEL2',
            'keep *_pdfInfo5_*_STPOLSEL2',
            #'keep *',
            #'keep *_recoTop_*_*',
            #'keep *_goodSignalMuons_*_*',
            #'keep *_goodSignalElectrons_*_*',
            #'keep *_goodJets_*_*',
            #'keep *_bTaggedJets_*_*',
            #'keep *_untaggedJets_*_*',
        )
    )
    if Config.doDebug:
        process.out.outputCommands.append("keep *")
        process.debugpath = cms.Path(
            process.muAnalyzer * process.eleAnalyzer *
            process.jetAnalyzer * process.metAnalyzer
        )
    process.outpath = cms.EndPath(process.out)
    if Config.doSkim:
        process.out.SelectEvents.SelectEvents = []
    process.out.SelectEvents.SelectEvents.append("elePath")
    process.out.SelectEvents.SelectEvents.append("muPath")

    #-----------------------------------------------
    # Final printout
    #-----------------------------------------------

    if hasattr(process, "out"):
        print "Output patTuples: %s" % process.out.fileName.value()
    print 80*"-"
    print "Step2 configured"

    return process

import unittest
from subprocess import check_call
class TestStep2Conf(unittest.TestCase):
    def testSubChannelsTTJets(self):
        print "Testing TTJets samples"
        subch = [
            "TTbar", "TTJets", "TTJets_MassiveBinDECAY",
            "TTJets_mass166_5", "TTJets_mass178_5", "TTJets_matchingdown",
            "TTJets_matchingup", "TTJets_scaleup", "TTJets_scaledown"
        ]

        def conf(s):
            check_call(["python", __file__, "subChannel=" + s])

        for s in subch:
            conf(s)
        self.assertEquals(True)

if __name__=="__main__":
    process = SingleTopStep2()
    from SingleTopPolarization.Analysis.test_files import testfiles
    process.source.fileNames=cms.untracked.vstring(testfiles["step1"]["signal"])
    process.maxEvents.input=-1

    print str(process.source)
