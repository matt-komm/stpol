#Note - this is a generic example file. Rather than changing it, make your own based on it, using the cuts you need.
#You can also import this file to avoid copying all the necessary parameters by doing
#from runconfs.step3_eventLoop_cfg import *

import FWCore.ParameterSet.Config as cms
import sys
import pdb
import optparse
import random
import string
import os

print "argv=",sys.argv

#read input files from stdin
input_files = []
print "Waiting for input files over stdin..."
for line in sys.stdin.readlines():
    input_files.append(line.strip())

parser = optparse.OptionParser()
#parser.add_option("--outfile", dest="outfile", type="string")
parser.add_option("--lepton", dest="lepton", type="string", default="mu")
parser.add_option("--doNJets", dest="doNJets", action="store_true", default=False)
parser.add_option("--nJ", dest="nJ", type="string", default="0,10")
parser.add_option("--doNTags", dest="doNTags", action="store_true", default=False)
parser.add_option("--nT", dest="nT", type="string", default="0,10")
parser.add_option("--mtw", dest="doMtw", action="store_true", default=False)
parser.add_option("--isMC", dest="isMC", action="store_true", default=False)
parser.add_option("--mtop", dest="doMtop", action="store_true", default=False)
parser.add_option("--doControlVars", dest="doControlVars", action="store_true", default=False)
parser.add_option("--skipTree", dest="skipTree", action="store_true", default=False)
parser.add_option("--outputFile", dest="outputFile", type="string", default="step3.root")

options, args = parser.parse_args()

options.nJMin = int(options.nJ.split(",")[0])
options.nJMax = int(options.nJ.split(",")[1])
options.nTMin = int(options.nT.split(",")[0])
options.nTMax = int(options.nT.split(",")[1])


process = cms.Process("STPOLSEL3")
process.options = cms.untracked.PSet(wantSummary=cms.untracked.bool(True))

process.fwliteInput = cms.PSet(
    fileNames   = cms.vstring(input_files),
    maxEvents   = cms.int32(-1),
    outputEvery = cms.uint32(10000),
    makeTree = cms.bool(not options.skipTree)
)
print "Input files:"
for fi in input_files:
    print "\t",fi
print "Output file: %s" % options.outputFile

process.fwliteOutput = cms.PSet(
    fileName  = cms.string(options.outputFile),
)

process.muonCuts = cms.PSet(
    cutOnIso  = cms.bool(False),
    doControlVars  = cms.bool(options.doControlVars),
    reverseIsoCut  = cms.bool(False),
    requireOneMuon  = cms.bool(options.lepton=="mu"),
    isoCut  = cms.double(0.12),

    muonPtSrc  = cms.InputTag("goodSignalMuonsNTupleProducer", "Pt"),
    muonRelIsoSrc  = cms.InputTag("goodSignalMuonsNTupleProducer", "relIso"),
    muonCountSrc  = cms.InputTag("muonCount"),
    eleCountSrc  = cms.InputTag("electronCount"),

    doVetoLeptonCut = cms.bool(False),
    vetoMuCountSrc = cms.InputTag("looseVetoMuCount"),
    vetoEleCountSrc = cms.InputTag("looseVetoEleCount"),

    muonDbSrc = cms.InputTag("goodSignalMuonsNTupleProducer", "db"),
    muonDzSrc = cms.InputTag("goodSignalMuonsNTupleProducer", "dz"),
    muonNormChi2Src = cms.InputTag("goodSignalMuonsNTupleProducer", "normChi2"),
    muonChargeSrc = cms.InputTag("goodSignalMuonsNTupleProducer", "Charge"),

    muonGTrackHitsSrc = cms.InputTag("goodSignalMuonsNTupleProducer", "globalTrackhitPatternnumberOfValidMuonHits"),
    muonITrackHitsSrc = cms.InputTag("goodSignalMuonsNTupleProducer", "innerTrackhitPatternnumberOfValidPixelHits"),
    muonStationsSrc = cms.InputTag("goodSignalMuonsNTupleProducer", "numberOfMatchedStations"),
    muonLayersSrc = cms.InputTag("goodSignalMuonsNTupleProducer", "trackhitPatterntrackerLayersWithMeasurement"),
    muonMotherPdgIdSrc = cms.InputTag("goodSignalMuonsNTupleProducer", "motherGenPdgId"),
    muonDecayTreeSrc = cms.InputTag("decayTreeProducerMu"),
)

process.eleCuts = cms.PSet(
    requireOneElectron = cms.bool(options.lepton=="ele"),
    eleCountSrc  = cms.InputTag("electronCount"),
    muonCountSrc = cms.InputTag("muonCount"),
    electronRelIsoSrc = cms.InputTag("goodSignalElectronsNTupleProducer","relIso"),
    electronMvaSrc = cms.InputTag("goodSignalElectronsNTupleProducer","mvaID"),
    electronPtSrc = cms.InputTag("goodSignalElectronsNTupleProducer", "Pt"),
    electronChargeSrc = cms.InputTag("goodSignalElectronsNTupleProducer", "Charge"),
    electronMotherPdgIdSrc = cms.InputTag("goodSignalElectronsNTupleProducer", "motherGenPdgId"),
    doVetoLeptonCut = cms.bool(False),
    vetoMuCountSrc = cms.InputTag("looseVetoMuCount"),
    vetoEleCountSrc = cms.InputTag("looseVetoEleCount"),
    electronDecayTreeSrc = cms.InputTag("decayTreeProducerEle"),
)

process.jetCuts = cms.PSet(
    cutOnNJets = cms.bool(options.doNJets),
    applyRmsLj = cms.bool(False),
    applyEtaLj = cms.bool(False),

    goodJetsCountSrc = cms.InputTag("goodJetCount"),
    bTagJetsCountSrc = cms.InputTag("bJetCount"),

    rmsMax = cms.double(0.025),
    etaMin = cms.double(0.0),

    nJetsMin = cms.int32(options.nJMin),
    nJetsMax = cms.int32(options.nJMax),

    goodJetsPtSrc = cms.InputTag("goodJetsNTupleProducer", "Pt"),
    goodJetsEtaSrc = cms.InputTag("goodJetsNTupleProducer", "Eta"),

    lightJetEtaSrc = cms.InputTag("lowestBTagJetNTupleProducer", "Eta"),
    lightJetBdiscrSrc = cms.InputTag("lowestBTagJetNTupleProducer", "bDiscriminatorTCHP"),
    lightJetPtSrc = cms.InputTag("lowestBTagJetNTupleProducer", "Pt"),
    lightJetRmsSrc = cms.InputTag("lowestBTagJetNTupleProducer", "rms"),
    lightJetDeltaRSrc = cms.InputTag("lowestBTagJetNTupleProducer", "deltaR"),

    #bJetEtaSrc = cms.InputTag("highestBTagJetNTupleProducer", "Eta"),
    #bJetBdiscrSrc = cms.InputTag("highestBTagJetNTupleProducer", "bDiscriminatorTCHP"),
    #bJetPtSrc = cms.InputTag("highestBTagJetNTupleProducer", "Pt"),
)

process.bTagCuts = cms.PSet(
    cutOnNTags  = cms.bool(options.doNTags),

    bTagJetsCountSrc = cms.InputTag("bJetCount"),

    nTagsMin = cms.int32(options.nTMin),
    nTagsMax = cms.int32(options.nTMax),

    bJetEtaSrc = cms.InputTag("highestBTagJetNTupleProducer", "Eta"),
    bJetBdiscrSrc = cms.InputTag("highestBTagJetNTupleProducer", "bDiscriminatorTCHP"),
    bJetPtSrc = cms.InputTag("highestBTagJetNTupleProducer", "Pt"),
    bJetDeltaRSrc = cms.InputTag("highestBTagJetNTupleProducer", "deltaR")
)

process.topCuts = cms.PSet(
        applyMassCut = cms.bool(options.doMtop),
        signalRegion = cms.bool(True),
        signalRegionMassLow = cms.double(130),
        signalRegionMassHigh = cms.double(220),
        topMassSrc = cms.InputTag("recoTopNTupleProducer", "Mass")
)

process.weights = cms.PSet(
    doWeights = cms.bool(options.isMC),
    doWeightSys = cms.bool(options.isMC),

    bWeightNominalSrc = cms.InputTag("bTagWeightProducerNoCut", "bTagWeight"),
    puWeightSrc = cms.InputTag("puWeightProducer", "PUWeightNtrue"),

    muonIDWeightSrc = cms.InputTag("muonWeightsProducer", "muonIDWeight"),
    muonIsoWeightSrc = cms.InputTag("muonWeightsProducer", "muonIsoWeight"),
    muonTriggerWeightSrc = cms.InputTag("muonWeightsProducer", "muonTriggerWeight"),

    electronIDWeightSrc = cms.InputTag("electronWeightsProducer","electronIdIsoWeight"),
    electronTriggerWeightSrc = cms.InputTag("electronWeightsProducer","electronTriggerWeight"),

    bWeightNominalLUpSrc = cms.InputTag("bTagWeightProducerNoCut", "bTagWeightSystLUp"),
    bWeightNominalLDownSrc = cms.InputTag("bTagWeightProducerNoCut", "bTagWeightSystLDown"),
    bWeightNominalBCUpSrc = cms.InputTag("bTagWeightProducerNoCut", "bTagWeightSystBCUp"),
    bWeightNominalBCDownSrc = cms.InputTag("bTagWeightProducerNoCut", "bTagWeightSystBCDown"),

    muonIDWeightUpSrc = cms.InputTag("muonWeightsProducer", "muonIDWeightUp"),
    muonIDWeightDownSrc = cms.InputTag("muonWeightsProducer", "muonIDWeightDown"),
    muonIsoWeightUpSrc = cms.InputTag("muonWeightsProducer", "muonIsoWeightUp"),
    muonIsoWeightDownSrc = cms.InputTag("muonWeightsProducer", "muonIsoWeightDown"),
    muonTriggerWeightUpSrc = cms.InputTag("muonWeightsProducer", "muonTriggerWeightUp"),
    muonTriggerWeightDownSrc = cms.InputTag("muonWeightsProducer", "muonTriggerWeightDown"),

    electronIDWeightUpSrc = cms.InputTag("electronWeightsProducer","electronIdIsoWeightUp"),
    electronIDWeightDownSrc = cms.InputTag("electronWeightsProducer","electronIdIsoWeightDown"),
    electronTriggerWeightUpSrc = cms.InputTag("electronWeightsProducer","electronTriggerWeightUp"),
    electronTriggerWeightDownSrc = cms.InputTag("electronWeightsProducer","electronTriggerWeightDown"),
)

process.mtMuCuts = cms.PSet(
    mtMuSrc = cms.InputTag("muAndMETMT"),
    metSrc = cms.InputTag("patMETNTupleProducer", "Pt"),
    doMTCut = cms.bool(options.doMtw),
    minVal = cms.double(50)
)

#The versions should be specified explicitly at the moment
process.HLTmu = cms.PSet(
    hltSrc = cms.InputTag("TriggerResults", "", "HLT"),
    hltNames = cms.vstring([
        "HLT_IsoMu24_eta2p1_v11",
        "HLT_IsoMu24_eta2p1_v12",
        "HLT_IsoMu24_eta2p1_v13",
        "HLT_IsoMu24_eta2p1_v14",
        "HLT_IsoMu24_eta2p1_v15",
        "HLT_IsoMu24_eta2p1_v17",
        "HLT_IsoMu24_eta2p1_v16"
    ]),
    doCutOnHLT = cms.bool(options.lepton=="mu"),
    saveHLTVars = cms.bool(False)
)

process.HLTele = cms.PSet(
    hltSrc = cms.InputTag("TriggerResults", "", "HLT"),
    hltNames = cms.vstring([
        "HLT_Ele27_WP80_v8",
        "HLT_Ele27_WP80_v9",
        "HLT_Ele27_WP80_v10",
        "HLT_Ele27_WP80_v11",
        ]),
    doCutOnHLT = cms.bool(options.lepton=="ele"),
    saveHLTVars = cms.bool(False)
)

process.finalVars = cms.PSet(
    cosThetaSrc = cms.InputTag("cosTheta", "cosThetaLightJet"),
    nVerticesSrc = cms.InputTag("goodOfflinePVCount"),
    #scaleFactorsSrc = cms.InputTag("bTagWeightProducerNJMT", "scaleFactors")

    #PDF stuff
    addPDFInfo = cms.bool(False),
    scalePDFSrc = cms.InputTag("PDFweights", "scalePDF"),
	x1Src = cms.InputTag("PDFweights", "x1"),
	x2Src = cms.InputTag("PDFweights", "x2"),
	id1Src = cms.InputTag("PDFweights", "id1"),
	id2Src = cms.InputTag("PDFweights", "id2"),

    #PDFSets = cms.vstring('cteq66.LHgrid','MSTW2008nlo68cl.LHgrid') #ok
	PDFSets	= cms.vstring('NNPDF21_100.LHgrid','CT10.LHgrid','MSTW2008nlo68cl.LHgrid'),
)

process.lumiBlockCounters = cms.PSet(
    totalPATProcessedCountSrc = cms.InputTag("singleTopPathStep1MuPreCount")
)

process.genParticles = cms.PSet(
    doGenParticles = cms.bool(options.isMC and options.doControlVars),
    trueBJetCountSrc = cms.InputTag("trueBJetCount"),
    trueCJetCountSrc = cms.InputTag("trueCJetCount"),
    trueLJetCountSrc = cms.InputTag("trueLJetCount"),
    trueBJetTaggedCountSrc = cms.InputTag("btaggedTrueBJetCount"),
    trueCJetTaggedCountSrc = cms.InputTag("btaggedTrueCJetCount"),
    trueLJetTaggedCountSrc = cms.InputTag("btaggedTrueLJetCount"),
    trueCosThetaSrc = cms.InputTag("cosThetaProducerTrueAll", "cosThetaLightJet"),
    trueLeptonPdgIdSrc = cms.InputTag("genParticleSelector", "trueLeptonPdgId"),
    wJetsClassificationSrc = cms.InputTag("flavourAnalyzer", "simpleClass"),
	requireGenMuon  = cms.bool(False)
)

process.bEfficiencyCalcs = cms.PSet(
    doBEffCalcs = cms.bool(options.isMC),
    jetPtSrc = cms.InputTag("goodJetsNTupleProducer", "Pt"),
    jetEtaSrc = cms.InputTag("goodJetsNTupleProducer", "Eta"),
    jetBDiscriminatorSrc = cms.InputTag("goodJetsNTupleProducer", "bDiscriminatorTCHP"),
    jetFlavourSrc = cms.InputTag("goodJetsNTupleProducer", "partonFlavour"),
)

for k, v in process.__dict__.items():
    if isinstance(v, cms.PSet):
        print k, v
