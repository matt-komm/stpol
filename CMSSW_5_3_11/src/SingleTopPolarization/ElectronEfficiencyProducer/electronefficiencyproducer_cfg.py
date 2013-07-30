import FWCore.ParameterSet.Config as cms

process = cms.Process("OWNPARTICLES")

process.load("FWCore.MessageService.MessageLogger_cfi")

process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(-1) )

process.source = cms.Source("PoolSource",
    # replace 'myfile.root' with the source file you want to use
    fileNames = cms.untracked.vstring(
        'file:/hdfs/cms/store/user/joosep/T_t-channel_TuneZ2star_8TeV-powheg-tauola/stpol_step1B/7dee8f5886a058feb3a776faa931adee/output_120_1_ITF.root'
    )
)

process.myProducerLabel = cms.EDProducer('ElectronEfficiencyProducer'
)

process.out = cms.OutputModule("PoolOutputModule",
    fileName = cms.untracked.string('myOutputFile.root')
)

  
process.p = cms.Path(process.myProducerLabel)

process.e = cms.EndPath(process.out)
