## import skeleton process
from PhysicsTools.PatAlgos.patTemplate_cfg import *

# load the PAT config
process.load("PhysicsTools.PatAlgos.patSequences_cff")
process.options   = cms.untracked.PSet( wantSummary = cms.untracked.bool(False) )

from PhysicsTools.PatAlgos.tools.pfTools import *

postfix = ""
jetAlgo="AK5"
usePF2PAT(process,runPF2PAT=True, jetAlgo=jetAlgo, runOnMC=True, postfix=postfix)

process.source.fileNames = [
"/store/mc/Summer12_DR53X/T_t-channel_TuneZ2star_8TeV-powheg-tauola/AODSIM/PU_S10_START53_V7A-v1/0000/0059C6F3-7CDC-E111-B4CB-001A92811726.root"
]


process.maxEvents.input = 10
process.out.fileName = 'patTuple_PF2PAT.root'

# Let it run
process.p = cms.Path(
    getattr(process,"patPF2PATSequence"+postfix)
)

process.out.outputCommands = cms.untracked.vstring([
    #'keep *',
    'drop *',

    'keep edmMergeableCounter_*_*_*', # Keep the lumi-block counter information
    'keep edmTriggerResults_TriggerResults__HLT', #Keep the trigger results
    'keep recoGenParticles_genParticles__SIM', #keep all the genParticles
    'keep recoVertexs_offlinePrimaryVertices__RECO', #keep the offline PV-s

    # Jets
    'keep patJets_selectedPatJets__PAT',
    'keep double_*_rho_RECO', #For rho-corr rel iso
    'keep recoGenJets_selectedPatJets_genJets_PAT', #For Jet MC smearing we need to keep the genJets
    "keep *_puJetId_*_*", # input variables
    "keep *_puJetMva_*_*", # final MVAs and working point flags

    # Muons
    'keep patMuons_selectedPatMuons__PAT',

    # Electrons
    'keep patElectrons_selectedPatElectrons__PAT',

    # METs
    'keep patMETs_patMETs__PAT',

    #ECAL laser corr filter
    'keep bool_ecalLaserCorrFilter__PAT',

    #For flavour analyzer
    'keep GenEventInfoProduct_generator__SIM',

    #PU info
    'keep PileupSummaryInfos_addPileupInfo__HLT',

    #PFCandidates
    'keep recoPFCandidates_*_pfCandidates_PAT',
    'keep recoPFMETs_pfMET__PAT',
    'keep recoPFMETs_pfMet__RECO',
    'keep recoGenMETs_genMetTrue__SIM',
    #'keep recoPFCandidateedmPtredmValueMap_particleFlow_*_RECO',
    'keep recoPFCandidates_particleFlow__RECO',
    'keep recoConversions_allConversions__RECO',
    'keep recoVertexCompositeCandidates_generalV0Candidates_*_RECO',
    'keep recoTracks_generalTracks__RECO',
    'keep recoBeamSpot_offlineBeamSpot__RECO',
    'keep recoMuons_muons__RECO',
])
