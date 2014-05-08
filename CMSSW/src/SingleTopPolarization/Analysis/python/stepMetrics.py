#!/usr/bin/python

#This program analyzes the efficiency of a CMSSW analysis step and calculates the metrics for a grid job configuration

import subprocess
import sys
import ROOT
import time
ROOT.gROOT.SetBatch(True)

stepCfgFile = "$CMSSW_BASE/src/SingleTopPolarization/Analysis/python/selection_step1_cfg.py"
effCalc = "$CMSSW_BASE/src/SingleTopPolarization/Analysis/python/efficiency_step1_cfg.py"
inputRootFile = sys.argv[1]
stepROOTFile = "patTuple.root"
tempSTDOUT = "tempOut.STDOUT"
effROOTFile = "histo.root"
effProcessName = "efficiencyStep1Analyzer"
maxEvents = -1

def call(cmd, retError=False):
    print "Calling external command %s" % cmd
    time0 = time.time()
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output, errors = p.communicate()
    retcode = p.returncode
    if retcode != 0:
        raise Exception("External command '%s' didn't exit successfully: \nSTDOUT\n%s\nSTDERR\n%s" % (cmd, output, errors))
    time1 = time.time()
    elapsedTime = time1-time0
    print "Done in %d seconds" % elapsedTime
    if retError:
        return output, errors
    else:
        return output

def getEventsInPatTuple(fn):
    fileUtilOut = call("edmFileUtil %s" % fn)
    eventsProcessed = long(fileUtilOut.split()[-4])
    fileSize = long(fileUtilOut.split()[-2])
    return eventsProcessed, fileSize

# Calling step
call("cmsRun %s inputFiles=%s maxEvents=%d outputFile=%s &> %s" % (stepCfgFile, inputRootFile, maxEvents, stepROOTFile, tempSTDOUT))
eventsOut, fileSize = getEventsInPatTuple(stepROOTFile)

# Efficiency analyzer
call("cmsRun %s inputFiles=file:%s outputFile=%s > tempEff" % (effCalc, stepROOTFile, effROOTFile))
f = ROOT.TFile(effROOTFile)
eventTime = float(call("grep 'Real/event' %s" % tempSTDOUT).split()[-1])
eventsProcessed = f.Get(effProcessName).Get("totalEventCount").GetBinContent(1)
countHistoNames = [k.GetName() for k in f.Get(effProcessName).GetListOfKeys()]
counts = dict()
for hn in countHistoNames:
    histo = f.Get(effProcessName).Get(hn)
    NBins = histo.GetNbinsX()
    bins = [int(histo.GetBinContent(i)) for i in range(1,NBins+1)]
    counts[hn] = bins
    print "count histogram %s: %s" % (hn, bins)

# Output
print "Output file %s has %d events" % (stepROOTFile, eventsOut)
eventSize = float(fileSize)/float(eventsOut)
print "Event size after slimming: %d b/event" % eventSize
efficiency = 100.0*float(eventsOut) / float(eventsProcessed)
print "Process efficiency: %.2f%% pass this step" % efficiency
eventsPerHour = 3600.0/eventTime
print "This step processes %d events/hour" % eventsPerHour
