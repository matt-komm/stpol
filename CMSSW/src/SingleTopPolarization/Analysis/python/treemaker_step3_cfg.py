import FWCore.ParameterSet.Config as cms

process = cms.Process("TREEMAKER")

process.load("FWCore.MessageService.MessageLogger_cfi")

process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(-1) )

process.source = cms.Source("PoolSource",
    fileNames = cms.untracked.vstring(
        ""
    )
)

def collection(type, collection_, maxElems_, varlist):
    varVPSet = cms.untracked.VPSet()
    for v in varlist:
        pset = cms.untracked.PSet(tag=cms.untracked.string(v[0]), expr=cms.untracked.string(v[1]), )
        varVPSet.append(pset)
    ret = cms.untracked.PSet(
        collection=cms.untracked.string(collection_),
        maxElems=cms.untracked.int32(maxElems_),
        variables=varVPSet
    )
    return ret

from SingleTopPolarization.Analysis.cmdlineParsing import enableCommandLineArguments
enableCommandLineArguments(process)

# process.treesBJets = cms.EDAnalyzer('JetCandOwnVectorTreemakerAnalyzer',
#         makeTree = cms.untracked.bool(True),
#         treeName = cms.untracked.string("eventTree"),
#         collections = cms.untracked.VPSet(
#                 cms.untracked.PSet(
#                         collection = cms.untracked.string("bTagsTCHPtight"),
#                         maxElems = cms.untracked.int32(1),
#                         variables = cms.untracked.VPSet(
#                                 cms.untracked.PSet(
#                                         tag = cms.untracked.string("Pt"),
#                                         expr = cms.untracked.string("pt")
#                                 ),
#                                 cms.untracked.PSet(
#                                         tag = cms.untracked.string("Eta"),
#                                         expr = cms.untracked.string("eta")
#                                 ),
#                                 cms.untracked.PSet(
#                                         tag = cms.untracked.string("Phi"),
#                                         expr = cms.untracked.string("phi")
#                                 ),
#                                 cms.untracked.PSet(
#                                         tag = cms.untracked.string("bTag"),
#                                         expr = cms.untracked.string("bDiscriminator('trackCountingHighPurBJetTags')")
#                                 ),
#                         )
#                 ),
#         )
# )

# process.treesTop = cms.EDAnalyzer('CompositeCandViewTreemakerAnalyzer',
#         makeTree = cms.untracked.bool(True),
#         treeName = cms.untracked.string("eventTree"),
#         collections = cms.untracked.VPSet(
#                 cms.untracked.PSet(
#                         collection = cms.untracked.string("recoTop"),
#                         maxElems = cms.untracked.int32(1),
#                         variables = cms.untracked.VPSet(
#                                 cms.untracked.PSet(
#                                         tag = cms.untracked.string("Pt"),
#                                         expr = cms.untracked.string("pt")
#                                 ),
#                                 cms.untracked.PSet(
#                                         tag = cms.untracked.string("Eta"),
#                                         expr = cms.untracked.string("eta")
#                                 ),
#                                 cms.untracked.PSet(
#                                         tag = cms.untracked.string("Phi"),
#                                         expr = cms.untracked.string("phi")
#                                 ),
#                                 cms.untracked.PSet(
#                                         tag = cms.untracked.string("Et"),
#                                         expr = cms.untracked.string("et")
#                                 ),
#                                 cms.untracked.PSet(
#                                         tag = cms.untracked.string("topMass"),
#                                         expr = cms.untracked.string("p4().M()")
#                                 ),
#                         )
#                 ),
#         )
# )

# process.treesJets = cms.EDAnalyzer('JetCandViewTreemakerAnalyzer',
#         makeTree = cms.untracked.bool(True),
#         treeName = cms.untracked.string("eventTree"),
#         collections = cms.untracked.VPSet(
#                 cms.untracked.PSet(
#                         collection = cms.untracked.string("goodJets"),
#                         maxElems = cms.untracked.int32(2),
#                         variables = cms.untracked.VPSet(
#                                 cms.untracked.PSet(
#                                         tag = cms.untracked.string("Pt"),
#                                         expr = cms.untracked.string("pt")
#                                 ),
#                                 cms.untracked.PSet(
#                                         tag = cms.untracked.string("Eta"),
#                                         expr = cms.untracked.string("eta")
#                                 ),
#                                 cms.untracked.PSet(
#                                         tag = cms.untracked.string("Phi"),
#                                         expr = cms.untracked.string("phi")
#                                 ),
#                                 cms.untracked.PSet(
#                                         tag = cms.untracked.string("bTag"),
#                                         expr = cms.untracked.string("bDiscriminator('trackCountingHighPurBJetTags')")
#                                 ),
#                         )
#                 ),
#         )
# )

# process.treesMu = cms.EDAnalyzer('MuonCandViewTreemakerAnalyzer',
#         makeTree = cms.untracked.bool(True),
#         treeName = cms.untracked.string("eventTree"),
#         collections = cms.untracked.VPSet(
#                 cms.untracked.PSet(
#                         collection = cms.untracked.string("goodSignalMuons"),
#                         maxElems = cms.untracked.int32(1),
#                         variables = cms.untracked.VPSet(
#                                 cms.untracked.PSet(
#                                         tag = cms.untracked.string("Pt"),
#                                         expr = cms.untracked.string("pt")
#                                 ),
#                                 cms.untracked.PSet(
#                                         tag = cms.untracked.string("Eta"),
#                                         expr = cms.untracked.string("eta")
#                                 ),
#                                 cms.untracked.PSet(
#                                         tag = cms.untracked.string("Phi"),
#                                         expr = cms.untracked.string("phi")
#                                 ),
#                                 cms.untracked.PSet(
#                                         tag = cms.untracked.string("deltaBetaCorrRelIso"),
#                                         expr = cms.untracked.string("userFloat('deltaBetaCorrRelIso')")
#                                 ),
#                                 cms.untracked.PSet(
#                                         tag = cms.untracked.string("dz"),
#                                         expr = cms.untracked.string("userFloat('dz')")
#                                 ),
#                                 cms.untracked.PSet(
#                                         tag = cms.untracked.string("track_hitPattern_trackerLayersWithMeasurement"),
#                                         expr = cms.untracked.string("userFloat('track_hitPattern_trackerLayersWithMeasurement')")
#                                 ),
#                                 cms.untracked.PSet(
#                                         tag = cms.untracked.string("globalTrack_hitPattern_numberOfValidMuonHits"),
#                                         expr = cms.untracked.string("userFloat('globalTrack_hitPattern_numberOfValidMuonHits')")
#                                 ),
#                                 cms.untracked.PSet(
#                                         tag = cms.untracked.string("innerTrack_hitPattern_numberOfValidPixelHits"),
#                                         expr = cms.untracked.string("userFloat('innerTrack_hitPattern_numberOfValidPixelHits')")
#                                 ),
#                         )
#                 ),
#                 cms.untracked.PSet(
#                         collection = cms.untracked.string("goodQCDMuons"),
#                         maxElems = cms.untracked.int32(2),
#                         variables = cms.untracked.VPSet(
#                                 cms.untracked.PSet(
#                                         tag = cms.untracked.string("Pt"),
#                                         expr = cms.untracked.string("pt")
#                                 ),
#                                 cms.untracked.PSet(
#                                         tag = cms.untracked.string("Eta"),
#                                         expr = cms.untracked.string("eta")
#                                 ),
#                                 cms.untracked.PSet(
#                                         tag = cms.untracked.string("Phi"),
#                                         expr = cms.untracked.string("phi")
#                                 ),
#                                 cms.untracked.PSet(
#                                         tag = cms.untracked.string("deltaBetaCorrRelIso"),
#                                         expr = cms.untracked.string("userFloat('deltaBetaCorrRelIso')")
#                                 ),
#                         )
#                 ),
#         )
# )

# process.treesEle = cms.EDAnalyzer('ElectronCandViewTreemakerAnalyzer',
#         makeTree=cms.untracked.bool(True),
#         treeName = cms.untracked.string("eventTree"),
#         collections = cms.untracked.VPSet(
#                 cms.untracked.PSet(
#                         collection = cms.untracked.string("goodSignalElectrons"),
#                         maxElems = cms.untracked.int32(1),
#                         variables = cms.untracked.VPSet(
#                                 cms.untracked.PSet(
#                                         tag = cms.untracked.string("Pt"),
#                                         expr = cms.untracked.string("pt")
#                                 ),
#                                 cms.untracked.PSet(
#                                         tag = cms.untracked.string("Eta"),
#                                         expr = cms.untracked.string("eta")
#                                 ),
#                                 cms.untracked.PSet(
#                                         tag = cms.untracked.string("Phi"),
#                                         expr = cms.untracked.string("phi")
#                                 ),
#                                 cms.untracked.PSet(
#                                         tag = cms.untracked.string("rhoCorrRelIso"),
#                                         expr = cms.untracked.string("userFloat('rhoCorrRelIso')")
#                                 ),
#                         )
#                 ),
#                 cms.untracked.PSet(
#                         collection = cms.untracked.string("goodQCDElectrons"),
#                         maxElems = cms.untracked.int32(2),
#                         variables = cms.untracked.VPSet(
#                                 cms.untracked.PSet(
#                                         tag = cms.untracked.string("Pt"),
#                                         expr = cms.untracked.string("pt")
#                                 ),
#                                 cms.untracked.PSet(
#                                         tag = cms.untracked.string("Eta"),
#                                         expr = cms.untracked.string("eta")
#                                 ),
#                                 cms.untracked.PSet(
#                                         tag = cms.untracked.string("Phi"),
#                                         expr = cms.untracked.string("phi")
#                                 ),
#                                 cms.untracked.PSet(
#                                         tag = cms.untracked.string("rhoCorrRelIso"),
#                                         expr = cms.untracked.string("userFloat('rhoCorrRelIso')")
#                                 ),
#                         )
#                 ),
#         )
# )

process.TFileService = cms.Service(
    "TFileService",
    fileName=cms.string("out_step3_trees.root"),
)

process.p = cms.Path(
		process.treesTop *
        process.treesJets *
        process.treesBJets *
        process.treesMu *
        process.treesEle
)
