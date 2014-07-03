import sys
import os
from array import array
from time import gmtime, strftime
import math
#Monkey-patch the system path to import the stpol header
#sys.path.append(os.path.join(os.environ["STPOL_DIR"], "src/headers"))
#from stpol import stpol, list_methods

import ROOT
from ROOT import TH1D, TFile
#import TMVA
# prepare the FWLite autoloading mechanism
ROOT.gSystem.Load("libFWCoreFWLite.so")
ROOT.AutoLibraryLoader.enable()
from PhysicsTools.PythonAnalysis import *
from DataFormats.FWLite import Events, Handle, Lumis

import pickle

print "args", sys.argv
#system.exit(1)
dataset = sys.argv[1]
counter = sys.argv[2]
base_filename = sys.argv[3]
added_filename = sys.argv[4]



infile =  TFile.Open(base_filename, "read")
infile2 = TFile.Open(added_filename, "read")

events = infile.Get('dataframe')
events2 = infile2.Get('dataframe')

colnames = ["bdt_qcd", "bdt_sig_bg", "xsweight", "wjets_ct_shape_weight", "wjets_fl_yield_weight"]
extra_data = {}
                
i=-1
for event in events2:
    i+=1
    if event.bdt_qcd2 <= 0.4: continue
    extra_data[i] = [event.bdt_qcd2, event.bdt_sig_bg, event.xsweight, event.wjets_ct_shape_weight, event.wjets_fl_yield_weight]

i=-1
missing = 0
outdata = {}
outdata["mu"] = {}
outdata["ele"] = {}
outdatai = {}
outdatai["mu"] = {}
outdatai["ele"] = {}
channels = ["mu", "ele"]
for event in events:
    i+=1
    if not i in extra_data: continue
    
    if event.njets == 2: 
        if event.ntags > 1: continue
    elif event.njets == 3:
        if event.ntags > 2: continue
        if event.ntags < 1: continue
    jt = "%sj%st" % (event.njets, event.ntags)    

    if abs(event.lepton_id) == 13:
        channel = "mu"
    elif abs(event.lepton_id) == 11:
        channel = "ele"
    else: continue

    #if vetomuons > 0 or vetoeles > 0: continue

    if event.bjet_pt < 40 or event.ljet_pt < 40: continue
    if abs(event.bjet_eta) > 4.5 or abs(event.ljet_eta) > 4.5: continue
    if channel == "mu" and event.lepton_pt < 26: continue
    if channel == "ele" and event.lepton_pt < 30: continue
    if channel == "mu" and event.hlt_mu != 1: continue
    if channel == "ele" and event.hlt_ele != 1: continue
    qcd_mva_cut = 0.4
    if channel == "ele":
        qcd_mva_cut = 0.55
    

    qcd_bdt = extra_data[i][0]
    if qcd_bdt < qcd_mva_cut: continue    
    run = event.run
    lumi = event.lumi
    eventid = event.event    

    if math.isnan(event.lepton_weight__id): continue
    if math.isnan(event.lepton_weight__iso): continue
    if math.isnan(event.lepton_weight__trigger): continue
    if math.isnan(event.b_weight): continue
    outdatai[channel][i] = True
    if run not in outdata[channel]:
        outdata[channel][run] = dict()
    if lumi not in outdata[channel][run]:
        outdata[channel][run][lumi] = dict()
    outdata[channel][run][lumi][eventid] = True
    

print "writing"
path = os.path.join(os.environ["STPOL_DIR"], "src", "pdf_uncertainties", "eventlists")
for channel in channels:
    outfilename = "%s/events_%s_%s_%s.pkl" % (path, channel, dataset, counter)
    outfile = open(outfilename, "wb")    
    pickle.dump(outdata, outfile)    
    pickle.dump(outdatai, outfile)    
    outfile.close()

print "finished"             

        
