# prepare the FWLite autoloading mechanism
from PhysicsTools.PythonAnalysis import *
from DataFormats.FWLite import Events, Handle, Lumis

import ROOT
from ROOT import TH1D, TH2D, TFile
ROOT.gSystem.Load("libFWCoreFWLite.so")
ROOT.AutoLibraryLoader.enable()

import sys
import os
from array import array
from time import gmtime, strftime
import math
#Monkey-patch the system path to import the stpol header
#sys.path.append(os.path.join(os.environ["STPOL_DIR"], "src/headers"))
#from stpol import stpol, list_methods




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
channel = sys.argv[4]
base_filename = sys.argv[5]
added_filename = sys.argv[6]

ROOT.TH1.AddDirectory(False)

variables = ["bdt_sig_bg", "cos_theta", "pdfweight"]
variables.extend(["scale", "id1", "id2", "x1", "x2"])

ranges = {}
ranges["bdt_sig_bg"] = (30, -1, 1)
ranges["cos_theta"] = (48, -1, 1)
ranges["pdfweight"] = (100, -200, 200)
ranges["scale"] = (100, 150, 500)
ranges["id1"] = (13, -6.5, 6.5)
ranges["id2"] = (13, -6.5, 6.5)
ranges["x1"] = (25, 0, 1)
ranges["x2"] = (25, 0, 1)

channels = ["mu", "ele"]
jettag = ["2j1t", "2j0t", "3j1t", "3j2t"]
histos = {}

infile =  TFile.Open(base_filename, "read")
infile2 = TFile.Open(added_filename, "read")

events = infile.Get('dataframe')
events2 = infile2.Get('dataframe')

colnames = ["bdt_qcd", "bdt_sig_bg", "xsweight", "wjets_ct_shape_weight", "wjets_fl_yield_weight"]
extra_data = {}

(pdf_weights, average_weights, pdf_input) = get_weights(dataset, thispdf, channel, counter)
maxscale = 200
minscale = 170
maxid = 0
minid = 0
maxx = 0.
minx = 0.

missing_events = set([3002880, 113669, 3741709, 2236942, 2576400, 162326, 3075608, 3934756, 1160230, 3193901, 1670194, 2995763, 2387013, 361040, 1491538, 3419221, 1615961, 365661, 2201697, 1012834, 1728619, 2073200, 993393, 3163250, 2943097, 2777213, 2263168, 3633346, 1569422, 3063441, 1341078, 1162907, 3395295, 2920098, 3272867, 256166, 508906, 2112706, 2588360, 3817166, 1303759, 1887956, 328406, 310487, 2059996, 3197663, 3349223, 2153706, 2737390, 30959, 3191541, 1780470, 3842260, 3748602, 488700, 319746, 2579722, 1671947, 192782, 95504, 2971412, 2400025, 2695966, 867615, 2077659, 408359, 345387, 3060528, 3057458, 2871091, 556852, 2949430, 2655547, 608576, 325441, 1090375, 3073871, 1342802, 3202390, 464728, 694620, 1303907, 1183594, 2230635, 3616624, 492914, 1466741, 3136380, 3355005, 616833, 1310597, 2378049, 2300813, 950161, 2068883, 724884, 2638744, 71070, 2254239, 3207585, 496548, 2391978, 1743294, 3491268, 819654, 2580426, 1675213, 2116048, 2162641, 2622931, 757784, 587733, 1149689, 3279695, 504808, 485866, 3872505, 49646, 3058673, 2636275, 321527, 2591225, 55290, 1491454, 3237375])

#outfilename = "pdftest.root"
#outfile = TFile(outfilename, "RECREATE")

#pdfs = ["MSTW2008nlo68cl", "NNPDF21", "cteq66", "CT10"]
#pdfs = ["NNPDF21", "CT10"]

#"MSTW2008CPdeutnlo68cl"]

histograms = dict()

c = channel

luminosity  = 19764
if channel == "ele":
    luminosity = 19820
    


#epath = os.path.join(os.environ["STPOL_DIR"], "src", "pdf_uncertainties", "output_events_new")
#efname = "%s/eventlist_%s_%s_%s_%s.txt" % (epath, channel, dataset, thispdf, counter)
#ef = open(efname, 'w')

histograms[c] = dict()
for p in pdfs:
        if not (thispdf == p or (p == 'NNPDF23' and thispdf == "NNPDF23nloas0119LHgrid")): continue
        print "midagi"
        histograms[c][p] = dict()
        for var in variables:
            histograms[c][p][var] = dict()
            histograms[c][p]["id1id2"] = dict()
            for jt in jettag:
                histograms[c][p][var][jt] = dict()
                histograms[c][p]["id1id2"][jt] = dict()
                name = "pdf__%s_%s__%s__%s" % (jt, var, dataset, p)
                if not var in ["scale", "id1", "id2", "x1", "x2"]:
                    histograms[c][p][var][jt]["nominal"] = TH1D(name+"_nominal", name+"_nominal", ranges[var][0], ranges[var][1], ranges[var][2])
                    histograms[c][p][var][jt]["nominal"].SetDirectory(0)
                    histograms[c][p][var][jt]["nominal"].Sumw2()
                    histograms[c][p][var][jt]["weighted"] = []
                    #print name, histograms[c][p][var][jt]["nominal"].Integral()
                if var == "pdfweight":
                    for mybin in range(ranges["cos_theta"][0]):
                        histograms[c][p]["pdfweight"][jt]["nominal_bin"+str(mybin)] = TH1D(name+"_nominal_bin"+str(mybin), name+"_nominal_bin"+str(mybin), ranges["pdfweight"][0], ranges["pdfweight"][1], ranges["pdfweight"][2])
                        histograms[c][p]["pdfweight"][jt]["nominal_bin"+str(mybin)].SetDirectory(0)
                        histograms[c][p]["pdfweight"][jt]["nominal_bin"+str(mybin)].Sumw2()
                                        
                for i in range(sizes[p]):
                    if var == "pdfweight": continue
                    if var in ["scale", "id1", "id2", "x1", "x2"]: continue
                    thisname = name + "_weighted_" + str(i)
                    histograms[c][p][var][jt]["weighted"].append(TH1D(thisname, thisname, ranges[var][0], ranges[var][1], ranges[var][2]))
                    #print c, p, var, jt, i, len(histograms[c][p][var][jt]["weighted"]), histograms[c][p][var][jt]["weighted"][i]
                    #print histograms[c][p][var][jt]["weighted"][i].GetEntries()
                    histograms[c][p][var][jt]["weighted"][i].SetDirectory(0)
                    histograms[c][p][var][jt]["weighted"][i].Sumw2()
                if var in ["scale", "id1", "id2", "x1", "x2"]:
                    histograms[c][p][var][jt]["nobdtcut"] = TH1D(name, name, ranges[var][0], ranges[var][1], ranges[var][2])
                    histograms[c][p][var][jt]["final"] = TH1D(name+"_final", name+"_final", ranges[var][0], ranges[var][1], ranges[var][2]) 
                    histograms[c][p][var][jt]["nobdtcut_strange"] = TH1D(name+"_strange", name+"_strange", ranges[var][0], ranges[var][1], ranges[var][2])
                    histograms[c][p][var][jt]["final_strange"] = TH1D(name+"_final_strange", name+"_final_strange", ranges[var][0], ranges[var][1], ranges[var][2]) 
                    histograms[c][p][var][jt]["final_strange_plus"] = TH1D(name+"_final_strange_plus", name+"_final_strange_plus", ranges[var][0], ranges[var][1], ranges[var][2]) 
                    histograms[c][p][var][jt]["final_strange_minus"] = TH1D(name+"_final_strange_minus", name+"_final_strange_minus", ranges[var][0], ranges[var][1], ranges[var][2]) 
                    histograms[c][p][var][jt]["final_strange_plusminus"] = TH1D(name+"_final_strange_plusminus", name+"_final_strange_plusminus", ranges[var][0], ranges[var][1], ranges[var][2])
                    #histograms[c][p][var][jt]["final_strange_bin11"] = TH1D(name+"_final_strange_bin11", name+"_final_strange_bin11", ranges[var][0], ranges[var][1], ranges[var][2])
                    #histograms[c][p][var][jt]["final_strange_bin12"] = TH1D(name+"_final_strange_bin12", name+"_final_strange_bin12", ranges[var][0], ranges[var][1], ranges[var][2])

                name = "pdf__%s_%s__%s__%s" % (jt, "id1id2", dataset, p)
                histograms[c][p]["id1id2"][jt]["nobdtcut"] = TH2D(name, name, ranges["id1"][0], ranges["id1"][1], ranges["id1"][2], ranges["id1"][0], ranges["id1"][1], ranges["id1"][2])
                histograms[c][p]["id1id2"][jt]["final"] = TH2D(name+"_final", name+"_final", ranges["id1"][0], ranges["id1"][1], ranges["id1"][2], ranges["id1"][0], ranges["id1"][1], ranges["id1"][2])
                histograms[c][p]["id1id2"][jt]["nobdtcut_strange"] = TH2D(name+"_strange", name+"_strange", ranges["id1"][0], ranges["id1"][1], ranges["id1"][2], ranges["id1"][0], ranges["id1"][1], ranges["id1"][2])
                histograms[c][p]["id1id2"][jt]["final_strange"] = TH2D(name+"_final_strange", name+"_final_strange", ranges["id1"][0], ranges["id1"][1], ranges["id1"][2], ranges["id1"][0], ranges["id1"][1], ranges["id1"][2])
                histograms[c][p]["id1id2"][jt]["final_strange_plus"] = TH2D(name+"_final_strange_plus", name+"_final_strange_plus", ranges["id1"][0], ranges["id1"][1], ranges["id1"][2], ranges["id1"][0], ranges["id1"][1], ranges["id1"][2])
                histograms[c][p]["id1id2"][jt]["final_strange_minus"] = TH2D(name+"_final_strange_minus", name+"_final_strange_minus", ranges["id1"][0], ranges["id1"][1], ranges["id1"][2], ranges["id1"][0], ranges["id1"][1], ranges["id1"][2])
                histograms[c][p]["id1id2"][jt]["final_strange_plusminus"] = TH2D(name+"_final_strange_plusminus", name+"_final_strange_plusminus", ranges["id1"][0], ranges["id1"][1], ranges["id1"][2], ranges["id1"][0], ranges["id1"][1], ranges["id1"][2])
                histograms[c][p]["id1id2"][jt]["final_strange_bin9"] = TH2D(name+"_final_strange_bin9", name+"_final_strange_bin9", ranges["id1"][0], ranges["id1"][1], ranges["id1"][2], ranges["id1"][0], ranges["id1"][1], ranges["id1"][2])

path = os.path.join(os.environ["STPOL_DIR"], "src", "pdf_uncertainties", "eventlists")
picklename = "%s/events_%s_%s_%s.pkl" % (path, channel, dataset, counter)
with open(picklename, 'rb') as f:
    outdata = pickle.load(f)
    outdatai = pickle.load(f)

       
i=-1
for event in events2:
    i+=1
    if event.bdt_qcd <= 0.4: continue
    extra_data[i] = [event.bdt_qcd, event.bdt_sig_bg, event.xsweight, event.wjets_ct_shape_weight, event.wjets_fl_yield_weight]

i=-1
missing = 0
asd = 0
qw = 0
for event in events:
    i+=1
    if not i in extra_data: continue
    
    run = event.run
    lumi = event.lumi
    eventid = event.event    

    if not run in outdata[channel]: continue
    if not lumi in outdata[channel][run]: continue
    if not eventid in outdata[channel][run][lumi]: continue
    if not outdata[channel][run][lumi][eventid] == True: continue

    """if event.njets == 2: 
        if event.ntags > 1: continue
    elif event.njets == 3:
        if event.ntags > 2: continue
        if event.ntags < 1: continue"""
    jt = "%sj%st" % (event.njets, event.ntags)
    #if channel == "mu" and not (abs(event.lepton_id) == 13): continue
    #if channel == "ele" and not (abs(event.lepton_id) == 11): continue
    qw += 1
    
    #if vetomuons > 0 or vetoeles > 0: continue

    #if event.bjet_pt < 40 or event.ljet_pt < 40: continue
    #if abs(event.bjet_eta) > 4.5 or abs(event.ljet_eta) > 4.5: continue
    #if channel == "mu" and event.lepton_pt < 26: continue
    #if channel == "ele" and event.lepton_pt < 30: continue
    #if channel == "mu" and event.hlt_mu != 1: continue
    #if channel == "ele" and event.hlt_ele != 1: continue
    #qcd_mva_cut = 0.4
    #if channel == "ele":
    #    qcd_mva_cut = 0.55
    
    asd += 1
    
    #qcd_bdt = extra_data[i][0]
    #if qcd_bdt < qcd_mva_cut: continue    
    bdt = extra_data[i][1]
    xsweight = extra_data[i][2]
    wjets_shape = extra_data[i][3]
    wjets_yield = extra_data[i][4]
    if math.isnan(event.b_weight): 
        event.b_weight = 1
    total_weight = event.pu_weight * event.lepton_weight__id * event.lepton_weight__iso * event.lepton_weight__trigger \
             * wjets_shape * wjets_yield * xsweight

    #if eventid in missing_events:
    #missing += 1
    #print "info", eventid, event.pu_weight, event.lepton_weight__id, event.lepton_weight__iso, event.lepton_weight__trigger, event.b_weight, wjets_shape,  wjets_yield, xsweight

    if event.top_weight > 0:
        total_weight *= event.top_weight
    if math.isnan(event.lepton_weight__id): continue
    if math.isnan(event.lepton_weight__iso): continue
    if math.isnan(event.lepton_weight__trigger): continue
    if not math.isnan(event.b_weight):
        total_weight *= event.b_weight
    
    total_weight *= luminosity

    #print "weights: ",event.pu_weight, event.lepton_weight__id, event.lepton_weight__iso, event.lepton_weight__trigger, \
    #       event.top_weight, event.b_weight, wjets_shape, wjets_yield, xsweight
    #print run, lumi, eventid
    #print pdf_weights
    if not (run in pdf_weights and lumi in pdf_weights[run] and eventid in pdf_weights[run][lumi]):
        missing+=1
        print "MISSING", run, lumi, eventid, "BDT", bdt
        continue
    pdf_stuff = pdf_weights[run][lumi][eventid]
    other_stuff = pdf_input[run][lumi][eventid]
    #print other_stuff
    """if other_stuff["scale"]>maxscale:
        maxscale = other_stuff["scale"]
    if other_stuff["scale"]<minscale:
        minscale = other_stuff["scale"]
    if max(other_stuff["id1"], other_stuff["id2"]) > maxid:
        maxid = max(other_stuff["id1"], other_stuff["id2"])
    if min(other_stuff["id1"], other_stuff["id2"]) < minid:
        minid = min(other_stuff["id1"], other_stuff["id2"])
    if max(other_stuff["x1"], other_stuff["x2"]) > maxx:
        maxx = max(other_stuff["x1"], other_stuff["x2"])
    if min(other_stuff["x1"], other_stuff["x2"]) < minx:
        minx = min(other_stuff["x1"], other_stuff["x2"])
    """
    for (p, w) in pdf_stuff.items():
        #print "thispdf", thispdf, p
        if not (thispdf == p or (p == 'NNPDF23' and thispdf == "NNPDF23nloas0119LHgrid")): continue
        if p not in pdfs: continue
        #print "here"
            
        if math.isnan(histograms[channel][p]["bdt_sig_bg"][jt]["nominal"].Integral()): ghts
        """if p == "CT10LHgrid" and channel == "mu" and jt == "2j1t":
            print "eventid", eventid
            if total_weight > 0:
               print "pos_event_id", eventid
            if not (math.isnan(bdt) or math.isnan(total_weight)):
               print "notnan_event_id", eventid
            if (total_weight > 0 and not (math.isnan(bdt) or math.isnan(total_weight))):
                print "allfine_event_id", eventid
        """    
        histograms[channel][p]["bdt_sig_bg"][jt]["nominal"].Fill(bdt, total_weight)
        #print run, lumi, eventid
        strange = False
        strangePlus=False
        strangeMinus=False
        for j in range(len(w)):      
            if abs(w[j] - 1) > 1:
                strange = True
            if w[j] > 2:
                strangePlus = True
            if w[j] < 0:
                strangeMinus = True
        #if (not (strangePlus == True and strangeMinus==True)) and (strangePlus == True or strangeMinus==True):
        #    print "NOT DOUBLYSTRANGE"
        """
        for var in ["scale", "id1", "id2", "x1", "x2"]:
            histograms[c][p][var][jt]["nobdtcut"].Fill(other_stuff[var], total_weight)
            if strange==True:
                histograms[c][p][var][jt]["nobdtcut_strange"].Fill(other_stuff[var], total_weight)
        histograms[c][p]["id1id2"][jt]["nobdtcut"].Fill(other_stuff["id1"], other_stuff["id2"], total_weight)
        if strange==True:
            histograms[c][p]["id1id2"][jt]["nobdtcut_strange"].Fill(other_stuff["id1"], other_stuff["id2"], total_weight)
        """
        ok = True
        """for j in range(len(w)):      
            if abs(w[j]-1) > 0:
                ok = False
                break
        if not ok: continue"""
        for j in range(len(w)):
            this_weight = total_weight * w[j]
            #if abs(w[j]) > 10: w[j] = 1.
            #print "weight!", run, lumi, eventid, j, w[j]
            #print "weight", j, total_weight, w[j]
            #print event.top_weight, event.pu_weight, event.lepton_weight__id, event.lepton_weight__iso, event.lepton_weight__trigger, event.b_weight, wjets_shape, wjets_yield , xsweight
            if (dataset.startswith("T_t") and not dataset.startswith("T_tW")) or (dataset.startswith("Tbar_t") and not dataset.startswith("Tbar_tW")):
                this_weight /= average_weights[p][j]
            histograms[channel][p]["bdt_sig_bg"][jt]["weighted"][j].Fill(bdt, this_weight)
            histograms[channel][p]["pdfweight"][jt]["nominal"].Fill(w[j])
            #if abs(w[j]) > 50:
            #    print "weight!", run, lumi, eventid, j, w[j]
        if bdt < 0.6: continue
        #print "event_bdtid", eventid
        #for mybin in range(ranges["cos_theta"][0]):
        #if event.cos_theta_lj >= -0.5833333333 and event.cos_theta_lj < -0.5:  
        histograms[channel][p]["cos_theta"][jt]["nominal"].Fill(event.cos_theta_lj, total_weight)
        """for var in ["scale", "id1", "id2", "x1", "x2"]:
            histograms[c][p][var][jt]["final"].Fill(other_stuff[var], total_weight)
            if strange==True:
                histograms[c][p][var][jt]["final_strange"].Fill(other_stuff[var], total_weight)
            if strangePlus==True:
                histograms[c][p][var][jt]["final_strange_plus"].Fill(other_stuff[var], total_weight)
                if strangeMinus==True:
                    histograms[c][p][var][jt]["final_strange_plusminus"].Fill(other_stuff[var], total_weight)
            if strangeMinus==True:
                histograms[c][p][var][jt]["final_strange_minus"].Fill(other_stuff[var], total_weight)
            if event.cos_theta_lj >= -0.625 and event.cos_theta_lj < -0.5833:
                histograms[c][p][var][jt]["final_strange_bin9"].Fill(other_stuff[var], total_weight)
        histograms[c][p]["id1id2"][jt]["final"].Fill(other_stuff["id1"], other_stuff["id2"], total_weight)
        if strange==True:
            histograms[c][p]["id1id2"][jt]["final_strange"].Fill(other_stuff["id1"], other_stuff["id2"], total_weight)
        if strangePlus==True:
            histograms[c][p]["id1id2"][jt]["final_strange_plus"].Fill(other_stuff["id1"], other_stuff["id2"], total_weight)
            if strangeMinus==True:
                histograms[c][p]["id1id2"][jt]["final_strange_plusminus"].Fill(other_stuff["id1"], other_stuff["id2"], total_weight)
        if strangeMinus==True:
            histograms[c][p]["id1id2"][jt]["final_strange_minus"].Fill(other_stuff["id1"], other_stuff["id2"], total_weight)
        if event.cos_theta_lj >= -0.625 and event.cos_theta_lj < -0.5833:
            histograms[c][p]["id1id2"][jt]["final_strange_bin9"].Fill(other_stuff["id1"], other_stuff["id2"], total_weight)
        """
        for j in range(len(w)):
            for mybin in range(ranges["cos_theta"][0]):
                lowedge = -1 + mybin * (2. / ranges["cos_theta"][0])
                highedge = -1 + (mybin + 1) * (2. / ranges["cos_theta"][0])
                if event.cos_theta_lj >= lowedge and event.cos_theta_lj <= highedge:  
                    histograms[channel][p]["pdfweight"][jt]["nominal_bin"+str(mybin)].Fill(w[j])
            
            this_weight = total_weight * w[j]
            if (dataset.startswith("T_t") and not dataset.startswith("T_tW")) or (dataset.startswith("Tbar_t") and not dataset.startswith("Tbar_tW")):
                this_weight /= average_weights[p][j]
            histograms[channel][p]["cos_theta"][jt]["weighted"][j].Fill(event.cos_theta_lj, this_weight)
            desc = "."
            if abs(w[j])>2: desc = "strange"
            #ef.write("%d %d %d %s %f %f %d %f %f %f %d %d %f %s\n" % (run, lumi, eventid, p, bdt, event.cos_theta_lj, j, other_stuff["scale"], other_stuff["x1"], other_stuff["x2"], other_stuff["id1"], other_stuff["id2"], w[j], desc))
        

print "writing"
#path = os.path.join(os.environ["STPOL_DIR"], "src", "pdf_uncertainties", "output_removestrange")
path = os.path.join(os.environ["STPOL_DIR"], "src", "pdf_uncertainties", "output")
#path = os.path.join(os.environ["STPOL_DIR"], "src", "pdf_uncertainties", "output_skip")
#path = os.path.join(os.environ["STPOL_DIR"], "src", "pdf_uncertainties", "output_events")
outfilename = "%s/pdftest_%s_%s_%s_%s.root" % (path, channel, dataset, thispdf, counter)
outfile = TFile(outfilename, "RECREATE")
for p in histograms[channel]:
        for var in variables:
            if var in ["scale", "id1", "id2", "x1", "x2"]: continue
            for jt in jettag:
                print p, var, jt
                print histograms[channel][p][var][jt]["nominal"].GetEntries(), histograms[channel][p][var][jt]["nominal"].Integral()
                histograms[channel][p][var][jt]["nominal"].Write()
                for h in histograms[channel][p][var][jt]["weighted"]:
                    print h.Integral()
                    h.Write()
for p in histograms[channel]:
    for jt in jettag:
        if thispdf == "CT10LHgrid":
            histograms[channel][p]["cos_theta"][jt]["nominal"].Write()
            histograms[channel][p]["bdt_sig_bg"][jt]["nominal"].Write()
        for mybin in range(ranges["cos_theta"][0]):
            histograms[channel][p]["pdfweight"][jt]["nominal_bin"+str(mybin)].Write()
        maxbin = ranges[var][0]
        print "UNDER/OVERFLOW", var, "bin11", histograms[channel][p]["pdfweight"][jt]["nominal_bin11"].GetBinContent(0), histograms[channel][p]["pdfweight"][jt]["nominal_bin11"].GetBinContent(maxbin)
        print "UNDER/OVERFLOW", var, "bin12", histograms[channel][p]["pdfweight"][jt]["nominal_bin12"].GetBinContent(0), histograms[channel][p]["pdfweight"][jt]["nominal_bin12"].GetBinContent(maxbin)
        
        for var in ["scale", "id1", "id2", "x1", "x2"]:
            for h in histograms[channel][p][var][jt]:
                histograms[channel][p][var][jt][h].Write()
            """maxbin = ranges[var][0]
            
            print "UNDER/OVERFLOW", var, "nobdtcut", histograms[channel][p][var][jt]["nobdtcut"].GetBinContent(0), histograms[channel][p][var][jt]["nobdtcut"].GetBinContent(maxbin)
            print "UNDER/OVERFLOW", var, "nobdtcut_strange", histograms[channel][p][var][jt]["nobdtcut_strange"].GetBinContent(0), histograms[channel][p][var][jt]["nobdtcut_strange"].GetBinContent(maxbin)
            print "UNDER/OVERFLOW", var, "final", histograms[channel][p][var][jt]["final"].GetBinContent(0), histograms[channel][p][var][jt]["final"].GetBinContent(maxbin)
            print "UNDER/OVERFLOW", var, "final_strange", histograms[channel][p][var][jt]["final_strange"].GetBinContent(0), histograms[channel][p][var][jt]["final_strange"].GetBinContent(maxbin)"""
        for h in histograms[channel][p]["id1id2"][jt]:
            histograms[channel][p]["id1id2"][jt][h].Write()
#ef.close()
outfile.Write()
outfile.Close()
print "missing", missing
print qw, asd
#print "minmax", maxscale, minscale, maxid, minid, maxx, minx
print "finished"             

        
