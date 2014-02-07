import FWCore.ParameterSet.Config as cms

def HLTSetup(process, conf):
    import HLTrigger.HLTfilters.triggerResultsFilter_cfi as HLT

    process.HLTprefilter = HLT.triggerResultsFilter.clone(
            hltResults = cms.InputTag( "TriggerResults","","HLT"),
            l1tResults = '',
            throw = False
            )

    process.HLTprefilter.triggerConditions = ["HLT_IsoMu24_eta2p1_v* OR HLT_Ele27_WP80_v*"]
