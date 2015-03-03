import FWCore.ParameterSet.Config as cms

process = cms.Process('PAT')
process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(20)
)
process.options = cms.untracked.PSet( wantSummary = cms.untracked.bool(True))

process.source = cms.Source("PoolSource",
    fileNames = cms.untracked.vstring(
        '/store/generator/Summer12/WJetsToLNu_scaledown_8TeV-madgraph-tauola/GEN/START52_V9-v2/0001/020F0C81-B5A5-E111-A51A-0025901D625A.root'
    )
)
'''

process.source = cms.Source("PoolSource",
    #fileNames = cms.untracked.vstring('root://xrootd.unl.edu//store/mc/Summer12_DR53X/TTJets_FullLeptMGDecays_8TeV-madgraph/AODSIM/PU_S10_START53_V7A-v2/00000/000C5D15-AB1A-E211-8BDE-00215E22053A.root'),
    fileNames = cms.untracked.vstring('root://xrootd.unl.edu//store/mc/Summer12_DR53X/TTJets_SemiLeptMGDecays_8TeV-madgraph/AODSIM/PU_S10_START53_V7A-v1/00000/00144C5F-1114-E211-BCF9-001E67397CC9.root'),
    #fileNames = cms.untracked.vstring('root://xrootd.unl.edu//store/mc/Summer12_DR53X/TTJets_MassiveBinDECAY_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V7A-v1/0000/001C868B-B2E1-E111-9BE3-003048D4DCD8.root'),
)
'''

# Output definition

process.load('SimGeneral.HepPDTESSource.pythiapdt_cfi')
process.prunedGenParticles = cms.EDProducer("GenParticlePruner",
    src=cms.InputTag("genParticles"),
    select=cms.vstring(
        "drop  *",
        "keep status = 3", #keeps all particles from the hard matrix element
        "+keep abs(pdgId) = 15 & status = 1" #keeps intermediate decaying tau
        )
    )
    

process.pat2pxlio=cms.EDAnalyzer('EDM2PXLIO',
    SelectEventsFromProcess=cms.vstring("USER"),  
    SelectEventsFromPath = cms.vstring("p0"),
    OutFileName=cms.untracked.string("wjets.pxlio"),
    process=cms.untracked.string("test"),
    
    genCollection = cms.PSet(
        type=cms.string("GenParticle2Pxlio"),
        srcs=cms.VInputTag(cms.InputTag("prunedGenParticles")),
        EventInfo=cms.InputTag('generator')
    ),
    
    genJets = cms.PSet(
        type=cms.string("GenJet2Pxlio"),
        srcs=cms.VInputTag("ak5GenJets","kt4GenJets","kt6GenJets"),
        names=cms.vstring("AK5GenJets","KT4GenJets","KT6GenJets")
    ),
    
    q2weights = cms.PSet(
        type=cms.string("ValueList2Pxlio"),
        srcs=cms.VInputTag(
            cms.InputTag("extraPartons","nExtraPartons"),
        ),
        names = cms.vstring("nExtraPartons")
    )
    
    
)


process.extraPartons = cms.EDProducer('ExtraPartonCounter'
)


process.out = cms.OutputModule("PoolOutputModule",
        fileName = cms.untracked.string("test.root")
)


process.p0 = cms.Path(process.prunedGenParticles*process.extraPartons)
process.pxlioOut=cms.EndPath(process.out*process.pat2pxlio)

