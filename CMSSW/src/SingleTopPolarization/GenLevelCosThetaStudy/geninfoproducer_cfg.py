import FWCore.ParameterSet.Config as cms
import sys

process = cms.Process("GENSTUDY")

from PhysicsTools.JetMCAlgos.SelectPartons_cff import *
from PhysicsTools.JetMCAlgos.IC5CaloJetsMCFlavour_cff import *
from PhysicsTools.JetMCAlgos.AK5CaloJetsMCFlavour_cff import *

process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(1000000)
)

process.load("FWCore.MessageLogger.MessageLogger_cfi")
process.MessageLogger.cerr.FwkReport.reportEvery = 1000

process.source = cms.Source("PoolSource",
    fileNames = cms.untracked.vstring()
)
process.source.duplicateCheckMode = cms.untracked.string('noDuplicateCheck')

process.myPartons = cms.EDProducer("PartonSelector",
     withLeptons = cms.bool(True),
     src = cms.InputTag("genParticles")
)

#Match jets to partons
process.flavourByRef = cms.EDProducer("JetPartonMatcher",
     jets = cms.InputTag("ak5GenJets"),
     coneSizeToAssociate = cms.double(0.3),
     partons = cms.InputTag("myPartons")
)

#Generate jets with flavour
process.flavourByVal = cms.EDProducer("JetFlavourIdentifier",
     srcByReference = cms.InputTag("flavourByRef"),
     physicsDefinition = cms.bool(False)
 )

#Select 1 lepton, 2J topology events
process.particleSelector = cms.EDFilter('GenInfoProducer',
    srcSelectedPartons = cms.InputTag("myPartons"),
    srcByValue = cms.InputTag("flavourByVal")
)

lep = cms.InputTag("particleSelector", "selectedLeptons")
bjet = cms.InputTag("particleSelector", "selectedBTagJets")
ljet = cms.InputTag("particleSelector", "selectedLightJets")

#Reconstruct the neutrino
process.recoNu = cms.EDProducer('ClassicReconstructedNeutrinoProducer',
    leptonSrc=lep,
    bjetSrc=bjet,
    metSrc=cms.InputTag("particleSelector", "selectedMETs")
)

#Reconstruct the top using vector addition
process.recoTop = cms.EDProducer('SimpleCompositeCandProducer',
    sources=cms.VInputTag([
        "recoNu",
        bjet,
        lep
    ])
)

#Calculate the angle between the lepton and light jet in the top mass frame
process.cosTheta = cms.EDProducer('CosThetaProducer',
    topSrc=cms.InputTag("recoTop"),
    jetSrc=ljet,
    leptonSrc=lep
)

process.out = cms.OutputModule("PoolOutputModule",
    fileName = cms.untracked.string('myOutputFile.root'),
    outputCommands=cms.untracked.vstring(
        'drop *',
        'keep *_cosTheta_*_*',
        'keep double_particleSelector_*_*',
        'keep floats_*_*_*'
    ),
    dropMetaData=cms.untracked.string("DROPPED"),
    splitLevel=cms.untracked.int32(99),
     SelectEvents=cms.untracked.PSet(
         SelectEvents=cms.vstring(["genParticlePath"])
     ),
)

#Make ntuples
def ntupleCollection(items):
    varVPSet = cms.VPSet()
    for item in items:
        pset = cms.untracked.PSet(
            tag=cms.untracked.string(item[0]),
            quantity=cms.untracked.string(item[1])
        )
        varVPSet.append(pset)
    return varVPSet

process.btaggedJet = cms.EDProducer(
    "CandViewNtpProducer2",
    src=bjet,
    lazyParser = cms.untracked.bool(True),
    prefix = cms.untracked.string(""),
    variables = ntupleCollection(
        [
            ["Pt", "pt"],
            ["Eta", "eta"],
            ["Phi", "phi"],
            ["Mass", "mass"],
            ["pdgId", "pdgId"],
        ]
  )
)
process.lightJet = process.btaggedJet.clone(src=ljet)
process.lepton = process.btaggedJet.clone(src=lep)

process.options = cms.untracked.PSet(wantSummary=cms.untracked.bool(True))

process.genParticlePath = cms.Path(
    process.myPartons *
    process.flavourByRef *
    process.flavourByVal *
    process.particleSelector *
    process.btaggedJet *
    process.lightJet *
    process.lepton *
    process.recoNu *
    process.recoTop *
    process.cosTheta
)

process.e = cms.EndPath(process.out)

#Enable command line args (has to be done at the end to have access to process.source/out)
from SingleTopPolarization.Analysis.cmdlineParsing import enableCommandLineArguments
enableCommandLineArguments(process)
