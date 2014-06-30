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

from get_weights import *
from utils import sizes, pdfs
#from src.qcd_mva.utils import *
#from src.qcd_mva.mva_variables import *
#from Dataset import *


print "args", sys.argv
#system.exit(1)
dataset = sys.argv[1]
thispdf = sys.argv[2]
counter = sys.argv[3]
base_filename = sys.argv[4]
added_filename = sys.argv[5]



variables = ["bdt_sig_bg", "cos_theta"]

ranges = {}
ranges["bdt_sig_bg"] = (30, -1, 1)
ranges["cos_theta"] = (48, -1, 1)

channels = ["mu", "ele"]
jettag = ["2j1t", "2j0t", "3j1t", "3j2t"]
histos = {}

infile =  TFile.Open(base_filename, "read")
infile2 = TFile.Open(added_filename, "read")

events = infile.Get('dataframe')
events2 = infile2.Get('dataframe')

colnames = ["bdt_qcd", "bdt_sig_bg", "xsweight", "wjets_ct_shape_weight", "wjets_fl_yield_weight"]
extra_data = {}

(pdf_weights, average_weights) = get_weights(dataset, thispdf)

#outfilename = "pdftest.root"
#outfile = TFile(outfilename, "RECREATE")

#pdfs = ["MSTW2008nlo68cl", "NNPDF21", "cteq66", "CT10"]
#pdfs = ["NNPDF21", "CT10"]

#"MSTW2008CPdeutnlo68cl"]

histograms = dict()
for c in channels:
    histograms[c] = dict()
    for p in pdfs:
        if not (thispdf == p or (p == 'NNPDF23' and thispdf == "NNPDF23nloas0119LHgrid")): continue
        print "midagi"
        histograms[c][p] = dict()
        for var in variables:
            histograms[c][p][var] = dict()
            for jt in jettag:
                histograms[c][p][var][jt] = dict()
                name = "pdf__%s_%s__%s__%s" % (jt, var, dataset, p)
                histograms[c][p][var][jt]["nominal"] = TH1D(name, name, ranges[var][0], ranges[var][1], ranges[var][2])
                histograms[c][p][var][jt]["nominal"].SetDirectory(0)
                histograms[c][p][var][jt]["nominal"].Sumw2()
                histograms[c][p][var][jt]["weighted"] = []
                #print name, histograms[c][p][var][jt]["nominal"].Integral()
                for i in range(sizes[p]):
                    thisname = name + "_weighted_" + str(i)
                    histograms[c][p][var][jt]["weighted"].append(TH1D(thisname, thisname, ranges[var][0], ranges[var][1], ranges[var][2]))
                    histograms[c][p][var][jt]["weighted"][i].SetDirectory(0)
                    histograms[c][p][var][jt]["weighted"][i].Sumw2()
                
i=-1
for event in events2:
    i+=1
    if event.bdt_qcd2 <= 0.4: continue
    extra_data[i] = [event.bdt_qcd2, event.bdt_sig_bg, event.xsweight, event.wjets_ct_shape_weight, event.wjets_fl_yield_weight]

i=-1
missing = 0
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
    bdt = extra_data[i][1]
    xsweight = extra_data[i][2]
    wjets_shape = extra_data[i][3]
    wjets_yield = extra_data[i][4]
    run = event.run
    lumi = event.lumi
    eventid = event.event    

    total_weight = event.pu_weight * event.lepton_weight__id * event.lepton_weight__iso * event.lepton_weight__trigger \
            * event.b_weight * wjets_shape * wjets_yield * xsweight
    if event.top_weight > 0:
        total_weight *= event.top_weight
    if math.isnan(event.lepton_weight__id): continue
    if math.isnan(event.lepton_weight__iso): continue
    if math.isnan(event.lepton_weight__trigger): continue
    if math.isnan(event.b_weight): continue
    
    #print "weights: ",event.pu_weight, event.lepton_weight__id, event.lepton_weight__iso, event.lepton_weight__trigger, \
    #       event.top_weight, event.b_weight, wjets_shape, wjets_yield, xsweight
    #print run, lumi, eventid
    if not (run in pdf_weights or lumi in pdf_weights[run] or eventid in pdf_weights[run][lumi]):
        missing+=1
        continue
    pdf_stuff = pdf_weights[run][lumi][eventid]

    for (p, w) in pdf_stuff.items():
        if not (thispdf == p or (p == 'NNPDF23' and thispdf == "NNPDF23nloas0119LHgrid")): continue
        if p not in pdfs: continue
        if math.isnan(histograms[channel][p]["bdt_sig_bg"][jt]["nominal"].Integral()): ghts

        histograms[channel][p]["bdt_sig_bg"][jt]["nominal"].Fill(bdt, total_weight)
      
        for j in range(len(w)):
            this_weight = total_weight * w[j]
            if (dataset.startswith("T_t") and not dataset.startswith("T_tW")) or (dataset.startswith("Tbar_t") and not dataset.startswith("Tbar_tW")):
                this_weight /= average_weights[p][j]
            histograms[channel][p]["bdt_sig_bg"][jt]["weighted"][j].Fill(bdt, this_weight)
        
        if bdt < 0.8: continue
        histograms[channel][p]["cos_theta"][jt]["nominal"].Fill(event.cos_theta_lj, total_weight)
        
        for j in range(len(w)):
            this_weight = total_weight * w[j]
            if (dataset.startswith("T_t") and not dataset.startswith("T_tW")) or (dataset.startswith("Tbar_t") and not dataset.startswith("Tbar_tW")):
                this_weight /= average_weights[p][j]
            histograms[channel][p]["cos_theta"][jt]["weighted"][j].Fill(event.cos_theta_lj, this_weight)

print "writing"
path = os.path.join(os.environ["STPOL_DIR"], "src", "pdf_uncertainties", "output")
for channel in channels:
    outfilename = "%s/pdftest_%s_%s_%s_%s.root" % (path, channel, dataset, thispdf, counter)
    outfile = TFile(outfilename, "RECREATE")
    for p in histograms[channel]:
        for var in variables:
            for jt in jettag:
                print p, var, jt
                print histograms[channel][p][var][jt]["nominal"].GetEntries(), histograms[channel][p][var][jt]["nominal"].Integral()
                histograms[channel][p][var][jt]["nominal"].Write()
                for h in histograms[channel][p][var][jt]["weighted"]:
                    print h.Integral()
                    h.Write()
    outfile.Write()
    outfile.Close()
print "missing", missing
print "finished"             

        
