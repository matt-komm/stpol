import FWCore.ParameterSet.Config as cms

process = cms.Process("TEST3")

process.load("FWCore.MessageService.MessageLogger_cfi")

process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(10) )

process.source = cms.Source("PoolSource",
    # replace 'myfile.root' with the source file you want to use
    fileNames = cms.untracked.vstring(
        'file:/hdfs/cms/store/user/jpata/TTJets_MassiveBinDECAY_TuneZ2star_8TeV-madgraph-tauola/stpol_Feb8_FastSimValidation_v2_FSIM/243fe90abe1b1cf7bc2119dc7c0b2e28/output_Skim_noSlim_99_2_aN4.root'
    )
)

process.PDFweigts = cms.EDProducer('PDFweightsProducer',
	PDFSets				=	cms.vstring('cteq66.LHgrid','MSTW2008nlo68cl.LHgrid') #ok
)

process.p = cms.Path( process.PDFweigts )


process.out = cms.OutputModule("PoolOutputModule",
    fileName = cms.untracked.string('myOutputFile10_x.root')
)


process.e = cms.EndPath(process.out)
