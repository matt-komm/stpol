# This module provides a skim filter based on CMSSW modules.
# Two skimming sequences are provided: electrons and muons.
# mu: looseMuonsSkim -> muonFilterSkim -> looseJetsSkim -> jetFilterSkim
# ele: looseElectronsSkim -> electronFilterSkim -> looseJetsSkim -> jetFilterSkim
import FWCore.ParameterSet.Config as cms
from SingleTopPolarization.Analysis.eventCounting import countInSequence

def skimFilters(process):
    muonMinPt = 20
    muonEtaRange = [-4.5, 4.5]
    muonSource = "muons"
    process.looseMuonsSkim = cms.EDFilter("EtaPtMinCandViewSelector",
    src = cms.InputTag(muonSource),
    ptMin   = cms.double(muonMinPt),
    etaMin = cms.double(min(muonEtaRange)),
    etaMax = cms.double(max(muonEtaRange))
    )

    jetMinPt = 20
    jetEtaRange = [-4.5, 4.5]
    jetSource = "ak5PFJets"
    process.looseJetsSkim = cms.EDFilter("EtaPtMinCandViewSelector",
    src = cms.InputTag(jetSource),
    ptMin   = cms.double(jetMinPt),
    etaMin = cms.double(min(jetEtaRange)),
    etaMax = cms.double(max(jetEtaRange))
    )

    electronMinPt = 20
    electronEtaRange = [-4.5, 4.5]
    electronSource = "gsfElectrons"
    process.looseElectronsSkim = cms.EDFilter("EtaPtMinCandViewSelector",
    src = cms.InputTag(electronSource),
    ptMin   = cms.double(electronMinPt),
    etaMin = cms.double(min(electronEtaRange)),
    etaMax = cms.double(max(electronEtaRange))
    )

    process.muonFilterSkim = cms.EDFilter("PATCandViewCountFilter",
      src = cms.InputTag("looseMuonsSkim"),
      minNumber = cms.uint32(1),
      maxNumber = cms.uint32(9999), #Somehow maxNumber works in PATCandViewCountFilter but not in CandViewCountFilter
    )

    process.jetFilterSkim = cms.EDFilter("PATCandViewCountFilter",
      src = cms.InputTag("looseJetsSkim"),
      minNumber = cms.uint32(2),
      maxNumber = cms.uint32(9999),
    )

    process.electronFilterSkim = cms.EDFilter("PATCandViewCountFilter",
      src = cms.InputTag("looseElectronsSkim"),
      minNumber = cms.uint32(1),
      maxNumber = cms.uint32(9999),
    )

    process.electronVetoFilterSkim = cms.EDFilter("PATCandViewCountFilter",
      src = cms.InputTag("looseElectronsSkim"),
      minNumber = cms.uint32(0),
      maxNumber = cms.uint32(0),
    )

    process.muonVetoFilterSkim = cms.EDFilter("PATCandViewCountFilter",
      src = cms.InputTag("looseMuonsSkim"),
      minNumber = cms.uint32(0),
      maxNumber = cms.uint32(0),
    )

    process.muonSkim = cms.Sequence(
          process.looseMuonsSkim
        * process.muonFilterSkim
        #* process.looseElectronsSkim
        #* process.electronVetoFilterSkim
        * process.looseJetsSkim
        * process.jetFilterSkim
    )
    process.electronSkim = cms.Sequence(
          process.looseElectronsSkim
        * process.electronFilterSkim
        #* process.looseMuonsSkim
        #* process.muonVetoFilterSkim
        * process.looseJetsSkim
        * process.jetFilterSkim
    )

    countInSequence(process, process.muonSkim)
    countInSequence(process, process.electronSkim)
