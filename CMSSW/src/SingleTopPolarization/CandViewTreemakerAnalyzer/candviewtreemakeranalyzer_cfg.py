import FWCore.ParameterSet.Config as cms

process = cms.Process("TREEMAKER")

process.load("FWCore.MessageLogger.MessageLogger_cfi")
process.MessageLogger = cms.Service("MessageLogger",
       destinations=cms.untracked.vstring('cout'),
       debugModules=cms.untracked.vstring('*'),
       cout=cms.untracked.PSet(threshold=cms.untracked.string('DEBUG')),
)
process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(-1) )

process.source = cms.Source("PoolSource",
    # replace 'myfile.root' with the source file you want to use
    fileNames = cms.untracked.vstring(
    	""
    )
)

process.trees1 = cms.EDAnalyzer('CandViewTreemakerAnalyzer',
	makeTree = cms.untracked.bool(True),
	treeName = cms.untracked.string("eventTree"),
	collections = cms.untracked.VPSet(
		cms.untracked.PSet(
			collection = cms.untracked.string("goodMuons"),
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
			)
		),
		cms.untracked.PSet(
			collection = cms.untracked.string("goodJets"),
			maxElems = cms.untracked.int32(2),
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
			)
		),
	)
)
process.trees2 = cms.EDAnalyzer('JetViewTreemakerAnalyzer',
	makeTree = cms.untracked.bool(True),
	treeName = cms.untracked.string("eventTree"),
	collections = cms.untracked.VPSet(
		cms.untracked.PSet(
			collection = cms.untracked.string("bTagsTCHPT"),
			maxElems = cms.untracked.int32(2),
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
					tag = cms.untracked.string("bTag"),
					expr = cms.untracked.string("bDiscriminator('default')")
				),
			)
		),
	)
)

process.treesDouble = cms.EDAnalyzer("DoubleTreemakerAnalyzer",
	collections = cms.VInputTag(cms.InputTag("cosThetaProducer", "cosThetaLightJet"), cms.InputTag("muAndMETMT", ""))
)

process.TFileService = cms.Service(
    "TFileService",
    fileName = cms.string("trees.root"),
)

process.p = cms.Path(
	#process.trees1 *
	#process.trees2 *
	process.treesDouble
)

from SingleTopPolarization.Analysis.cmdlineParsing import enableCommandLineArguments
enableCommandLineArguments(process)
