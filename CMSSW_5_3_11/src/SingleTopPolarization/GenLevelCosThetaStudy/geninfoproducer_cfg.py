import FWCore.ParameterSet.Config as cms

process = cms.Process("GENSTUDY")


from PhysicsTools.JetMCAlgos.SelectPartons_cff import *
from PhysicsTools.JetMCAlgos.IC5CaloJetsMCFlavour_cff import *
from PhysicsTools.JetMCAlgos.AK5CaloJetsMCFlavour_cff import *

process.load("FWCore.MessageLogger.MessageLogger_cfi")
#process.MessageLogger = cms.Service("MessageLogger",
#        destinations=cms.untracked.vstring(
#            'cout',
#            'debug'
#        ),
#        debugModules=cms.untracked.vstring('*'),
#        cout=cms.untracked.PSet(threshold=cms.untracked.string('WARNING')),
#        debug=cms.untracked.PSet(threshold=cms.untracked.string('DEBUG')),
#)

process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(-1)
)

process.source = cms.Source("PoolSource",
    fileNames = cms.untracked.vstring(
        'file:/home/joosep/fromdima/GEN/gen_10018_17635.root'
    )
)


process.myPartons = cms.EDProducer("PartonSelector",
     withLeptons = cms.bool(True),
     src = cms.InputTag("genParticles")
)

process.flavourByRef = cms.EDProducer("JetPartonMatcher",
     jets = cms.InputTag("ak5GenJetsNoNu"),
     coneSizeToAssociate = cms.double(0.3),
     partons = cms.InputTag("myPartons")
)

process.flavourByVal = cms.EDProducer("JetFlavourIdentifier",
     srcByReference = cms.InputTag("flavourByRef"),
     physicsDefinition = cms.bool(False)
 )

process.particleSelector = cms.EDFilter('GenInfoProducer',
    srcSelectedPartons = cms.InputTag("myPartons"),
    srcByValue = cms.InputTag("flavourByVal")
)

lep = cms.InputTag("particleSelector", "selectedLeptons")
bjet = cms.InputTag("particleSelector", "selectedBTagJets")
ljet = cms.InputTag("particleSelector", "selectedLightJets")
process.recoNu = cms.EDProducer('ClassicReconstructedNeutrinoProducer',
    leptonSrc=lep,
    bjetSrc=bjet,
    metSrc=cms.InputTag("particleSelector", "selectedMETs")
)
process.recoTop = cms.EDProducer('SimpleCompositeCandProducer',
    sources=cms.VInputTag([
        "recoNu",
        bjet,
        lep
    ])
)
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
        'keep floats_*_*_*'
    ),
    dropMetaData=cms.untracked.string("DROPPED"),
    splitLevel=cms.untracked.int32(99),
     SelectEvents=cms.untracked.PSet(
         SelectEvents=cms.vstring(["genParticlePath"])
     ),
)

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
process.lightJet = process.btaggedJet.clone(
    src=ljet
)
process.lepton = process.btaggedJet.clone(
    src=lep
)

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
