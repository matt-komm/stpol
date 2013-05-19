import ROOT, os, sys
from file_names import dataFiles, mcFiles, dataLumi
from plot_defs import hist_def,cuts

try:
    sys.path.append(os.environ["STPOL_DIR"] )
except KeyError:
    print "Could not find the STPOL_DIR environment variable, did you run `source setenv.sh` in the code base directory?"
    sys.exit(1)

from plots.common.cross_sections import xs

cutstring = "final"
#cutstring = "final_nomet"

#cutstring = "2j1t"
#cutstring = "2j1t_nomet"

#cutstring = "2j0t"
#cutstring = "2j0t_nomet"

cutstring_qcd_template = cutstring + "_antiiso"

apply_PUw = True
apply_Elw = True
apply_Bw = False

mode = "_lep"     # leptonic samples of signal and ttbar
#mode = "_incl"    # inclusive samples of signal and ttbar

#infilePath = "/home/liis/data/Step3_output_0105/"

#infilePathMC = "/home/liis/SingleTopJoosep/stpol/step3_trees/step3_mc_05_10/"
infilePathMC = "/home/liis/SingleTopJoosep/stpol/step3_trees/step3_mc_05_17/"
infilePathData = "/home/liis/SingleTopJoosep/stpol/step3_trees/step3_data_05_10/"

#----------------------------get files---------------------
#Lumi = sum(dataLumi.values())
Lumi = 19400

files_data = {}
print("Loading files")
for key in dataFiles:
    filename = dataFiles[key]
    infile = infilePathData + filename
    print "Opening file: " + infile
    files_data[key] = ROOT.TFile(infile)

file_data_anti = ROOT.TFile( infilePathData + "qcd_temp.root")

files_mc = {}
for key in mcFiles:
    filename = mcFiles[key]
    infile = infilePathMC + filename
    print "Opening file: " + infile
    files_mc[key] = ROOT.TFile(infile)
              
# ----------------------get trees-----------------------
trees_data = {}
trees_mc = {}

for key in files_data:
    trees_data[key] = files_data[key].Get("trees").Get("Events")

trees_data_anti = file_data_anti.Get("trees").Get("Events")

for key in files_mc:
    trees_mc[key] = files_mc[key].Get("trees").Get("Events")

cut = cuts[cutstring]
cut_qcd_template = cuts[cutstring_qcd_template]

w_PU = "1"
w_btag = "1"
w_eliso = "1"
w_eltr = "1"

if apply_PUw:
    w_PU = "pu_weight"

if apply_Bw:
    w_btag = "b_weight_nominal"

if apply_Elw:
    w_eltr = "electron_triggerWeight"    
    w_eliso = "electron_IDWeight"

histos = {}
hist_final = {}

for hist_name in hist_def:
    print("Get " + hist_name + " historgrams:")
    histToPlot = hist_def[hist_name][0]
    hRange = hist_def[hist_name][1]
    
    histos[hist_name] = {}
    hist_final[hist_name] = {}
    
    print("Loading data histograms")
    histName_data = "h_data_" + hist_name
    histData = ROOT.TH1F( histName_data, histName_data, hRange[0], hRange[1], hRange[2] )

    histName_data_anti = "h_data_anti" + hist_name
    histData_anti = ROOT.TH1F( histName_data_anti, histName_data_anti, hRange[0], hRange[1], hRange[2] )
    
    for key in trees_data:
        print("Loading: " + key)
        if( hist_name ==  "eta_lj" ):
            trees_data[key].Draw( "abs(" + histToPlot + ")" + ">>+" + histName_data, cut, "goff") #">>+histName" -- sum all histograms to histData, goff = "graphics off"
        else:
            trees_data[key].Draw( histToPlot + ">>+" + histName_data, cut, "goff") #">>+histName" -- sum all histograms to histData, goff = "graphics off"
            
    if( hist_name == "eta_lj"):
        trees_data_anti.Draw( "abs(" + histToPlot + ")" + ">>" + histName_data_anti, cut_qcd_template, "goff")
    else:
        trees_data_anti.Draw( histToPlot + ">>" + histName_data_anti, cut_qcd_template, "goff")

    hist_final[hist_name]["data"] = histData
    hist_final[hist_name]["data_anti"] = histData_anti

    print("Loading MC histograms")
    for process in trees_mc:
        N = files_mc[process].Get("trees").Get("count_hist").GetBinContent(1) #total number of analyzed MC events
        w = Lumi*xs[process]/N
        print("Loading:" + process + " with xs = " + str(xs[process])+ " and MC ev. weight = " + str(w))
        
        histName = "h_" + hist_name + "_" + process
        h = ROOT.TH1F( histName, histName, hRange[0], hRange[1], hRange[2] )
        h.Sumw2() # remember weights - not sure of the use

        if( hist_name == "eta_lj"):
            trees_mc[process].Draw( "abs(" + histToPlot + ")" + ">>" + histName, str(w)+ "*" + w_PU + "*" + w_btag + "*" + w_eliso + "*" + w_eltr + "*" +  cut, "goff" )
        else:
            trees_mc[process].Draw( histToPlot + ">>" + histName, str(w)+ "*" + w_PU + "*" + w_btag + "*" + w_eliso + "*" + w_eltr + "*" +  cut, "goff" )
            
        histos[hist_name][process] = h
        
    #------------------Join stuff---------------------------
    if mode == "_incl":
        hist_final[hist_name]["signal"] = histos[hist_name]["T_t"].Clone("signal")
        hist_final[hist_name]["signal"].Add(histos[hist_name]["Tbar_t"])

#        hist_final[hist_name]["ttjets"] = histos[hist_name]["TTJets_MassiveBinDECAY"].Clone("ttjets")
    elif mode == "_lep":
        hist_final[hist_name]["signal"] = histos[hist_name]["T_t_ToLeptons"].Clone("signal")
        hist_final[hist_name]["signal"].Add(histos[hist_name]["Tbar_t_ToLeptons"])

#        hist_final[hist_name]["ttjets"] = histos[hist_name]["TTJets_SemiLept"].Clone("ttjets")
#        hist_final[hist_name]["ttjets"].Add(histos[hist_name]["TTJets_FullLept"])
    else:
        print "error"

    hist_final[hist_name]["ttjets"] = histos[hist_name]["TTJets_SemiLept"].Clone("ttjets")
    hist_final[hist_name]["ttjets"].Add(histos[hist_name]["TTJets_FullLept"])

    hist_final[hist_name]["wjets"] = histos[hist_name]["W1Jets_exclusive"].Clone("wjets")
    hist_final[hist_name]["wjets"].Add(histos[hist_name]["W2Jets_exclusive"])
    hist_final[hist_name]["wjets"].Add(histos[hist_name]["W3Jets_exclusive"])
    hist_final[hist_name]["wjets"].Add(histos[hist_name]["W4Jets_exclusive"])

    hist_final[hist_name]["diboson"] = histos[hist_name]["WW"].Clone("diboson")
    hist_final[hist_name]["diboson"].Add(histos[hist_name]["WZ"])
    hist_final[hist_name]["diboson"].Add(histos[hist_name]["ZZ"])

    hist_final[hist_name]["sch"] = histos[hist_name]["T_s"].Clone("stop")
    hist_final[hist_name]["sch"].Add(histos[hist_name]["Tbar_s"])
    
    hist_final[hist_name]["tW"] = histos[hist_name]["T_tW"].Clone("tW")
    hist_final[hist_name]["tW"].Add(histos[hist_name]["Tbar_tW"])

#    hist_final[hist_name]["gjets"] = histos[hist_name]["GJets2"].Clone("gjets")
#    hist_final[hist_name]["gjets"].Add(histos[hist_name]["GJets1"])

    hist_final[hist_name]["zjets"] = histos[hist_name]["DYJets"].Clone("zjets")

    hist_final[hist_name]["qcd_mc"] = histos[hist_name]["QCD_Pt_20_30_BCtoE"].Clone("qcd_mc")
    hist_final[hist_name]["qcd_mc"].Add(histos[hist_name]["QCD_Pt_30_80_BCtoE"])
    hist_final[hist_name]["qcd_mc"].Add(histos[hist_name]["QCD_Pt_80_170_BCtoE"])
    hist_final[hist_name]["qcd_mc"].Add(histos[hist_name]["QCD_Pt_170_250_BCtoE"])
    hist_final[hist_name]["qcd_mc"].Add(histos[hist_name]["QCD_Pt_250_350_BCtoE"])
    hist_final[hist_name]["qcd_mc"].Add(histos[hist_name]["QCD_Pt_350_BCtoE"])
    hist_final[hist_name]["qcd_mc"].Add(histos[hist_name]["QCD_Pt_20_30_EMEnriched"])
    hist_final[hist_name]["qcd_mc"].Add(histos[hist_name]["QCD_Pt_30_80_EMEnriched"])
    hist_final[hist_name]["qcd_mc"].Add(histos[hist_name]["QCD_Pt_80_170_EMEnriched"])
    hist_final[hist_name]["qcd_mc"].Add(histos[hist_name]["QCD_Pt_170_250_EMEnriched"])
    hist_final[hist_name]["qcd_mc"].Add(histos[hist_name]["QCD_Pt_250_350_EMEnriched"])
    hist_final[hist_name]["qcd_mc"].Add(histos[hist_name]["QCD_Pt_350_EMEnriched"])
#-----------------save histograms for plotting---------------
weightstring = ""
if w_PU != "1":
    weightstring = weightstring + "_PUw"
if w_btag != "1":
    weightstring = weightstring + "_Bw"
if w_eliso != "1":
    weightstring = weightstring + "_Elw"
if w_eltr != "1":
    weightstring = weightstring + "_ElTrw"

outfile = "Histograms/" + cutstring + "/" + cutstring + weightstring + mode + ".root"
p = ROOT.TFile(outfile,"recreate")
print "writing output to file: " + outfile

dirs = {} # make a directory for each process

for process in hist_final[hist_name]:
    dirs[process] = p.mkdir(process)
    
for hist_name in hist_final:
    for process in hist_final[hist_name]:
        dirs[process].cd()
        hist_final[hist_name][process].Write(hist_name)
p.Close()

#---------------------save qcd templates----------------
#if cutstring == "2j1t_nomet" or cutstring == "2j0t_nomet" or cutstring == "final_nomet_lep":
outfile = "Histograms/" + cutstring  + "/" + cutstring + weightstring + mode + "_templates.root"
t = ROOT.TFile(outfile,"recreate")
print "writing templates for qcd-fit: " + outfile

met__ewk = hist_final["met"]["signal"].Clone("met__ewk")
for key in hist_final["met"]:
    if key != "signal" and key != "data" and key != "data_anti" and key != "QCD":
        met__ewk.Add(hist_final["met"][key])
        
met__DATA = hist_final["met"]["data"].Clone("met__DATA") #apply the appropriate naming scheme for theta_auto input
met__qcd = hist_final["met"]["data_anti"].Clone("met__qcd")
      
met__DATA.Write()
met__ewk.Write()
met__qcd.Write()
t.Close()
#------------------print event yields-------------------
sum_mc = 0
print "Event yields at Lumi = " + str(Lumi)
for process in hist_final[hist_name]:
    if process != "data" and process != "data_anti":
        print process + ": " + str(hist_final[hist_name][process].Integral())
        sum_mc += hist_final[hist_name][process].Integral()

print "data: " + str(hist_final[hist_name]["data"].Integral())
print "sum_mc: " + str(sum_mc)
print "qcd template from data: " + str(hist_final[hist_name]["data_anti"].Integral())        
                                
