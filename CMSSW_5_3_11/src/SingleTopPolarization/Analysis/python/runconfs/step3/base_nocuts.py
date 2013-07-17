#Note - this is a generic example file. Rather than changing it, make your own based on it, using the cuts you need.
#NOTE!!!!
#Don't change the cut behaviour in this file without notice. It's imported by other files and sets reasonable defaults.

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

#FIXME: replace old-style OptionParser with ArgumentParser for more flexibility
class OptionParser(optparse.OptionParser):
    def add_option(self, *args, **kwargs):
        if "description" in kwargs.keys():
            kwargs.pop("description")
        if "choices" in kwargs.keys():
            kwargs.pop("choices")
        optparse.OptionParser.add_option(self, *args, **kwargs)

parser = OptionParser()
parser.add_option("--doLepton", dest="doLepton", action="store_true", default=False,
    description="Select events that had exactly one good lepton."
)
parser.add_option("--doHLT", dest="doHLT", action="store_true", default=False,
    description="Select events that pass the HLT corresponding to the lepton channel."
)
parser.add_option("--lepton", dest="lepton", type="string", default="mu", choices=["mu", "ele"],
    description="Specify the lepton channel."
)
parser.add_option("--doNJets", dest="doNJets", action="store_true", default=False,
    description="Select events that had a particular number of jets."
)
parser.add_option("--nJ", dest="nJ", type="string", default="0,10",
    description="The number of jets to consider."
)
parser.add_option("--doNTags", dest="doNTags", action="store_true", default=False,
    description="Select events that had a number of tags."
)
parser.add_option("--nT", dest="nT", type="string", default="0,10",
    description="A comma separated list of min,max of the number of tags to consider."
)
parser.add_option("--mtw", dest="doMtw", action="store_true", default=False,
    description="Select events that pass an MtW(mu) cut."
)
parser.add_option("--met", dest="doMet", action="store_true", default=False,
    description="Select events that pass a MET cut."
)
parser.add_option("--etalj", dest="doEtaLj", action="store_true", default=False,
    description="Select events that pass the |eta_lj|>2.5 cut."
)
parser.add_option("--isMC", dest="isMC", action="store_true", default=False,
    description="Processed files are MC."
)
parser.add_option("--mtop", dest="mtop", type="string", default="none", choices=["SR", "SB", "none"],
    description="Select events that pass the top mass window cut in a predefined signal/sideband region."
)
parser.add_option("--doControlVars", dest="doControlVars", action="store_true", default=False,
    description="Add several additional variables in the trees."
)
parser.add_option("--doEventShape", dest="doEventShape", action="store_true", default=False,
    description="Do runtime calculation of the event shape variables."
)
parser.add_option("--isAntiIso", dest="isAntiIso", action="store_true", default=False,
    description="Enable anti-iso lepton specific processing."
)
parser.add_option("--skipTree", dest="skipTree", action="store_true", default=False,
    description="Do not produce the output tree."
)
parser.add_option("--outputFile", dest="outputFile", type="string", default="step3.root",
    description="Filename of the flat ROOT output file."
)
parser.add_option("--cutString", dest="cutString", type="string", default="1.0",
    description="An additional TTree called Events_selected will be created by applying this cutstring.\
    Note that applying this cut string will NOT decrease processing time by skipping some events,\
    which is conceptually different from the above cuts."
)

options, args = parser.parse_args()

options.nJMin = int(options.nJ.split(",")[0])
options.nJMax = int(options.nJ.split(",")[1])
options.nTMin = int(options.nT.split(",")[0])
options.nTMax = int(options.nT.split(",")[1])

#Note: the isolation cut is already necesarily applied in step 2. Applying it here is redundant, unless
#one wants to tighten the single (anti)-isolated lepton and get a strict subset of the selected events.
if options.lepton=="mu":
    if options.isAntiIso:
        isoC = 0.2
        isoCHigh = 0.9
    else:
        isoC = 0.12
        isoCHigh = 0.12
else:
    #FIXME: whatever is needed for electrons
    isoC = -1
    isoCHigh = -1

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
    fileName = cms.string(options.outputFile),
    cutString = cms.string(options.cutString)
)

process.muonCuts = cms.PSet(
    requireOneMuon  = cms.bool(options.doLepton and options.lepton=="mu"),
    doControlVars  = cms.bool(options.doControlVars),
    reverseIsoCut  = cms.bool(options.isAntiIso),
    cutOnIso = cms.bool(False), #by default this is NOT necessary (done @ step2)
    isoCut  = cms.double(isoC),
    isoCutHigh  = cms.double(isoCHigh),

    muonPtSrc  = cms.InputTag("goodSignalMuonsNTupleProducer", "Pt"),
    muonEtaSrc  = cms.InputTag("goodSignalMuonsNTupleProducer", "Eta"),
    muonPhiSrc  = cms.InputTag("goodSignalMuonsNTupleProducer", "Phi"),

    muonRelIsoSrc  = cms.InputTag("goodSignalMuonsNTupleProducer", "relIso"),
    muonCountSrc  = cms.InputTag("muonCount"),
    eleCountSrc  = cms.InputTag("electronCount"),

    doVetoLeptonCut = cms.bool(options.doLepton and options.lepton=="mu"),
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
    muonTriggerMatchSrc = cms.InputTag("goodSignalMuonsNTupleProducer", "triggerMatch"),
    muonDecayTreeSrc = cms.InputTag("decayTreeProducerMu"),
)

process.eleCuts = cms.PSet(
    requireOneElectron = cms.bool(options.doLepton and options.lepton=="ele"),
    reverseIsoCut = cms.bool(options.isAntiIso),
    cutOnIso = cms.bool(False),
    isoCut = cms.double(0.1),
    mvaCut = cms.double(0.9),

    eleCountSrc  = cms.InputTag("electronCount"),
    muonCountSrc = cms.InputTag("muonCount"),
    electronRelIsoSrc = cms.InputTag("goodSignalElectronsNTupleProducer","relIso"),
    electronMvaSrc = cms.InputTag("goodSignalElectronsNTupleProducer","mvaID"),

    electronPtSrc = cms.InputTag("goodSignalElectronsNTupleProducer", "Pt"),
    electronEtaSrc = cms.InputTag("goodSignalElectronsNTupleProducer", "Eta"),
    electronPhiSrc = cms.InputTag("goodSignalElectronsNTupleProducer", "Phi"),

    electronChargeSrc = cms.InputTag("goodSignalElectronsNTupleProducer", "Charge"),
    electronMotherPdgIdSrc = cms.InputTag("goodSignalElectronsNTupleProducer", "motherGenPdgId"),
    electronTriggerMatchSrc = cms.InputTag("goodSignalElectronsNTupleProducer", "triggerMatch"),

    doVetoLeptonCut = cms.bool(options.doLepton and options.lepton=="ele"),
    vetoMuCountSrc = cms.InputTag("looseVetoMuCount"),
    vetoEleCountSrc = cms.InputTag("looseVetoEleCount"),
    electronDecayTreeSrc = cms.InputTag("decayTreeProducerEle"),
)

process.jetCuts = cms.PSet(
    cutOnNJets = cms.bool(options.doNJets),
    applyRmsLj = cms.bool(False),
    applyEtaLj = cms.bool(options.doEtaLj),

    goodJetsCountSrc = cms.InputTag("goodJetCount"),
    bTagJetsCountSrc = cms.InputTag("bJetCount"),

    rmsMax = cms.double(0.025),
    etaMin = cms.double(2.5),

    nJetsMin = cms.int32(options.nJMin),
    nJetsMax = cms.int32(options.nJMax),

    goodJetsPtSrc = cms.InputTag("goodJetsNTupleProducer", "Pt"),
    goodJetsEtaSrc = cms.InputTag("goodJetsNTupleProducer", "Eta"),

    lightJetPtSrc = cms.InputTag("lowestBTagJetNTupleProducer", "Pt"),
    lightJetEtaSrc = cms.InputTag("lowestBTagJetNTupleProducer", "Eta"),
    lightJetPhiSrc = cms.InputTag("lowestBTagJetNTupleProducer", "Phi"),
    lightJetPUMVASrc = cms.InputTag("lowestBTagJetNTupleProducer", "puMva"),

    lightJetBdiscrSrc = cms.InputTag("lowestBTagJetNTupleProducer", "bDiscriminatorTCHP"),
    lightJetRmsSrc = cms.InputTag("lowestBTagJetNTupleProducer", "rms"),
    lightJetDeltaRSrc = cms.InputTag("lowestBTagJetNTupleProducer", "deltaR"),
)

process.bTagCuts = cms.PSet(
    cutOnNTags  = cms.bool(options.doNTags),

    bTagJetsCountSrc = cms.InputTag("bJetCount"),

    nTagsMin = cms.int32(options.nTMin),
    nTagsMax = cms.int32(options.nTMax),

    bJetPtSrc = cms.InputTag("highestBTagJetNTupleProducer", "Pt"),
    bJetEtaSrc = cms.InputTag("highestBTagJetNTupleProducer", "Eta"),
    bJetPhiSrc = cms.InputTag("highestBTagJetNTupleProducer", "Phi"),
    bJetPUMVASrc = cms.InputTag("highestBTagJetNTupleProducer", "puMva"),

    bJetBdiscrSrc = cms.InputTag("highestBTagJetNTupleProducer", "bDiscriminatorTCHP"),
    bJetDeltaRSrc = cms.InputTag("highestBTagJetNTupleProducer", "deltaR")
)

process.topCuts = cms.PSet(
        applyMassCut = cms.bool(options.mtop != "none"),
        signalRegion = cms.bool(options.mtop == "SR"),
        signalRegionMassLow = cms.double(130),
        signalRegionMassHigh = cms.double(220),
        topMassSrc = cms.InputTag("recoTopNTupleProducer", "Mass")
)

process.weights = cms.PSet(
    doWeights = cms.bool(options.isMC),
    doWeightSys = cms.bool(options.isMC),
    leptonChannel = cms.string(options.lepton),

    bWeightNominalSrc = cms.InputTag("bTagWeightProducerNoCut", "bTagWeight"),
    puWeightSrc = cms.InputTag("puWeightProducer", "PUWeightNtrue"),
    ttbarWeightSrc = cms.InputTag("ttbarTopWeight", "weight"),

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

process.metCuts = cms.PSet(
    mtMuSrc = cms.InputTag("muAndMETMT"),
    mtElSrc = cms.InputTag("eleAndMETMT"),
    metSrc = cms.InputTag("patMETNTupleProducer", "Pt"),
    metPhiSrc = cms.InputTag("patMETNTupleProducer", "Phi"),
    doMTCut = cms.bool( options.doMtw ),
    doMETCut = cms.bool( options.doMet ),
    minValMtw = cms.double(50),
    minValMet = cms.double(45)
    )

process.evtShapeVars = cms.PSet(
    doEvtShapeVars = cms.bool(options.doEventShape),
    leptonChannel = cms.string(options.lepton),

    muPtSrc = cms.InputTag("goodSignalMuonsNTupleProducer", "Pt"),
    muEtaSrc = cms.InputTag("goodSignalMuonsNTupleProducer", "Eta"),
    muPhiSrc = cms.InputTag("goodSignalMuonsNTupleProducer", "Phi"),

    elPtSrc = cms.InputTag("goodSignalElectronsNTupleProducer", "Pt"),
    elEtaSrc = cms.InputTag("goodSignalElectronsNTupleProducer", "Eta"),
    elPhiSrc = cms.InputTag("goodSignalElectronsNTupleProducer", "Phi"),

    bjPtSrc = cms.InputTag("highestBTagJetNTupleProducer", "Pt"),
    bjEtaSrc = cms.InputTag("highestBTagJetNTupleProducer", "Eta"),
    bjPhiSrc = cms.InputTag("highestBTagJetNTupleProducer", "Phi"),

    ljPtSrc = cms.InputTag("lowestBTagJetNTupleProducer", "Pt"),
    ljEtaSrc = cms.InputTag("lowestBTagJetNTupleProducer", "Eta"),
    ljPhiSrc = cms.InputTag("lowestBTagJetNTupleProducer", "Phi"),

    nuPtSrc = cms.InputTag("recoNuNTupleProducer", "Pt"),
    nuEtaSrc = cms.InputTag("recoNuNTupleProducer", "Eta"),
    nuPhiSrc = cms.InputTag("recoNuNTupleProducer", "Phi"),
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
        "HLT_IsoMu24_eta2p1_v16",
    ]),
    doCutOnHLT = cms.bool(options.doHLT and options.lepton=="mu"),
    saveHLTVars = cms.bool(options.doControlVars or not options.doHLT)
)

process.HLTele = cms.PSet(
    hltSrc = cms.InputTag("TriggerResults", "", "HLT"),
    hltNames = cms.vstring([
        "HLT_Ele27_WP80_v8",
        "HLT_Ele27_WP80_v9",
        "HLT_Ele27_WP80_v10",
        "HLT_Ele27_WP80_v11",
        ]),
    doCutOnHLT = cms.bool(options.doHLT and options.lepton=="ele"),
    saveHLTVars = cms.bool(options.doControlVars or not options.doHLT)
)

process.finalVars = cms.PSet(
    cosThetaSrc = cms.InputTag("cosTheta", "cosThetaLightJet"),
    nVerticesSrc = cms.InputTag("goodOfflinePVCount"),
    #scaleFactorsSrc = cms.InputTag("bTagWeightProducerNJMT", "scaleFactors")
)

process.pdfWeights = cms.PSet(
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

    lightJetFlavourSrc = cms.InputTag("lowestBTagJetNTupleProducer", "partonFlavour"),
    bJetFlavourSrc = cms.InputTag("highestBTagJetNTupleProducer", "partonFlavour"),

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

def print_process(p):
    for k, v in p.__dict__.items():
        if isinstance(v, cms.PSet):
            print k, v

if __name__=="__main__":
    print_process(process)
