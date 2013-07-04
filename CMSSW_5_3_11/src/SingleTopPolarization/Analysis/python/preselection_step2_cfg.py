import logging
logging.basicConfig(level=logging.INFO)
import FWCore.ParameterSet.Config as cms
import SingleTopPolarization.Analysis.eventCounting as eventCounting
from SingleTopPolarization.Analysis.config_step2_cfg import Config

from FWCore.ParameterSet.VarParsing import VarParsing
import SingleTopPolarization.Analysis.pileUpDistributions as pileUpDistributions
import sys

def SingleTopStep2Preselection():
    Config.doMuon = False
    Config.doElectron = False
    #Whether to filter the HLT
    Config.filterHLT = False

    #Whether to use the cross-strigger or the single lepton trigger
    Config.useXTrigger = False

    #Either running over MC or Data
    Config.isMC = True
    if not Config.onGrid:
        options = VarParsing('analysis')
        options.register ('subChannel', 'T_t',
                  VarParsing.multiplicity.singleton,
                  VarParsing.varType.string,
                  "The sample that you are running on")
        options.register ('doDebug', False,
                  VarParsing.multiplicity.singleton,
                  VarParsing.varType.bool,
                  "Turn on debugging messages")
        options.register ('compHep', False,
                  VarParsing.multiplicity.singleton,
                  VarParsing.varType.bool,
                  "Turn on debugging messages")
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
        options.register ('doGenParticlePath', True,
                  VarParsing.multiplicity.singleton,
                  VarParsing.varType.bool,
                  "Run the gen particle paths (only works on specific MC)"
        )
        options.register ('destPUDistribution', "data",
                  VarParsing.multiplicity.singleton,
                  VarParsing.varType.string,
                  "destination pile-up distribution"
        )
        options.parseArguments()
        
        Config.channel = Config.Channel.signal
        Config.srcPUDistribution = pileUpDistributions.distributions[options.srcPUDistribution]
        Config.destPUDistribution = pileUpDistributions.distributions[options.destPUDistribution]
        
    
        Config.subChannel = options.subChannel
        Config.doDebug = options.doDebug
        Config.isMC = True
        Config.isCompHep = options.compHep
        Config.dataRun = "RunABCD"        

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

    process.decayTreeProducerMu = cms.EDProducer(
        'GenParticleDecayTreeProducer',
        src=cms.InputTag(Config.Muons.source)
    )

    process.decayTreeProducerEle = cms.EDProducer(
        'GenParticleDecayTreeProducer',
        src=cms.untracked.InputTag(Config.Electrons.source)
    )

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
    
    process.trueMuonsNTupleProducer = cms.EDProducer(
        "CandViewNtpProducer2",
        src = cms.InputTag(Config.Muons.source),
        lazyParser = cms.untracked.bool(True),
        prefix = cms.untracked.string(""),
        #eventInfo = cms.untracked.bool(True),
        variables = ntupleCollection(
            [
                ["Pt", "pt"],
                ["Eta", "eta"],
                ["Phi", "phi"],
                #["relIso", "userFloat('%s')" % Config.Muons.relIsoType],
                ["Charge", "charge"],
                ["genPdgId", "? genParticlesSize() > 0 ? genParticle(0).pdgId() : 0"],
                ["motherGenPdgId", "? genParticlesSize() > 0 ? genParticle(0).mother(0).pdgId() : 0"],                
            ]
      )
    )

    process.puWeightProducer = cms.EDProducer('PUWeightProducer'
            , maxVertices = cms.uint32(50)
            , srcDistribution = cms.vdouble(Config.srcPUDistribution)
            , destDistribution = cms.vdouble(Config.destPUDistribution)
        )

    process.muonWeightsProducer = cms.EDProducer("MuonEfficiencyProducer",
        src=cms.InputTag("genParticleSelector", "trueLepton", "STPOLSEL2"),
        dataRun=cms.string(Config.dataRun)
    )

    process.electronWeightsProducer = cms.EDProducer("ElectronEfficiencyProducer",
        src = cms.InputTag("genParticleSelector", "trueLepton", "STPOLSEL2")
    )

    process.elePathPreCount = cms.EDProducer("EventCountProducer")
    process.muPathPreCount = cms.EDProducer("EventCountProducer")

    process.treeSequenceNew = cms.Sequence(
        process.muPathPreCount *
        process.elePathPreCount *
        process.trueTopNTupleProducer *
        process.trueNuNTupleProducer *
        process.trueLeptonNTupleProducer *
        process.trueLightJetNTupleProducer *
        process.trueMuonsNTupleProducer *
        process.puWeightProducer #*
        #process.muonWeightsProducer *
        #process.electronWeightsProducer
    )

    if Config.isCompHep:
        from SingleTopPolarization.Analysis.partonStudy_comphep_step2_cfi import PartonStudySetup
    else:
        from SingleTopPolarization.Analysis.partonStudy_step2_cfi import PartonStudySetup
    PartonStudySetup(process)
    process.partonPath = cms.Path()
    process.partonPath += process.partonStudyTrueSequence
    process.treePath = cms.Path(
        process.treeSequenceNew
    )

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
                'keep floats_trueTopNTupleProducer_*_STPOLSEL2',
                'keep floats_trueNuNTupleProducer_*_STPOLSEL2',
                'keep floats_trueLeptonNTupleProducer_*_STPOLSEL2',
                #'keep floats_goodSignalMuonsNTupleProducer_*_STPOLSEL2',
                #'keep floats_goodSignalElectronsNTupleProducer_*_STPOLSEL2',
                #'keep floats_goodJetsNTupleProducer_*_STPOLSEL2',
                #'keep floats_lowestBTagJetNTupleProducer_*_STPOLSEL2',
                #'keep floats_highestBTagJetNTupleProducer_*_STPOLSEL2',
                'keep double_*__STPOLSEL2',
                'keep float_*__STPOLSEL2',
                'keep double_*_*_STPOLSEL2',
                'keep float_*_*_STPOLSEL2',
                #'keep double_cosTheta_*_STPOLSEL2',
                'keep double_cosThetaProducerTrueAll_*_STPOLSEL2',
                #'keep double_cosThetaProducerTrueTop_*_STPOLSEL2',
                #'keep double_cosThetaProducerTrueLepton_*_STPOLSEL2',
                #'keep double_cosThetaProducerTrueJet_*_STPOLSEL2',
                #'keep *_bTagWeightProducerNJMT_*_STPOLSEL2',
                'keep int_*__STPOLSEL2',
                'keep int_*_*_STPOLSEL2',
                'keep String_*_*_*', #the decay trees
                #'keep *_pdfInfo1_*_STPOLSEL2',
                #'keep *_pdfInfo2_*_STPOLSEL2',
                #'keep *_pdfInfo3_*_STPOLSEL2',
                #'keep *_pdfInfo4_*_STPOLSEL2',
                #'keep *_pdfInfo5_*_STPOLSEL2',
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
        #if Config.doElectron:
        #    process.out.SelectEvents.SelectEvents.append("elePath")
        #if Config.doMuon:
        #    process.out.SelectEvents.SelectEvents.append("muPath")

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
