from FWCore.ParameterSet.VarParsing import VarParsing
import FWCore.ParameterSet.Config as cms

def enableCommandLineArguments(process):
    options = VarParsing('analysis')
    options.parseArguments()
    # if options.outputFile=="":
    # 	options.outputFile = "out_%s.root" % process.name_()
    # print "output: %s" % options.outputFile
    process.source.fileNames = cms.untracked.vstring(options.inputFiles)
    process.maxEvents = cms.untracked.PSet(
      input = cms.untracked.int32(options.maxEvents)
    )
    if hasattr(process, "out"):
    	process.out.fileName = cms.untracked.string(options.outputFile)
    return (options.inputFiles, options.outputFile)
