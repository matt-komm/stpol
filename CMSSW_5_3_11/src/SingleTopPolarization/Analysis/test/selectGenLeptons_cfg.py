import FWCore.ParameterSet.Config as cms

process = cms.Process("test")

process.load("FWCore.MessageLogger.MessageLogger_cfi")
process.MessageLogger = cms.Service("MessageLogger",
       destinations=cms.untracked.vstring(
                                              'cout',
                    ),
       cout=cms.untracked.PSet(
        threshold=cms.untracked.string('DEBUG')
        ),
)
process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(-1) )

process.source = cms.Source("PoolSource",
    fileNames = cms.untracked.vstring(""
    )
)

#Command-line arguments
from SingleTopPolarization.Analysis.cmdlineParsing import enableCommandLineArguments
enableCommandLineArguments(process)

process.genLeptons = cms.EDFilter("CandViewSelector",
    src=cms.InputTag("genParticles"),
    cut=cms.string(
        #Consider muons or electrons
        "(abs(pdgId()) == 13 || abs(pdgId()) == 11 ) \
         && abs((mother().pdgId()))==24" #The first mother is the "oldest" particle. In our case, we are looking for a top quark
    )
)

process.load("SimGeneral.HepPDTESSource.pythiapdt_cfi")

process.printDecay = cms.EDAnalyzer(
    "ParticleDecayDrawer",
    src = cms.InputTag("genParticles"),
    printP4 = cms.untracked.bool(False),
    printPtEtaPhi = cms.untracked.bool(False),
    printVertex = cms.untracked.bool(False)
)

process.genLeptonAnalyzer = cms.EDAnalyzer("SimpleEventAnalyzer",
    interestingCollections=cms.untracked.VInputTag("genLeptons")
)

process.p = cms.Path(process.printDecay * process.genLeptons * process.genLeptonAnalyzer)
