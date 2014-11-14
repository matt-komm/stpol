import FWCore.ParameterSet.Config as cms

process = cms.Process("OWNPARTICLES")

process.load("FWCore.MessageService.MessageLogger_cfi")

process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(-1) )

process.source = cms.Source("PoolSource",
    # replace 'myfile.root' with the source file you want to use
    fileNames = cms.untracked.vstring(
         "root://xrootd.unl.edu//store/mc/Summer12_DR53X/TToLeptons_t-channel_8TeV-powheg-tauola/AODSIM/PU_S10_START53_V7A-v1/0000/0034258A-D7DE-E111-BEE3-00261834B529.root"
    
    )
)
process.load('SimGeneral.HepPDTESSource.pythiapdt_cfi')
process.prunedGenParticles = cms.EDProducer("GenParticlePruner",
    src=cms.InputTag("genParticles"),
    select=cms.vstring(
        "drop  *",
        "keep status = 3", #keeps all particles from the hard matrix element
        "keep abs(pdgId) = 15 & status = 1" #keeps intermediate decaying tau
    )
)


process.genParticleSelector = cms.EDProducer('GenParticleSelectorPowheg',
    src=cms.InputTag("genParticles"),
)

process.lightQuarkMatch = cms.EDProducer('GenJetLightQuarkMatcher',
    trueLightQuark=cms.InputTag("genParticleSelector","trueLightJet"),
    genJets=cms.InputTag("ak5GenJets")
)

process.pat2pxlio=cms.EDAnalyzer('EDM2PXLIO',
    OutFileName=cms.untracked.string("data.pxlio"),
    process=cms.untracked.string("tChannel"),
    
    SelectEvents=cms.untracked.VPSet(
        cms.untracked.PSet(
            process=cms.untracked.string("OWNPARTICLES"),
            paths=cms.untracked.vstring("p0"),
        )
    ),
    
    genCollection = cms.PSet(
        type=cms.string("GenParticle2Pxlio"),
        srcs=cms.VInputTag(cms.InputTag("prunedGenParticles")),
        targetEventViews=cms.vstring("PrunedGen"),
        EventInfo=cms.InputTag('generator')
    ),
    
    selectedGenCollection = cms.PSet(
        type=cms.string("GenParticle2Pxlio"),
        srcs=cms.VInputTag(
            cms.InputTag("genParticleSelector","trueTop"),
            cms.InputTag("genParticleSelector","trueLightJet"),
            cms.InputTag("genParticleSelector","trueLepton"),
            cms.InputTag("genParticleSelector","trueNeutrino"),
            cms.InputTag("genParticleSelector","trueWboson"),
        ),
        names=cms.vstring(
            "trueTop",
            "trueLightJet",
            "trueLepton",
            "trueNeutrino",
            "trueWboson",
        ),
        useNameDB=cms.bool(False),
        targetEventViews=cms.vstring("SelectedGen"),
    ),
    
    matchedDRJet= cms.PSet(
        type=cms.string("Candidate2Pxlio"),
        srcs=cms.VInputTag(cms.InputTag("lightQuarkMatch","dRMatch"))
    
    ),
    
    genJets = cms.PSet(
        type=cms.string("GenJet2Pxlio"),
        srcs=cms.VInputTag("ak5GenJets",cms.InputTag("lightQuarkMatch","lightDecayingJets")),#,"kt4GenJets","kt6GenJets"),
        names=cms.vstring("AK5GenJets","LQDecay"), #,"KT4GenJets","KT6GenJets"),
        targetEventViews=cms.vstring("GenJets")
    ),
    
    
    
    
    
    #triggerRegex=cms.vstring("HLT_Mu","HLT_IsoMu","HLT_Ele")
)

  
process.p0 = cms.Path(process.prunedGenParticles*process.genParticleSelector*process.lightQuarkMatch)

process.e = cms.EndPath(process.pat2pxlio)
