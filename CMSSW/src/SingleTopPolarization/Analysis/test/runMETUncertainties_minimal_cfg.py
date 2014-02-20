#!/usr/bin/python
# -*- coding: utf-8 -*-
import FWCore.ParameterSet.Config as cms

process = cms.Process('RUNMET')

process.load('FWCore.MessageLogger.MessageLogger_cfi')
process.MessageLogger = cms.Service("MessageLogger",
    destinations=cms.untracked.vstring('cout', 'info', 'debug'),
    debugModules=cms.untracked.vstring('*'),
    cout=cms.untracked.PSet(threshold=cms.untracked.string('WARNING')),
    info=cms.untracked.PSet(threshold=cms.untracked.string('INFO')),
    debug=cms.untracked.PSet(threshold=cms.untracked.string('DEBUG')),
)

process.options = cms.untracked.PSet(wantSummary=cms.untracked.bool(False))

process.source = cms.Source('PoolSource',
                            fileNames=cms.untracked.vstring()
)

process.maxEvents = cms.untracked.PSet(input=cms.untracked.int32(100)
)

process.out = cms.OutputModule('PoolOutputModule',
                               fileName=cms.untracked.string('patTuple.root'
                               ),
                               SelectEvents=cms.untracked.PSet(SelectEvents=cms.vstring('p'
                               )),
                               outputCommands=cms.untracked.vstring('keep *'
                               )
)

process.outpath = cms.EndPath(process.out)

process.source.fileNames = [
    #'file:patTuple_PF2PAT.root',
    'file:sync_step1/sync_T_t_METUnc1_numEvent100_noSkim.root'
]

process.maxEvents.input = 100

process.out.fileName = 'patTuple_PF2PAT1.root'

# process.load("JetMETCorrections.Configuration.JetCorrectionServicesAllAlgos_cff")
#

#
# jetCorr = cms.ESSource(
#    'JetCorrectionService',
#    algorithm = cms.string('AK5PFCHS'),
#
#    ## the 'algorithm' tag is also the name of the DB payload
#    #useCondDB = cms.untracked.bool(True)
# )
# process.load('Configuration.StandardSequences.Services_cff')

process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff'
             )
process.GlobalTag.globaltag = 'START53_V7F::All'
from Configuration.AlCa.autoCond import autoCond
process.GlobalTag.globaltag = cms.string(autoCond['startup'])
process.load('Configuration.StandardSequences.MagneticField_cff')
process.load('Configuration.Geometry.GeometryIdeal_cff')

from PhysicsTools.PatUtils.tools.metUncertaintyTools import runMEtUncertainties
runMEtUncertainties(
    process,
    electronCollection=cms.InputTag('electronsWithID'),
    #electronCollection=cms.InputTag('selectedPatElectrons'),
    photonCollection='',
    muonCollection=cms.InputTag('muonsWithID'),
    #muonCollection=cms.InputTag('selectedPatMuons'),
    tauCollection='',
    jetCollection=cms.InputTag('selectedPatJets'),
    addToPatDefaultSequence=False,
)

process.simpleAnalyzer = cms.EDAnalyzer('SimpleEventAnalyzer',
    interestingCollections=cms.untracked.VInputTag([
        'smearedPatJets',
        'smearedPatJetsResUp',
        'smearedPatJetsResDown',
        'muonsWithID',
        'shiftedMuonsWithIDenDown',
        'shiftedMuonsWithIDenUp',
        'electronsWithID',
        'shiftedElectronsWithIDenDown',
        'shiftedElectronsWithIDenUp',
    ]),
    maxObjects=cms.untracked.uint32(0)
)

# Let it run

process.p = cms.Path(
    process.metUncertaintySequence
    * process.simpleAnalyzer
)
