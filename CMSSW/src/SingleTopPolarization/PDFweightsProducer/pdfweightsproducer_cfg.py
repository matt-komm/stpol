import FWCore.ParameterSet.Config as cms

process = cms.Process("TEST3")

process.load("FWCore.MessageService.MessageLogger_cfi")

process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(100) )

process.source = cms.Source("PoolSource",
    # replace 'myfile.root' with the source file you want to use
    fileNames = cms.untracked.vstring(
        '/store/user/joosep/TToLeptons_t-channel_8TeV-powheg-tauola/Jul8_51f69b/e6cee8f160cb239f414a74aa40d88ea9/output_noSkim_1_1_YzB.root'
    )
)

process.PDFweigts = cms.EDProducer('PDFweightsProducer',
	PDFSets	= cms.vstring('cteq66.LHgrid','MSTW2008nlo68cl.LHgrid')
)

process.p = cms.Path( process.PDFweigts )


process.out = cms.OutputModule("PoolOutputModule",
    fileName = cms.untracked.string('myOutputFile10_x.root')
)


process.e = cms.EndPath(process.out)
