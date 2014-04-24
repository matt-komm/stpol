import FWCore.ParameterSet.Config as cms

process = cms.Process("OWNPARTICLES")

process.load("FWCore.MessageService.MessageLogger_cfi")

process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(100) )

process.source = cms.Source("PoolSource",
    # replace 'myfile.root' with the source file you want to use
    fileNames = cms.untracked.vstring(
        'file:/hdfs/cms/store/user/joosep/T_t-channel_TuneZ2star_8TeV-powheg-tauola/Jul8_51f69b/e6cee8f160cb239f414a74aa40d88ea9/output_noSkim_1_1_Nq6.root'
    )
)

process.pdfWeights = cms.EDProducer('PDFWeightProducer',
    PDFSets = cms.vstring([
       #'cteq66.LHgrid',
       #'MSTW2008nlo68cl.LHgrid',
       #'NNPDF21_100.LHgrid',
       'CT10.LHgrid',
       'MSTW2008nlo68cl.LHgrid'
    ]),
    doPowhegTopMassFix=cms.bool(True)
)

process.out = cms.OutputModule("PoolOutputModule",
    fileName = cms.untracked.string('myOutputFile.root'),
    outputCommands = cms.untracked.vstring([
        "drop *",
        "keep *_pdfWeights_*_*"
        ]
    )
)


process.p = cms.Path(process.pdfWeights)

process.e = cms.EndPath(process.out)
