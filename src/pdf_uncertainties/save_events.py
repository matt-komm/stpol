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


missing_events = set([3002880, 113669, 3741709, 2236942, 2576400, 162326, 3075608, 3934756, 1160230, 3193901, 1670194, 2995763, 2387013, 361040, 1491538, 3419221, 1615961, 365661, 2201697, 1012834, 1728619, 2073200, 993393, 3163250, 2943097, 2777213, 2263168, 3633346, 1569422, 3063441, 1341078, 1162907, 3395295, 2920098, 3272867, 256166, 508906, 2112706, 2588360, 3817166, 1303759, 1887956, 328406, 310487, 2059996, 3197663, 3349223, 2153706, 2737390, 30959, 3191541, 1780470, 3842260, 3748602, 488700, 319746, 2579722, 1671947, 192782, 95504, 2971412, 2400025, 2695966, 867615, 2077659, 408359, 345387, 3060528, 3057458, 2871091, 556852, 2949430, 2655547, 608576, 325441, 1090375, 3073871, 1342802, 3202390, 464728, 694620, 1303907, 1183594, 2230635, 3616624, 492914, 1466741, 3136380, 3355005, 616833, 1310597, 2378049, 2300813, 950161, 2068883, 724884, 2638744, 71070, 2254239, 3207585, 496548, 2391978, 1743294, 3491268, 819654, 2580426, 1675213, 2116048, 2162641, 2622931, 757784, 587733, 1149689, 3279695, 504808, 485866, 3872505, 49646, 3058673, 2636275, 321527, 2591225, 55290, 1491454, 3237375])

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
    if event.bdt_qcd <= 0.4: continue
    extra_data[i] = [event.bdt_qcd, event.bdt_sig_bg, event.xsweight, event.wjets_ct_shape_weight, event.wjets_fl_yield_weight]

i=-1

missing_present = 0

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

    
    """if event.event in missing_events:
        missing_present += 1
        if not i in extra_data:
            print event.event, i in extra_data
        else:
            print event.event, i in extra_data, event.njets, event.ntags, event.n_signal_mu, event.n_signal_ele, event.bjet_pt<= 40, event.ljet_pt <= 40,  abs(event.bjet_eta) >= 4.5, abs(event.ljet_eta) >= 4.5, event.lepton_pt <= 26, event.hlt_mu != 1, event.bjet_dr <= 0.3, event.ljet_pt <= 0.3, "qcd=",extra_data[i][0], math.isnan(event.lepton_weight__id), math.isnan(event.lepton_weight__iso), math.isnan(event.lepton_weight__trigger), math.isnan(event.b_weight)
        #print "info", run in outdata[channel], lumi in outdata[channel][run], eventid in outdata[channel][run][lumi], outdata[channel][run][lumi][eventid], math.isnan(event.lepton_weight__iso), math.isnan(event.lepton_weight__trigger), math.isnan(event.b_weight)
    """
    if not i in extra_data: continue
    
    if event.njets == 2: 
        if event.ntags > 1: continue
    elif event.njets == 3:
        if event.ntags > 2: continue
        if event.ntags < 1: continue
    jt = "%sj%st" % (event.njets, event.ntags)    

    if event.n_signal_mu == 1:
        channel = "mu"
    elif event.n_signal_ele == 1:
        channel = "ele"
    else: continue

    if event.n_veto_mu > 0 or event.n_veto_ele > 0: continue

    if event.bjet_pt <= 40 or event.ljet_pt <= 40: continue
    if abs(event.bjet_eta) >= 4.5 or abs(event.ljet_eta) >= 4.5: continue
    if channel == "mu" and event.lepton_pt <= 26: continue
    if channel == "ele" and event.lepton_pt <= 30: continue
    if channel == "mu" and event.hlt_mu != 1: continue
    if channel == "ele" and event.hlt_ele != 1: continue
    if event.bjet_dr <= 0.3 or event.ljet_pt <= 0.3: continue
    qcd_mva_cut = 0.4
    if channel == "ele":
        qcd_mva_cut = 0.55
    

    qcd_bdt = extra_data[i][0]
    if qcd_bdt <= qcd_mva_cut: continue    
    run = event.run
    lumi = event.lumi
    eventid = event.event    

    if math.isnan(event.lepton_weight__id): continue
    if math.isnan(event.lepton_weight__iso): continue
    if math.isnan(event.lepton_weight__trigger): continue
    #if math.isnan(event.b_weight): continue
    outdatai[channel][i] = True
    if run not in outdata[channel]:
        outdata[channel][run] = dict()
    if lumi not in outdata[channel][run]:
        outdata[channel][run][lumi] = dict()
    outdata[channel][run][lumi][eventid] = True
    
print "missing present", missing_present
print "writing"
path = os.path.join(os.environ["STPOL_DIR"], "src", "pdf_uncertainties", "eventlists")
for channel in channels:
    outfilename = "%s/events_%s_%s_%s.pkl" % (path, channel, dataset, counter)
    outfile = open(outfilename, "wb")    
    pickle.dump(outdata, outfile)    
    pickle.dump(outdatai, outfile)    
    outfile.close()

print "finished"             

        
