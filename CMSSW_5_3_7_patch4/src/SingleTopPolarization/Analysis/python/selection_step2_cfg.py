import logging
logging.basicConfig(level=logging.INFO)
import FWCore.ParameterSet.Config as cms
import SingleTopPolarization.Analysis.eventCounting as eventCounting
from SingleTopPolarization.Analysis.config_step2_cfg import Config

from FWCore.ParameterSet.VarParsing import VarParsing
import SingleTopPolarization.Analysis.pileUpDistributions as pileUpDistributions

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
        options.register ('channel', 'signal',
                  VarParsing.multiplicity.singleton,
                  VarParsing.varType.string,
                  "Signal or Background")
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

        options.register ('systematic', "",
                  VarParsing.multiplicity.singleton,
                  VarParsing.varType.string,
                  "Apply Systematic variation")

        options.register ('doPDFWeights', True,
                  VarParsing.multiplicity.singleton,
                  VarParsing.varType.bool,
                  "Run the PDF weight generation module")

        options.register ('dataRun', "RunABCD",
                  VarParsing.multiplicity.singleton,
                  VarParsing.varType.string,
                  "A string Run{A,B,C,D} to specify the data period")

        options.parseArguments()


        if options.isMC:
            if options.channel.lower() == "signal":
                Config.channel = Config.Channel.signal
            elif options.channel.lower() == "background":
                Config.channel = Config.Channel.background
            Config.srcPUDistribution = pileUpDistributions.distributions[options.srcPUDistribution]
            Config.destPUDistribution = pileUpDistributions.distributions[options.destPUDistribution]
        else:
            Config.channel = "data"
            Config.subChannel = None


        Config.Leptons.reverseIsoCut = options.reverseIsoCut
        Config.subChannel = options.subChannel
        Config.doDebug = options.doDebug
        Config.isMC = options.isMC
        Config.isCompHep = options.compHep
        Config.systematic = options.systematic
        Config.dataRun = options.dataRun
        print "Systematic! ",Config.systematic

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

    process.maxEvents = cms.untracked.PSet(input=cms.untracked.int32(-1))

    process.options = cms.untracked.PSet(wantSummary=cms.untracked.bool(True))

    process.source = cms.Source("PoolSource",
        # replace 'myfile.root' with the source file you want to use
        fileNames=cms.untracked.vstring(""),
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

    #Embed the corrected isolations to the leptons
    #process.muonClones = cms.EDProducer("MuonShallowCloneProducer",
    #    src = cms.InputTag(Config.Muons.source)
    #)
    process.skimmedMuons = cms.EDFilter("PtMinCandViewCloneSelector",
      src=cms.InputTag(Config.Muons.source), ptMin=cms.double(20)
    )
    process.muonsWithIso = cms.EDProducer(
      'MuonIsolationProducer',
      leptonSrc = cms.InputTag("skimmedMuons"),
      rhoSrc = cms.InputTag("kt6PFJets", "rho"),
      dR = cms.double(0.4)
    )
    process.muIsoSequence = cms.Sequence(process.skimmedMuons*process.muonsWithIso)

    process.skimmedElectrons = cms.EDFilter("PtMinCandViewCloneSelector",
      src=cms.InputTag(Config.Electrons.source), ptMin=cms.double(20)
    )
    process.elesWithIso = cms.EDProducer(
      'ElectronIsolationProducer',
      leptonSrc = cms.InputTag("skimmedElectrons"),
      rhoSrc = cms.InputTag("kt6PFJets", "rho"),
      dR = cms.double(0.3)
    )
    process.eleIsoSequence = cms.Sequence(process.skimmedElectrons*process.elesWithIso)

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


    #Combine the found electron/muon to a single collection
    process.goodSignalLeptons = cms.EDProducer(
         'CandRefCombiner',
         sources=cms.untracked.vstring(["singleIsoMu", "singleIsoEle"]),
             maxOut=cms.untracked.uint32(1),
             minOut=cms.untracked.uint32(1)
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

    #Following treemakers for reference only, not to be used. Use CandViewNtpProducer2 instead! --joosep
    #process.treesMu = cms.EDAnalyzer('MuonCandViewTreemakerAnalyzer',
    #    collections = cms.untracked.VPSet(
    #        treeCollection(
    #            cms.untracked.InputTag("muonsWithIso"), 1,
    #            [
    #                ["Pt", "pt"],
    #                ["Eta", "eta"],
    #                ["Phi", "phi"],
    #                ["relIso", "userFloat('%s')" % Config.Muons.relIsoType],
    #                ["Charge", "charge"],
    #                ["genPdgId", "? genParticlesSize() > 0 ? genParticle(0).pdgId() : 0"],
    #                ["normChi2", "? globalTrack().isNonnull() ? normChi2 : -1.0"],
    #                ["track_hitPattern_trackerLayersWithMeasurement", "userFloat('track_hitPattern_trackerLayersWithMeasurement')"],
    #                ["globalTrack_hitPattern_numberOfValidMuonHits", "userFloat('globalTrack_hitPattern_numberOfValidMuonHits')"],
    #                ["innerTrack_hitPattern_numberOfValidPixelHits", "userFloat('innerTrack_hitPattern_numberOfValidPixelHits')"],
    #                ["db", "dB"],
    #                ["dz", "userFloat('dz')"],
    #                ["numberOfMatchedStations", "numberOfMatchedStations"],
    #            ]
    #        ),
    #        treeCollection(
    #            cms.untracked.InputTag("goodSignalMuons"), 1,
    #            [
    #                ["Pt", "pt"],
    #                ["Eta", "eta"],
    #                ["Phi", "phi"],
    #                ["relIso", "userFloat('%s')" % Config.Muons.relIsoType],
    #                ["Charge", "charge"],
    #                ["genPdgId", "? genParticlesSize() > 0 ? genParticle(0).pdgId() : 0"],
    #            ]
    #        ),
    #        treeCollection(
    #            cms.untracked.InputTag("looseVetoMuons"), 1,
    #            [
    #                ["Pt", "pt"],
    #                ["Eta", "eta"],
    #                ["Phi", "phi"],
    #                ["relIso", "userFloat('%s')" % Config.Muons.relIsoType],
    #                ["Charge", "charge"],
    #                ["genPdgId", "? genParticlesSize() > 0 ? genParticle(0).pdgId() : 0"],
    #            ]
    #        )
    #    )
    #)

    #process.treesEle = cms.EDAnalyzer('ElectronCandViewTreemakerAnalyzer',
    #    collections = cms.untracked.VPSet(
    #        treeCollection(
    #            cms.untracked.InputTag("elesWithIso"), 1,
    #            [
    #                ["Pt", "%s" % Config.Electrons.pt],
    #                ["Eta", "eta"],
    #                ["Phi", "phi"],
    #                ["relIso", "userFloat('%s')" % Config.Electrons.relIsoType],
    #                ["mvaID", "electronID('mvaTrigV0')"],
    #                ["Charge", "charge"],
    #                ["superCluster_eta", "superCluster.eta"],
    #                ["passConversionVeto", "passConversionVeto()"],
    #                ["superCluster_eta", "superCluster.eta"],
    #                ["gsfTrack_trackerExpectedHitsInner_numberOfHits", "userInt('gsfTrack_trackerExpectedHitsInner_numberOfHits')"]
    #            ]
    #        ),
    #        treeCollection(
    #            cms.untracked.InputTag("goodSignalElectrons"), 1,
    #            [
    #                ["Pt", "%s" % Config.Electrons.pt],
    #                ["Eta", "eta"],
    #                ["Phi", "phi"],
    #                ["relIso", "userFloat('%s')" % Config.Electrons.relIsoType],
    #                ["mvaID", "electronID('mvaTrigV0')"],
    #                ["Charge", "charge"],
    #            ]
    #        ),
    #        treeCollection(
    #            cms.untracked.InputTag("looseVetoElectrons"), 1,
    #            [
    #                ["Pt", "pt"],
    #                ["Eta", "eta"],
    #                ["Phi", "phi"],
    #                ["relIso", "userFloat('%s')" % Config.Electrons.relIsoType],
    #                ["Charge", "charge"],
    #                ["genPdgId", "? genParticlesSize() > 0 ? genParticle(0).pdgId() : 0"],
    #            ]
    #        )
    #    )
    #)
    #process.treesJets = cms.EDAnalyzer('JetCandViewTreemakerAnalyzer',
    #        collections = cms.untracked.VPSet(
    #        #all the selected jets in events, passing the reference selection cuts, ordered pt-descending
    #        treeCollection(
    #            cms.untracked.InputTag("goodJets"), 5,
    #            [
    #                ["Pt", "pt"],
    #                ["Eta", "eta"],
    #                ["Phi", "phi"],
    #                ["Mass", "mass"],
    #                ["bDiscriminator", "bDiscriminator('%s')" % Config.Jets.bTagDiscriminant],
    #                ["bDiscriminatorTCHP", "bDiscriminator('%s')" % Config.Jets.BTagDiscriminant.TCHP],
    #                ["bDiscriminatorCSV_MVA", "bDiscriminator('%s')" % Config.Jets.BTagDiscriminant.CSV_MVA],
    #                ["rms", "userFloat('rms')"],
    #                ["partonFlavour", "partonFlavour()"],
    #                ["deltaR", "userFloat('deltaR')"]
    #            ]
    #        ),
    #        # treeCollection(
    #        #     cms.untracked.InputTag("fwdMostLightJet"), 1,
    #        #     [
    #        #         ["Pt", "pt"],
    #        #         ["Eta", "eta"],
    #        #         ["Phi", "phi"],
    #        #         ["Mass", "mass"],
    #        #         ["bDiscriminator", "bDiscriminator('combinedSecondaryVertexBJetTags')"],
    #        #         ["rms", "userFloat('rms')"]
    #        #     ]
    #        # ),

    #        #the tagged jet with the highest b-discriminator value (== THE b-jet)
    #        treeCollection(
    #            cms.untracked.InputTag("highestBTagJet"), 1,
    #            [
    #                ["Pt", "pt"],
    #                ["Eta", "eta"],
    #                ["Phi", "phi"],
    #                ["Mass", "mass"],
    #                ["bDiscriminator", "bDiscriminator('%s')" % Config.Jets.bTagDiscriminant],
    #                ["bDiscriminatorTCHP", "bDiscriminator('%s')" % Config.Jets.BTagDiscriminant.TCHP],
    #                ["bDiscriminatorCSV_MVA", "bDiscriminator('%s')" % Config.Jets.BTagDiscriminant.CSV_MVA],
    #                ["rms", "userFloat('rms')"],
    #                ["partonFlavour", "partonFlavour()"],
    #                ["deltaR", "userFloat('deltaR')"]
    #            ]
    #        ),

    #        #The jet with the lowest b-discriminator value (== THE light jet)
    #        treeCollection(
    #            cms.untracked.InputTag("lowestBTagJet"), 1,
    #            [
    #                ["Pt", "pt"],
    #                ["Eta", "eta"],
    #                ["Phi", "phi"],
    #                ["Mass", "mass"],
    #                ["bDiscriminator", "bDiscriminator('%s')" % Config.Jets.bTagDiscriminant],
    #                ["bDiscriminatorTCHP", "bDiscriminator('%s')" % Config.Jets.BTagDiscriminant.TCHP],
    #                ["bDiscriminatorCSV_MVA", "bDiscriminator('%s')" % Config.Jets.BTagDiscriminant.CSV_MVA],
    #                ["rms", "userFloat('rms')"],
    #                ["partonFlavour", "partonFlavour()"],
    #                ["deltaR", "userFloat('deltaR')"]
    #            ]
    #        ),

    #    #all the b-tagged jets in the event, ordered pt-descending
    #        treeCollection(
    #            cms.untracked.InputTag("btaggedJets"), Config.Jets.nBTags,
    #            [
    #                ["Pt", "pt"],
    #                ["Eta", "eta"],
    #                ["Phi", "phi"],
    #                ["Mass", "mass"],
    #                ["bDiscriminator", "bDiscriminator('%s')" % Config.Jets.bTagDiscriminant],
    #                ["bDiscriminatorTCHP", "bDiscriminator('%s')" % Config.Jets.BTagDiscriminant.TCHP],
    #                ["bDiscriminatorCSV_MVA", "bDiscriminator('%s')" % Config.Jets.BTagDiscriminant.CSV_MVA],
    #                ["rms", "userFloat('rms')"],
    #                ["partonFlavour", "partonFlavour()"],
    #                ["deltaR", "userFloat('deltaR')"]
    #            ]
    #        ),
    #        treeCollection(
    #            cms.untracked.InputTag("untaggedJets"), Config.Jets.nJets-Config.Jets.nBTags,
    #            [
    #                ["Pt", "pt"],
    #                ["Eta", "eta"],
    #                ["Phi", "phi"],
    #                ["Mass", "mass"],
    #                ["bDiscriminator", "bDiscriminator('%s')" % Config.Jets.bTagDiscriminant],
    #                ["bDiscriminatorTCHP", "bDiscriminator('%s')" % Config.Jets.BTagDiscriminant.TCHP],
    #                ["bDiscriminatorCSV_MVA", "bDiscriminator('%s')" % Config.Jets.BTagDiscriminant.CSV_MVA],
    #                ["rms", "userFloat('rms')"],
    #                ["partonFlavour", "partonFlavour()"],
    #                ["deltaR", "userFloat('deltaR')"]
    #            ]
    #        )
    #    )
    #)



    ##process.treesEle = cms.EDAnalyzer('ElectronCandViewTreemakerAnalyzer',
    ##        collections = cms.untracked.VPSet(treeCollection("goodSignalElectrons", 1,
    ##            [
    ##                ["Pt", "pt"],
    ##                ["Eta", "eta"],
    ##                ["Phi", "phi"],
    ##                ["rhoCorrRelIso", "userFloat('rhoCorrRelIso')"],
    ##            ]
    ##            )
    ##        )
    ##)

    #process.treesCands = cms.EDAnalyzer('CandViewTreemakerAnalyzer',
    #        collections = cms.untracked.VPSet(
    #        treeCollection(
    #            cms.untracked.InputTag("recoTop"), 1,
    #            [
    #                ["Pt", "pt"],
    #                ["Eta", "eta"],
    #                ["Phi", "phi"],
    #                ["Mass", "mass"],
    #            ]
    #        ),
    #        treeCollection(
    #            cms.untracked.InputTag("recoNu"), 1,
    #            [
    #                ["Pt", "pt"],
    #                ["Eta", "eta"],
    #                ["Phi", "phi"],
    #                ["Px", "p4().Px()"],
    #                ["Py", "p4().Py()"],
    #                ["Pz", "p4().Pz()"],
    #            ]
    #        ),
    #        treeCollection(
    #            cms.untracked.InputTag("genParticleSelector", "trueTop", "STPOLSEL2"), 1,
    #            [
    #                ["Pt", "pt"],
    #                ["Eta", "eta"],
    #                ["Phi", "phi"],
    #                ["Mass", "mass"],
    #            ]
    #        ),
    #        treeCollection(
    #            cms.untracked.InputTag("genParticleSelector", "trueNeutrino", "STPOLSEL2"), 1,
    #            [
    #                ["Pt", "pt"],
    #                ["Eta", "eta"],
    #                ["Phi", "phi"],
    #                ["Px", "p4().Px()"],
    #                ["Py", "p4().Py()"],
    #                ["Pz", "p4().Pz()"],
    #            ]
    #        ),
    #        treeCollection(
    #            cms.untracked.InputTag("genParticleSelector", "trueLepton", "STPOLSEL2"), 1,
    #            [
    #                ["Pt", "pt"],
    #                ["Eta", "eta"],
    #                ["Phi", "phi"],
    #            ]
    #        ),
    #        treeCollection(
    #            cms.untracked.InputTag("genParticleSelector", "trueLightJet", "STPOLSEL2"), 1,
    #            [
    #                ["Pt", "pt"],
    #                ["Eta", "eta"],
    #                ["Phi", "phi"],
    #            ]
    #        ),
    #        treeCollection(
    #            cms.untracked.InputTag("patMETs"), 1,
    #            [
    #                ["Pt", "pt"],
    #            ]
    #        ),
    #    )
    #)

    #process.treesDouble = cms.EDAnalyzer("FloatTreemakerAnalyzer",
    #    collections = cms.VInputTag(
    #        #Merged cosTheta*
    #        cms.InputTag("cosTheta", "cosThetaLightJet"),

    #        #cosTheta* separately from mu and ele
    #        #cms.InputTag("cosThetaProducerEle", "cosThetaLightJet"),
    #        #cms.InputTag("cosThetaProducerMu", "cosThetaLightJet"),

    #        #cosTheta* from gen
    #        cms.InputTag("cosThetaProducerTrueTop", "cosThetaLightJet"),
    #        cms.InputTag("cosThetaProducerTrueLepton", "cosThetaLightJet"),
    #        cms.InputTag("cosThetaProducerTrueJet", "cosThetaLightJet"),
    #        cms.InputTag("cosThetaProducerTrueAll", "cosThetaLightJet"),

    #        cms.InputTag("puWeightProducer", "nVerticesTrue"),

    #        #Transverse mass of MET and lepton
    #        cms.InputTag("muAndMETMT", ""),
    #        cms.InputTag("eleAndMETMT", ""),

    #        ##B-tag systematics
    #        #cms.InputTag("bTagWeightProducer", "bTagWeight"),
    #        #cms.InputTag("bTagWeightProducer", "bTagWeightSystBCUp"),
    #        #cms.InputTag("bTagWeightProducer", "bTagWeightSystBCDown"),
    #        #cms.InputTag("bTagWeightProducer", "bTagWeightSystLUp"),
    #        #cms.InputTag("bTagWeightProducer", "bTagWeightSystLDown"),


    #        #Some debugging data
    #        #cms.InputTag("kt6PFJets", "rho", "RECO"),
    #        #cms.InputTag("recoNu", "Delta"),
    #    )
    #)

    #process.treesDoubleWeight = cms.EDAnalyzer("FloatTreemakerAnalyzer",
    #    defaultValue = cms.untracked.double(0),
    #    putNaNs = cms.untracked.bool(False),
    #    collections = cms.VInputTag(
    #        #B-tag systematics
    #        cms.InputTag("bTagWeightProducerNJMT", "bTagWeight"),
    #        cms.InputTag("bTagWeightProducerNJMT", "bTagWeightSystBCUp"),
    #        cms.InputTag("bTagWeightProducerNJMT", "bTagWeightSystBCDown"),
    #        cms.InputTag("bTagWeightProducerNJMT", "bTagWeightSystLUp"),
    #        cms.InputTag("bTagWeightProducerNJMT", "bTagWeightSystLDown"),

    #        #cms.InputTag("bTagWeightProducer2J1T", "bTagWeight"),
    #        #cms.InputTag("bTagWeightProducer2J1T", "bTagWeightSystBCUp"),
    #        #cms.InputTag("bTagWeightProducer2J1T", "bTagWeightSystBCDown"),
    #        #cms.InputTag("bTagWeightProducer2J1T", "bTagWeightSystLUp"),
    #        #cms.InputTag("bTagWeightProducer2J1T", "bTagWeightSystLDown"),

    #        #cms.InputTag("bTagWeightProducer2J0T", "bTagWeight"),
    #        #cms.InputTag("bTagWeightProducer2J0T", "bTagWeightSystBCUp"),
    #        #cms.InputTag("bTagWeightProducer2J0T", "bTagWeightSystBCDown"),
    #        #cms.InputTag("bTagWeightProducer2J0T", "bTagWeightSystLUp"),
    #        #cms.InputTag("bTagWeightProducer2J0T", "bTagWeightSystLDown"),

    #        #cms.InputTag("bTagWeightProducer3J0T", "bTagWeight"),
    #        #cms.InputTag("bTagWeightProducer3J0T", "bTagWeightSystBCUp"),
    #        #cms.InputTag("bTagWeightProducer3J0T", "bTagWeightSystBCDown"),
    #        #cms.InputTag("bTagWeightProducer3J0T", "bTagWeightSystLUp"),
    #        #cms.InputTag("bTagWeightProducer3J0T", "bTagWeightSystLDown"),

    #        #cms.InputTag("bTagWeightProducer3J1T", "bTagWeight"),
    #        #cms.InputTag("bTagWeightProducer3J1T", "bTagWeightSystBCUp"),
    #        #cms.InputTag("bTagWeightProducer3J1T", "bTagWeightSystBCDown"),
    #        #cms.InputTag("bTagWeightProducer3J1T", "bTagWeightSystLUp"),
    #        #cms.InputTag("bTagWeightProducer3J1T", "bTagWeightSystLDown"),

    #        #cms.InputTag("puWeightProducer", "PUWeightN0"),
    #        cms.InputTag("puWeightProducer", "PUWeightNtrue"),

    #        cms.InputTag("muonWeightsProducer", "muonIDWeight"),
    #        cms.InputTag("muonWeightsProducer", "muonIDWeightUp"),
    #        cms.InputTag("muonWeightsProducer", "muonIDWeightDown"),
    #        cms.InputTag("muonWeightsProducer", "muonIsoWeight"),
    #        cms.InputTag("muonWeightsProducer", "muonIsoWeightUp"),
    #        cms.InputTag("muonWeightsProducer", "muonIsoWeightDown")
    #    )
    #)

    #process.treesBool = cms.EDAnalyzer("BoolTreemakerAnalyzer",
    #    collections = cms.VInputTag(
    #        cms.InputTag("ecalLaserCorrFilter", "", "PAT"),
    #    )
    #)

    #process.treesInt = cms.EDAnalyzer("IntTreemakerAnalyzer",
    #    collections = cms.VInputTag(
    #        [
    #        #cms.InputTag("recoNuProducerMu", "solType"),
    #        #cms.InputTag("recoNuProducerEle ", "solType"),
    #        cms.InputTag("muonCount"),
    #        cms.InputTag("electronCount"),
    #        cms.InputTag("topCount"),
    #        cms.InputTag("bJetCount"),
    #        cms.InputTag("lightJetCount"),

    #        cms.InputTag("looseVetoMuCount"),
    #        cms.InputTag("looseVetoEleCount"),

    #        cms.InputTag("btaggedTrueBJetCount"),
    #        cms.InputTag("trueBJetCount"),
    #        cms.InputTag("btaggedTrueCJetCount"),
    #        cms.InputTag("trueCJetCount"),
    #        cms.InputTag("btaggedTrueLJetCount"),
    #        cms.InputTag("trueLJetCount"),

    #        cms.InputTag("eventIDProducer", "eventId"),
    #        cms.InputTag("eventIDProducer", "runId"),
    #        cms.InputTag("eventIDProducer", "lumiId"),

    #        cms.InputTag("offlinePVCount"),

    #        cms.InputTag("genLeptonsTCount"),
    #        cms.InputTag("trueLeptonPdgId")
    #        ]
    #    )
    #)

    #process.treeSequence = cms.Sequence(process.treesMu*process.treesEle*process.treesDouble*process.treesBool*process.treesCands*process.treesJets*process.treesInt*process.treesDoubleWeight)

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

    if Config.isMC and Config.subChannel=="WJets":
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

    if Config.isMC and options.doPDFWeights:
        process.PDFweights = cms.EDProducer('PDFweightsProducer')
        process.pdfPath = cms.Path(
              process.PDFweights
        )


    if Config.doDebug:
        from SingleTopPolarization.Analysis.debugAnalyzers_step2_cfi import DebugAnalyzerSetup
        DebugAnalyzerSetup(process)

    process.looseVetoMuCount = cms.EDProducer(
        "CollectionSizeProducer<reco::Candidate>",
        src = cms.InputTag("looseVetoMuons")
    )

    process.looseVetoElectronCount = cms.EDProducer(
        "CollectionSizeProducer<reco::Candidate>",
        src = cms.InputTag("looseVetoElectrons")
    )

    if Config.isMC and options.doGenParticlePath:
        if Config.isCompHep:
            from SingleTopPolarization.Analysis.partonStudy_comphep_step2_cfi import PartonStudySetup
        else:
            from SingleTopPolarization.Analysis.partonStudy_step2_cfi import PartonStudySetup
        PartonStudySetup(process)
        process.partonPath = cms.Path()
        #process.partonPath = cms.Path(process.commonPartonSequence)
        if Config.channel==Config.Channel.signal:
            process.partonPath += process.partonStudyTrueSequence

    if Config.doMuon:
        from SingleTopPolarization.Analysis.muons_step2_cfi import MuonPath
        MuonPath(process, Config)
        process.muPath.insert(process.muPath.index(process.singleIsoMu)+1, process.goodSignalLeptons)
        process.muPath.insert(process.muPath.index(process.looseVetoMuons)+1, process.looseVetoMuCount)
        process.muPath.insert(process.muPath.index(process.looseVetoElectrons)+1, process.looseVetoEleCount)

    if Config.doElectron:
        from SingleTopPolarization.Analysis.electrons_step2_cfi import ElectronPath
        ElectronPath(process, Config)
        process.elePath.insert(process.elePath.index(process.singleIsoEle)+1, process.goodSignalLeptons)
        process.elePath.insert(process.elePath.index(process.looseVetoMuons)+1, process.looseVetoMuCount)
        process.elePath.insert(process.elePath.index(process.looseVetoElectrons)+1, process.looseVetoEleCount)

    if Config.isMC:
        process.puWeightProducer = cms.EDProducer('PUWeightProducer'
            , maxVertices = cms.uint32(50)
            , srcDistribution = cms.vdouble(Config.srcPUDistribution)
            , destDistribution = cms.vdouble(Config.destPUDistribution)
        )
        if Config.doMuon:
             process.muPath.insert(0, process.puWeightProducer)
        if Config.doElectron:
             process.elePath.insert(0, process.puWeightProducer)


#    process.offlinePVCount = cms.EDProducer(
#        "CollectionSizeProducer<reco::Vertex>",
#        src = cms.InputTag("offlinePrimaryVertices")
#    )

    process.eventIDProducer = cms.EDProducer('EventIDProducer'
    )
    process.treePath = cms.Path(
        process.eventIDProducer *
        #process.offlinePVCount *
       # process.treeSequence *
        process.treeSequenceNew
    )

    if Config.isMC and Config.subChannel=="WJets":
        process.treePath += process.flavourAnalyzer


    #-----------------------------------------------
    # Outpath
    #-----------------------------------------------
    if not Config.skipPatTupleOutput:
        process.out = cms.OutputModule("PoolOutputModule",
            dropMetaData=cms.untracked.string("DROPPED"),
            splitLevel=cms.untracked.int32(99),
            fileName=cms.untracked.string('out_step2.root'),
             SelectEvents=cms.untracked.PSet(
                 SelectEvents=cms.vstring(["*"])
             ),
            outputCommands=cms.untracked.vstring(
                #'drop *',
                'drop *',
                'keep edmMergeableCounter_*__*',
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
        process.outpath = cms.EndPath(process.out)
        if Config.doElectron:
            process.out.SelectEvents.SelectEvents.append("elePath")
        if Config.doMuon:
            process.out.SelectEvents.SelectEvents.append("muPath")

    #-----------------------------------------------
    #
    #-----------------------------------------------

    #Command-line arguments
    if not Config.onGrid:
        process.source.fileNames = cms.untracked.vstring(options.inputFiles)
        process.maxEvents = cms.untracked.PSet(
          input = cms.untracked.int32(options.maxEvents)
        )
        if hasattr(process, "out"):
            process.out.fileName = cms.untracked.string(options.outputFile)
        outFile = options.outputFile
        #from SingleTopPolarization.Analysis.cmdlineParsing import enableCommandLineArguments
        #(inFiles, outFile) = enableCommandLineArguments(process)
    else:
        outFile = "step2.root"

    #process.TFileService = cms.Service(
    #    "TFileService",
    #    fileName=cms.string(outFile.replace(".root", "_trees.root")),
    #)

    #print "Output trees: %s" % process.TFileService.fileName.value()
    if hasattr(process, "out"):
        print "Output patTuples: %s" % process.out.fileName.value()
    print 80*"-"
    print "Step2 configured"

    return process
