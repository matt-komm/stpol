raise Exception("FIXME: rewrite to import base_nocuts and work from there")
#Compile with
#$ scram b -f SingleTopPolarization/Analysis
#Output will be in $CMSSW_DIR/bin/
import FWCore.ParameterSet.Config as cms
import sys
import pdb
import optparse
import random
import string
import os

#outfile = "step3_out_%s.root" % (''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(6)))
if "STPOL_STEP3_OUTPUTFILE" in os.environ.keys():
    outfile = os.environ['STPOL_STEP3_OUTPUTFILE']
else:
    outfile = "out_step3.root"
if "STPOL_ISMC" in os.environ.keys():
    isMC_env = os.environ["STPOL_ISMC"]
    if isMC_env.lower() == "true":
        isMC = True
    elif isMC_env.lower() == "false":
        isMC = False
    else:
        raise ValueError("STPOL_ISMC must be true/false")
else:
    isMC = True
print "isMC = %s" % isMC

isAntiIso = False
isoC = 0.12
if "STPOL_ANTIISO" in os.environ.keys():
    isAntiIso_env = os.environ["STPOL_ANTIISO"]
    if isAntiIso_env.lower() == "true":
        isAntiIso = True
        isoC = 0.2
    elif isAntiIso_env.lower() == "false":
        isAntiIso = False
        isoC = 0.12
    else:
        raise ValueError("STPOL_ANTIISO must be true/false")
print "isAntiIso = %s" % isAntiIso


#read input files from stdin
input_files = []
print "Waiting for input files over stdin..."
for line in sys.stdin.readlines():
    input_files.append(line.strip())


#parser = optparse.OptionParser()
#parser.add_option("--outfile", dest="outfile", type="string")
#options, args = parser.parse_args()

process = cms.Process("STPOLSEL3")
#process.load("FWCore.MessageLogger.MessageLogger_cfi")
#process.MessageLogger.cerr.FwkReport.reportEvery = 1000
#process.MessageLogger.cerr.threshold = cms.untracked.string("INFO")
process.options = cms.untracked.PSet(wantSummary=cms.untracked.bool(True))

process.fwliteInput = cms.PSet(
    fileNames   = cms.vstring(input_files),
    maxEvents   = cms.int32(-1),
    outputEvery = cms.uint32(100000),
)
print "Input files: %s" % input_files
print "Output file: %s" %  outfile

doControlVars = True
process.fwliteOutput = cms.PSet(
    fileName  = cms.string(outfile),
)

process.muonCuts = cms.PSet(
    cutOnIso  = cms.bool(True),
    doControlVars  = cms.bool(False),
    reverseIsoCut  = cms.bool(isAntiIso),
    requireOneMuon  = cms.bool(True),
    isoCut  = cms.double(isoC),
    muonPtSrc  = cms.InputTag("goodSignalMuonsNTupleProducer", "Pt"),
    muonRelIsoSrc  = cms.InputTag("goodSignalMuonsNTupleProducer", "relIso"),
    muonCountSrc  = cms.InputTag("muonCount"),
    eleCountSrc  = cms.InputTag("electronCount"),
    doVetoLeptonCut = cms.bool(True),
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
)

process.eleCuts = cms.PSet(
    requireOneElectron = cms.bool(False),
    eleCountSrc  = cms.InputTag("electronCount"),
    muonCountSrc = cms.InputTag("muonCount"),
    electronRelIsoSrc = cms.InputTag("goodSignalElectronsNTupleProducer","relIso"),
    electronMvaSrc = cms.InputTag("goodSignalElectronsNTupleProducer","mvaID"),
    electronPtSrc = cms.InputTag("goodSignalElectronsNTupleProducer", "Pt"),
    electronChargeSrc = cms.InputTag("goodSignalElectronsNTupleProducer", "Charge"),
    electronMotherPdgIdSrc = cms.InputTag("goodSignalElectronsNTupleProducer", "motherGenPdgId"),
    doVetoLeptonCut = cms.bool(True),
    vetoMuCountSrc = cms.InputTag("looseVetoMuCount"),
    vetoEleCountSrc = cms.InputTag("looseVetoEleCount"),
)

process.jetCuts = cms.PSet(
    cutOnNJets  = cms.bool(True),
    cutOnNTags  = cms.bool(True),
    applyRmsLj  = cms.bool(False),
    applyEtaLj  = cms.bool(False),

    goodJetsCountSrc = cms.InputTag("goodJetCount"),
    bTagJetsCountSrc = cms.InputTag("bJetCount"),

    rmsMax = cms.double(0.025),

    nJetsMin = cms.int32(2),
    nJetsMax = cms.int32(5),

    nTagsMin = cms.int32(0),
    nTagsMax = cms.int32(4),

    etaMin = cms.double(2.5),

    goodJetsPtSrc = cms.InputTag("goodJetsNTupleProducer", "Pt"),
    goodJetsEtaSrc = cms.InputTag("goodJetsNTupleProducer", "Eta"),

    lightJetEtaSrc = cms.InputTag("lowestBTagJetNTupleProducer", "Eta"),
    lightJetBdiscrSrc = cms.InputTag("lowestBTagJetNTupleProducer", "bDiscriminatorTCHP"),
    lightJetPtSrc = cms.InputTag("lowestBTagJetNTupleProducer", "Pt"),
    lightJetRmsSrc = cms.InputTag("lowestBTagJetNTupleProducer", "rms"),
    lightJetDeltaRSrc = cms.InputTag("lowestBTagJetNTupleProducer", "deltaR"),

)

process.bTagCuts = cms.PSet(
    cutOnNTags  = cms.bool(False),

    bTagJetsCountSrc = cms.InputTag("bJetCount"),

    nTagsMin = cms.int32(0),
    nTagsMax = cms.int32(2),

    bJetEtaSrc = cms.InputTag("highestBTagJetNTupleProducer", "Eta"),
    bJetBdiscrSrc = cms.InputTag("highestBTagJetNTupleProducer", "bDiscriminatorTCHP"),
    bJetPtSrc = cms.InputTag("highestBTagJetNTupleProducer", "Pt"),
    bJetDeltaRSrc = cms.InputTag("highestBTagJetNTupleProducer", "deltaR")
)

process.topCuts = cms.PSet(
        applyMassCut = cms.bool(False),
        signalRegion = cms.bool(True),
        signalRegionMassLow = cms.double(130),
        signalRegionMassHigh = cms.double(220),
        topMassSrc = cms.InputTag("recoTopNTupleProducer", "Mass")
)

process.weights = cms.PSet(
    doWeights = cms.bool(isMC),
    bWeightNominalSrc = cms.InputTag("bTagWeightProducerNJMT", "bTagWeight"),
    puWeightSrc = cms.InputTag("puWeightProducer", "PUWeightNtrue"),
    muonIDWeightSrc = cms.InputTag("muonWeightsProducer", "muonIDWeight"),
    muonIsoWeightSrc = cms.InputTag("muonWeightsProducer", "muonIsoWeight"),
    muonTriggerWeightSrc = cms.InputTag("muonWeightsProducer", "muonTriggerWeight"),

    electronIDWeightSrc = cms.InputTag("electronWeightsProducer","electronIdIsoWeight"),
    electronTriggerWeightSrc = cms.InputTag("electronWeightsProducer","electronTriggerWeight")
)

process.mtMuCuts = cms.PSet(
    mtMuSrc = cms.InputTag("muAndMETMT"),
    metSrc = cms.InputTag("patMETNTupleProducer", "Pt"),
    doMTCut = cms.bool(False),
    minVal = cms.double(50)
)

process.HLT = cms.PSet(
       hltSrc = cms.InputTag("TriggerResults", "", "HLT"),
       hltNames = cms.vstring([
           "HLT_IsoMu24_eta2p1_v17",
           "HLT_IsoMu24_eta2p1_v16",
           "HLT_IsoMu24_eta2p1_v15",
           "HLT_IsoMu24_eta2p1_v14",
           "HLT_IsoMu24_eta2p1_v13",
           "HLT_IsoMu24_eta2p1_v12",
           "HLT_IsoMu24_eta2p1_v11",
           "HLT_Mu24_eta2p1_v3"
       ]),
       cutOnHLT = cms.string("HLT_IsoMu24_eta2p1_v12"),
       doCutOnHLT = cms.bool(False)
)

process.HLTele = cms.PSet(
    hltSrc = cms.InputTag("TriggerResults", "", "HLT"),
    hltNames = cms.vstring([
        "HLT_Ele27_WP80_v8",
        "HLT_Ele27_WP80_v9",
        "HLT_Ele27_WP80_v10",
        "HLT_Ele27_WP80_v11",
        ]),
    doCutOnHLT = cms.bool(False)
)


process.finalVars = cms.PSet(
    cosThetaSrc = cms.InputTag("cosTheta", "cosThetaLightJet"),
    nVerticesSrc = cms.InputTag("offlinePVCount"),
    scaleFactorsSrc = cms.InputTag("bTagWeightProducerNJMT", "scaleFactors"),
    addPDFInfo = cms.bool(False)
)

process.lumiBlockCounters = cms.PSet(
    totalPATProcessedCountSrc = cms.InputTag("singleTopPathStep1MuPreCount")
)

process.genParticles = cms.PSet(
    doGenParticles = cms.bool(isMC),
    trueBJetCountSrc = cms.InputTag("trueBJetCount"),
    trueCJetCountSrc = cms.InputTag("trueCJetCount"),
    trueLJetCountSrc = cms.InputTag("trueLJetCount"),
    trueBJetTaggedCountSrc = cms.InputTag("btaggedTrueBJetCount"),
    trueCJetTaggedCountSrc = cms.InputTag("btaggedTrueCJetCount"),
    trueLJetTaggedCountSrc = cms.InputTag("btaggedTrueLJetCount"),
    trueCosThetaSrc = cms.InputTag("cosThetaProducerTrueAll", "cosThetaLightJet"),
    trueLeptonPdgIdSrc = cms.InputTag("genParticleSelector", "trueLeptonPdgId"),
	requireGenMuon  = cms.bool(False)
)
