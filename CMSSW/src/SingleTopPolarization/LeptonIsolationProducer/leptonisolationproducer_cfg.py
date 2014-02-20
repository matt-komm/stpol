import FWCore.ParameterSet.Config as cms

process = cms.Process("OWNPARTICLES")

process.load("FWCore.MessageService.MessageLogger_cfi")

process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(-1) )

process.source = cms.Source("PoolSource",
    # replace 'myfile.root' with the source file you want to use
    fileNames = cms.untracked.vstring(
        'file:myfile.root'
    )
)

# process.eventsWithMuon = cms.EDFilter(
#     "PATCandViewCountFilter",
#     src = cms.InputTag("looseVetoMuons"),
#     minNumber = cms.uint32(1),
#     maxNumber = cms.uint32(999),
# )

process.muonsWithIso = cms.EDProducer(
	'MuonIsolationProducer',
	leptonSrc = cms.InputTag("looseVetoMuons"),
	rhoSrc = cms.InputTag("kt6PFJets", "rho")
)

process.trees1 = cms.EDAnalyzer('MuonCandViewTreemakerAnalyzer',
	makeTree = cms.untracked.bool(True),
	treeName = cms.untracked.string("eventTree"),
	collections = cms.untracked.VPSet(
		cms.untracked.PSet(
			collection = cms.untracked.string("muonsWithIso"),
			maxElems = cms.untracked.int32(1),
			variables = cms.untracked.VPSet(
				cms.untracked.PSet(
					tag = cms.untracked.string("Pt"),
					expr = cms.untracked.string("pt")
				), 
				cms.untracked.PSet(
					tag = cms.untracked.string("Eta"),
					expr = cms.untracked.string("eta")
				),
				cms.untracked.PSet(
					tag = cms.untracked.string("Phi"),
					expr = cms.untracked.string("phi")
				),
				cms.untracked.PSet(
					tag = cms.untracked.string("deltaBetaCorrRelIso"),
					expr = cms.untracked.string("userFloat('deltaBetaCorrRelIso')")
				),
				cms.untracked.PSet(
					tag = cms.untracked.string("rhoCorrRelIso"),
					expr = cms.untracked.string("userFloat('rhoCorrRelIso')")
				),
			)
		),
	)
)


process.out = cms.OutputModule("PoolOutputModule",
    fileName = cms.untracked.string('myOutputFile.root')
)

process.TFileService = cms.Service(
    "TFileService",
    fileName = cms.string("test_trees.root"),
)

from SingleTopPolarization.Analysis.cmdlineParsing import enableCommandLineArguments
enableCommandLineArguments(process)

process.p = cms.Path(
	#process.eventsWithMuon *
	process.muonsWithIso *
	process.trees1
)

process.e = cms.EndPath(process.out)
