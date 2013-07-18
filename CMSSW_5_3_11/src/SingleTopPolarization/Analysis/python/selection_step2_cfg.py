import logging
logging.basicConfig(level=logging.INFO)
import FWCore.ParameterSet.Config as cms
import SingleTopPolarization.Analysis.eventCounting as eventCounting
from SingleTopPolarization.Analysis.config_step2_cfg import Config

from FWCore.ParameterSet.VarParsing import VarParsing
import SingleTopPolarization.Analysis.pileUpDistributions as pileUpDistributions
from SingleTopPolarization.Analysis.weights_cfg import WeightSetup
import SingleTopPolarization.Analysis.sample_types as sample_types


#BTag working points from https://twiki.cern.ch/twiki/bin/viewauth/CMS/BTagPerformanceOP#B_tagging_Operating_Points_for_5
#TODO: place in proper class
#TrackCountingHighPur     TCHPT   3.41
#JetProbability   JPL     0.275
#JetProbability   JPM     0.545
#JetProbability   JPT     0.790
#CombinedSecondaryVertex  CSVL    0.244
#CombinedSecondaryVertex  CSVM    0.679
#CombinedSecondaryVertex  CSVT    0.898

#BTag tagger names
#trackCountingHighPurBJetTags
#combinedSecondaryVertexMVABJetTags

def SingleTopStep2():

    if not Config.onGrid:
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

        options.register ('compHep', False,
                  VarParsing.multiplicity.singleton,
                  VarParsing.varType.bool,
                  "Use CompHep-specific processing")

        options.register ('sherpa', False,
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
        options.register ('doSync', False,
            VarParsing.multiplicity.singleton,
            VarParsing.varType.bool,
            "Are you performing the sync exercise?"
        )

        options.parseArguments()


        if options.isMC:
            Config.srcPUDistribution = pileUpDistributions.distributions[options.srcPUDistribution]
            Config.destPUDistribution = pileUpDistributions.distributions[options.destPUDistribution]


        Config.Leptons.reverseIsoCut = options.reverseIsoCut
        Config.subChannel = options.subChannel
        Config.doDebug = options.doDebug
        Config.isMC = options.isMC
        Config.isCompHep = options.compHep
        Config.isSherpa = options.sherpa
        Config.systematic = options.systematic
        Config.dataRun = options.dataRun
        Config.doSync = options.doSync

        Config.Jets.doPUClean = Config.Jets.doPUClean and not Config.doSync
        Config.doDebug = Config.doDebug or Config.doSync

        print "Systematic: ",Config.systematic

    if Config.isMC:
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
        # replace 'myfile.root' with the source file you want to use
        fileNames=cms.untracked.vstring(options.inputFiles),
        cacheSize = cms.untracked.uint32(10*1024*1024),
    )


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
    TopRecoSetup(process)

    process.allEventObjects = cms.EDProducer(
         'CandRefCombiner',
         sources=cms.vstring(["goodJets", "goodSignalLeptons", Config.metSource]),
         maxOut=cms.uint32(9999),
         minOut=cms.uint32(0),
         logErrors=cms.bool(False)
    )
    process.eventShapeVars = cms.EDProducer(
        'EventShapeVarsProducer',
        src = cms.InputTag("allEventObjects")
    )
    process.eventShapeSequence = cms.Sequence(
        process.allEventObjects *
        process.eventShapeVars
    )

    #-----------------------------------------------
    # Treemaking
    #-----------------------------------------------


    def treeCollection(collection_, maxElems_, varlist):
        varVPSet = cms.untracked.VPSet()
        for v in varlist:
            pset = cms.untracked.PSet(tag=cms.untracked.string(v[0]), expr=cms.untracked.string(v[1]), )
            varVPSet.append(pset)
        ret = cms.untracked.PSet(
            collection=collection_,
            maxElems=cms.untracked.int32(maxElems_),
            variables=varVPSet
        )
        return ret

    def ntupleCollection(items):
        varVPSet = cms.VPSet()
        for item in items:
            pset = cms.untracked.PSet(
                tag=cms.untracked.string(item[0]),
                quantity=cms.untracked.string(item[1])
            )
            varVPSet.append(pset)
        return varVPSet

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

    process.trueNuNTupleProducer = process.recoNuNTupleProducer.clone(
        src=cms.InputTag("genParticleSelector", "trueNeutrino", "STPOLSEL2"),
    )
    if Config.isCompHep:
        process.trueTopNTupleProducer = process.recoTopNTupleProducer.clone(
            src=cms.InputTag("recoTrueTop"),
        )
    else:
        process.trueTopNTupleProducer = process.recoTopNTupleProducer.clone(
            src=cms.InputTag("genParticleSelector", "trueTop", "STPOLSEL2"),
        )
    process.patMETNTupleProducer = process.recoTopNTupleProducer.clone(
        src=cms.InputTag(Config.metSource),
    )
    process.trueLeptonNTupleProducer = process.recoTopNTupleProducer.clone(
        src=cms.InputTag("genParticleSelector", "trueLepton", "STPOLSEL2"),
    )

    process.trueLightJetNTupleProducer = process.recoTopNTupleProducer.clone(
        src=cms.InputTag("genParticleSelector", "trueLightJet", "STPOLSEL2"),
    )
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
                ["relIso", "userFloat('%s')" % Config.Muons.relIsoType],
                ["Charge", "charge"],
                ["genPdgId", "? genParticlesSize() > 0 ? genParticle(0).pdgId() : 0"],
                ["motherGenPdgId", "? genParticlesSize() > 0 ? genParticle(0).mother(0).pdgId() : 0"],
                ["normChi2", "? globalTrack().isNonnull() ? normChi2 : -1.0"],
                ["trackhitPatterntrackerLayersWithMeasurement", "userFloat('track_hitPattern_trackerLayersWithMeasurement')"],
                ["globalTrackhitPatternnumberOfValidMuonHits", "userFloat('globalTrack_hitPattern_numberOfValidMuonHits')"],
                ["innerTrackhitPatternnumberOfValidPixelHits", "userFloat('innerTrack_hitPattern_numberOfValidPixelHits')"],
                ["db", "dB"],
                ["dz", "userFloat('dz')"],
                ["numberOfMatchedStations", "numberOfMatchedStations"],
                ["triggerMatch", "? triggerObjectMatchesByPath('{0}').size()==1 ? triggerObjectMatchByPath('{0}').hasPathLastFilterAccepted() : 0.0".format(Config.Muons.triggerPath)],
            ]
      )
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
                    ["relIso", "userFloat('%s')" % Config.Electrons.relIsoType],
                    ["mvaID", "electronID('mvaTrigV0')"],
                    ["Charge", "charge"],
                    ["superClustereta", "superCluster.eta"],
                    ["passConversionVeto", "passConversionVeto()"],
                    ["gsfTracktrackerExpectedHitsInnernumberOfHits", "userInt('gsfTrack_trackerExpectedHitsInner_numberOfHits')"],
                    ["triggerMatch", "? triggerObjectMatchesByPath('{0}').size()==1 ? triggerObjectMatchByPath('{0}').hasPathLastFilterAccepted() : 0.0".format(Config.Electrons.triggerPath)],
                    ["genPdgId", "? genParticlesSize() > 0 ? genParticle(0).pdgId() : 0"],
                    ["motherGenPdgId", "? genParticlesSize() > 0 ? genParticle(0).mother(0).pdgId() : 0"],
                ]
      )
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
                    #["bDiscriminatorCSV_MVA", "bDiscriminator('%s')" % Config.Jets.BTagDiscriminant.CSV_MVA],
                    ["rms", "userFloat('rms')"],
                    ["partonFlavour", "partonFlavour()"],
                    ["area", "jetArea()"],

                    #These require PFCandidates to be present (huge collection)
                    #["n90", "n90()"],
                    #["n60", "n60()"],

                    #["genJetFlavour", "? genJet()>0 ? (genJet()->pdgId()) : 0"], #FIXME
                    ["deltaR", "userFloat('deltaR')"],

                    ["numberOfDaughters", "numberOfDaughters"],
                    ["neutralHadronEnergy", "neutralHadronEnergy"],
                    ["HFHadronEnergy", "HFHadronEnergy"],
                    ["chargedEmEnergyFraction", "chargedEmEnergyFraction"],
                    ["neutralEmEnergyFraction", "neutralEmEnergyFraction"],
                    ["chargedHadronEnergyFraction", "chargedHadronEnergyFraction"],
                    ["chargedMultiplicity", "chargedMultiplicity"],
                    ["nParticles", "userFloat('nParticles')"],
                    ["puMva", "userFloat('mva')"],
                    ["nCharged", "userFloat('nCharged')"],
                    ["nNeutral", "userFloat('nNeutral')"],
                ]
        )
    )
    process.lowestBTagJetNTupleProducer = process.goodJetsNTupleProducer.clone(src=cms.InputTag("lowestBTagJet"))
    process.highestBTagJetNTupleProducer = process.goodJetsNTupleProducer.clone(src=cms.InputTag("highestBTagJet"))

    process.treeSequenceNew = cms.Sequence(
        process.patMETNTupleProducer *
        process.recoTopNTupleProducer *
        process.recoNuNTupleProducer *
        process.trueTopNTupleProducer *
        process.trueNuNTupleProducer *
        process.trueLeptonNTupleProducer *
        process.trueLightJetNTupleProducer *
        process.goodJetsNTupleProducer *
        process.lowestBTagJetNTupleProducer *
        process.highestBTagJetNTupleProducer *
        process.goodSignalMuonsNTupleProducer *
        process.goodSignalElectronsNTupleProducer
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

    from SingleTopPolarization.Analysis.leptons_cfg import LeptonSetup
    LeptonSetup(process, Config)

    if Config.doDebug:
        from SingleTopPolarization.Analysis.debugAnalyzers_step2_cfi import DebugAnalyzerSetup
        DebugAnalyzerSetup(process)

    if Config.isMC and options.doGenParticlePath:
        if Config.isCompHep:
            from SingleTopPolarization.Analysis.partonStudy_comphep_step2_cfi import PartonStudySetup
        else:
            from SingleTopPolarization.Analysis.partonStudy_step2_cfi import PartonStudySetup
        PartonStudySetup(process)
        process.partonPath = cms.Path()
        if sample_types.is_signal(Config.subChannel):
            process.partonPath += process.partonStudyTrueSequence

    if Config.isMC:
        WeightSetup(process, Config)

    from SingleTopPolarization.Analysis.muons_step2_cfi import MuonPath
    MuonPath(process, Config)

    from SingleTopPolarization.Analysis.electrons_step2_cfi import ElectronPath
    ElectronPath(process, Config)
    if Config.isMC:
        process.muPath += process.weightSequence
        process.elePath += process.weightSequence

    #process.eventIDProducer = cms.EDProducer('EventIDProducer'
    #)
    process.treePath = cms.Path(
        process.treeSequenceNew
    )

    process.eventVarsPath = cms.Path(
        process.eventShapeSequence
    )
    if Config.doWJetsFlavour:
        process.treePath += process.flavourAnalyzer


    #-----------------------------------------------
    # Outpath
    #-----------------------------------------------
    if not Config.skipPatTupleOutput:
        process.out = cms.OutputModule("PoolOutputModule",
            dropMetaData=cms.untracked.string("DROPPED"),
            splitLevel=cms.untracked.int32(99),
            fileName=cms.untracked.string(options.outputFile),
             SelectEvents=cms.untracked.PSet(
                 SelectEvents=cms.vstring(["*"])
             ),
            outputCommands=cms.untracked.vstring(
                'drop *',
                'keep edmMergeableCounter_*__*',
                'keep *_generator__*',
                'keep edmTriggerResults_TriggerResults__*',
                'keep *_flavourAnalyzer_*_STPOLSEL2',
                'keep floats_patMETNTupleProducer_*_STPOLSEL2',
                'keep floats_recoTopNTupleProducer_*_STPOLSEL2',
                'keep floats_recoNuNTupleProducer_*_STPOLSEL2',
                'keep floats_trueTopNTupleProducer_*_STPOLSEL2',
                'keep floats_trueNuNTupleProducer_*_STPOLSEL2',
                'keep floats_trueLeptonNTupleProducer_*_STPOLSEL2',
                'keep floats_goodSignalMuonsNTupleProducer_*_STPOLSEL2',
                'keep floats_goodSignalElectronsNTupleProducer_*_STPOLSEL2',
                'keep floats_goodJetsNTupleProducer_*_STPOLSEL2',
                'keep floats_lowestBTagJetNTupleProducer_*_STPOLSEL2',
                'keep floats_highestBTagJetNTupleProducer_*_STPOLSEL2',
                'keep double_*__STPOLSEL2',
                'keep float_*__STPOLSEL2',
                'keep double_*_*_STPOLSEL2',
                'keep float_*_*_STPOLSEL2',
                'keep double_cosTheta_*_STPOLSEL2',
                'keep double_cosThetaProducerTrueAll_*_STPOLSEL2',
                'keep double_cosThetaProducerTrueTop_*_STPOLSEL2',
                'keep double_cosThetaProducerTrueLepton_*_STPOLSEL2',
                'keep double_cosThetaProducerTrueJet_*_STPOLSEL2',
                'keep *_bTagWeightProducerNJMT_*_STPOLSEL2',
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
        process.outpath = cms.EndPath(process.out)
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
