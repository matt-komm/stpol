from PhysicsTools.PatAlgos.patTemplate_cfg import *
process.load("PhysicsTools.PatAlgos.patSequences_cff")
from PhysicsTools.PatAlgos.tools.pfTools import *

process.options = cms.untracked.PSet(wantSummary=cms.untracked.bool(False))

#No postfix
postfix = ""

jetAlgo="AK5"
usePF2PAT(process,runPF2PAT=True, jetAlgo=jetAlgo, runOnMC=True, postfix=postfix)
process.p = cms.Path(
    getattr(process,"patPF2PATSequence"+postfix)
)
from PhysicsTools.PatAlgos.patEventContent_cff import patEventContentNoCleaning
process.out.outputCommands = cms.untracked.vstring('drop *',
                                                   *patEventContentNoCleaning )

getattr(process,"pfNoPileUp"+postfix).enable = True
getattr(process,"pfNoMuon"+postfix).enable = True
getattr(process,"pfNoElectron"+postfix).enable = True
getattr(process,"pfNoTau"+postfix).enable = False
getattr(process,"pfNoJet"+postfix).enable = True
getattr(process,"pfNoMuon"+postfix).verbose = False
getattr(process,"pfIsolatedMuons"+postfix).doDeltaBetaCorrection = False
process.source.fileNames = ["/store/mc/Summer12_DR53X/T_t-channel_TuneZ2star_8TeV-powheg-tauola/AODSIM/PU_S10_START53_V7A-v1/0000/0059C6F3-7CDC-E111-B4CB-001A92811726.root"]
process.maxEvents.input = 100
process.out.fileName = 'patTuple_PF2PAT.root'

#use unisolated candidates
process.patMuons.pfMuonSource = cms.InputTag("pfMuons")
process.muonMatch.src = cms.InputTag("pfMuons")
process.patElectrons.pfElectronSource = cms.InputTag("pfElectrons")
#process.electronMatch.src = cms.InputTag("pfElectrons")
