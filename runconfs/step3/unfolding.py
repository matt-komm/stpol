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
    outputEvery = cms.uint32(10000000),
)
print "Input files: %s" % input_files
print "Output file: %s" %  outfile

process.fwliteOutput = cms.PSet(
    fileName  = cms.string(outfile),
)

process.muonCuts = cms.PSet(
    cutOnIso  = cms.bool(True),
    doControlVars  = cms.bool(False),
    reverseIsoCut  = cms.bool(False),
    requireOneMuon  = cms.bool(True),
    isoCut  = cms.double(0.12),
    muonPtSrc  = cms.InputTag("goodSignalMuonsNTupleProducer", "Pt"),
    muonRelIsoSrc  = cms.InputTag("goodSignalMuonsNTupleProducer", "relIso"),
    muonCountSrc  = cms.InputTag("muonCount"),
    eleCountSrc  = cms.InputTag("electronCount"),
    doVetoLeptonCut = cms.bool(True),
    vetoMuCountSrc = cms.InputTag("looseVetoMuCount"),
    vetoEleCountSrc = cms.InputTag("looseVetoEleCount"),
)

process.eleCuts = cms.PSet(
)

process.jetCuts = cms.PSet(
    cutOnNJets  = cms.bool(True),
    cutOnNTags  = cms.bool(True),
    applyRmsLj  = cms.bool(True),
    applyEtaLj  = cms.bool(True),

    goodJetsCountSrc = cms.InputTag("goodJetCount"),
    bTagJetsCountSrc = cms.InputTag("bJetCount"),

    rmsMax = cms.double(0.025),

    nJetsMin = cms.int32(2),
    nJetsMax = cms.int32(2),

    etaMin = cms.double(2.5),

    goodJetsPtSrc = cms.InputTag("goodJetsNTupleProducer", "Pt"),
    goodJetsEtaSrc = cms.InputTag("goodJetsNTupleProducer", "Eta"),

    lightJetEtaSrc = cms.InputTag("lowestBTagJetNTupleProducer", "Eta"),
    lightJetBdiscrSrc = cms.InputTag("lowestBTagJetNTupleProducer", "bDiscriminatorTCHP"),
    lightJetPtSrc = cms.InputTag("lowestBTagJetNTupleProducer", "Pt"),
    lightJetRmsSrc = cms.InputTag("lowestBTagJetNTupleProducer", "rms"),

    bJetEtaSrc = cms.InputTag("highestBTagJetNTupleProducer", "Eta"),
    bJetBdiscrSrc = cms.InputTag("highestBTagJetNTupleProducer", "bDiscriminatorTCHP"),
    bJetPtSrc = cms.InputTag("highestBTagJetNTupleProducer", "Pt"),

	lightJetDeltaRSrc = cms.InputTag("lowestBTagJetNTupleProducer", "deltaR")

)

process.bTagCuts = cms.PSet(
    cutOnNTags  = cms.bool(True),

    bTagJetsCountSrc = cms.InputTag("bJetCount"),

    nTagsMin = cms.int32(1),
    nTagsMax = cms.int32(1),

    bJetEtaSrc = cms.InputTag("highestBTagJetNTupleProducer", "Eta"),
    bJetBdiscrSrc = cms.InputTag("highestBTagJetNTupleProducer", "bDiscriminatorTCHP"),
    bJetPtSrc = cms.InputTag("highestBTagJetNTupleProducer", "Pt"),
    bJetDeltaRSrc = cms.InputTag("highestBTagJetNTupleProducer", "deltaR")
)

process.topCuts = cms.PSet(
        applyMassCut = cms.bool(True),
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
    muonIsoWeightSrc = cms.InputTag("muonWeightsProducer", "muonIsoWeight")
)

process.mtMuCuts = cms.PSet(
    mtMuSrc = cms.InputTag("muAndMETMT"),
    metSrc = cms.InputTag("patMETNTupleProducer", "Pt"),
    doMTCut = cms.bool(True),
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
           "HLT_IsoMu24_eta2p1_v11"
       ]),
       cutOnHLT = cms.string("HLT_IsoMu24_eta2p1_v12"),
       doCutOnHLT = cms.bool(False)
)


process.finalVars = cms.PSet(
    cosThetaSrc = cms.InputTag("cosTheta", "cosThetaLightJet"),
    nVerticesSrc = cms.InputTag("offlinePVCount"),
    scaleFactorsSrc = cms.InputTag("bTagWeightProducerNJMT", "scaleFactors"),

    #PDF stuff
    addPDFInfo = cms.bool(True),
    scalePDFSrc = cms.InputTag("PDFweights", "scalePDF"),
	x1Src = cms.InputTag("PDFweights", "x1"),
	x2Src = cms.InputTag("PDFweights", "x2"),
	id1Src = cms.InputTag("PDFweights", "id1"),
	id2Src = cms.InputTag("PDFweights", "id2"),

    #PDFSets = cms.vstring('cteq66.LHgrid','MSTW2008nlo68cl.LHgrid') #ok
	PDFSets	= cms.vstring('NNPDF21_100.LHgrid','CT10.LHgrid','MSTW2008nlo68cl.LHgrid'),

    lowestBTagJetNTupleProducerEtaSrc = cms.InputTag("lowestBTagJetNTupleProducer", "Eta"),
    #muAndMETMTSrc = cms.InputTag("muAndMETMT", ""),
    recoTopNTupleProducerMassSrc = cms.InputTag("recoTopNTupleProducer", "Mass"),
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
