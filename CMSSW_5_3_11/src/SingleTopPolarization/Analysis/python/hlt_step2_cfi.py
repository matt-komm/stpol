import FWCore.ParameterSet.Config as cms

def HLTSetup(process, conf):
    import HLTrigger.HLTfilters.triggerResultsFilter_cfi as HLT

    process.stepHLTsyncMu = HLT.triggerResultsFilter.clone(
            hltResults = cms.InputTag( "TriggerResults","","HLT"),
            l1tResults = '',
            throw = False
            )

    process.stepHLTsyncEle = HLT.triggerResultsFilter.clone(
            hltResults = cms.InputTag( "TriggerResults","","HLT"),
            l1tResults = '',
            throw = False
            )

    if conf.filterHLT:
        if conf.useXTrigger:
            process.stepHLTsyncMu.triggerConditions = ["HLT_IsoMu24_eta2p1_v* OR HLT_IsoMu17_eta2p1_CentralPFNoPUJet30_BTagIPIter_v*"]
            process.stepHLTsyncEle.triggerConditions = ["HLT_Ele27_WP80_v* OR HLT_Ele25_CaloIdVT_CaloIsoT_TrkIdT_TrkIsoT_CentralPFNoPUJet30_BTagIPIter_v*"]
        else:
            process.stepHLTsyncMu.triggerConditions = ["HLT_IsoMu24_eta2p1_v*"]
            process.stepHLTsyncEle.triggerConditions = ["HLT_Ele27_WP80_v*"]
    else:
        process.stepHLTsyncMu.triggerConditions = ["HLT_*"]
        process.stepHLTsyncEle.triggerConditions = ["HLT_*"]
