#from make_file_list import *
import FWCore.ParameterSet.Config as cms
from FWCore.ParameterSet.VarParsing import VarParsing

process = cms.Process("STPOLPDF")

process.load("FWCore.MessageService.MessageLogger_cfi")

process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(-1) )

#filelist = get_file_list()

options = VarParsing('analysis')
options.register ('PowhegTopMassFix', False,
              VarParsing.multiplicity.singleton,
              VarParsing.varType.bool,
              "Apply Powheg scale fix?")
options.parseArguments()

#print "option", options

process.source = cms.Source("PoolSource",
    # replace 'myfile.root' with the source file you want to use
    fileNames = cms.untracked.vstring(
        #filelist
        #'file:/hdfs/cms/store/user/joosep/T_t-channel_TuneZ2star_8TeV-powheg-tauola/Jul8_51f69b/e6cee8f160cb239f414a74aa40d88ea9/output_noSkim_1_1_Nq6.root'
    )
)

process.pdfWeights = cms.EDProducer('PDFWeightProducer',
    PDFSets = cms.vstring([
       'NNPDF23_nlo_as_0119.LHgrid',       
    ]),
    doPowhegTopMassFix=cms.bool(options.PowhegTopMassFix)
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
