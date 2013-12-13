import ROOT, os, sys
from file_names import dataFiles_ele, dataFiles_mu, mcFiles, dataLumi_ele, dataLumi_mu

try:
    sys.path.append(os.environ["STPOL_DIR"] )
except KeyError:
    print "Could not find the STPOL_DIR environment variable, did you run `source setenv.sh` in the code base directory?"
    sys.exit(1)

from plots.common.cross_sections import xs

#channel = "electron_channel"
channel = "muon_channel"

if channel == "muon_channel":
    from plot_defs_mu import hist_def, cuts
else:
    from plot_defs_ele import hist_def, cuts

cutstring = "final"
#cutstring = "final_nomet"
#cutstring = "final_nomet_antiiso"

#cutstring = "2j1t"
#cutstring = "2j1t_nomet"

#cutstring = "2j0t"
#cutstring = "2j0t_nomet"

#cutstring = "3j2t"
#cutstring = "3j1t"

if cutstring == "final_nomet_antiiso":
    cutstring_qcd_template = cutstring
else:
    cutstring_qcd_template = cutstring + "_antiiso"


apply_PUw = True
apply_Elw = True
apply_Bw = True

mode = "_lep"     # leptonic samples of signal and ttbar
#mode = "_incl"    # inclusive samples of signal and ttbar

if channel == "electron_channel":
    infilePathMC = "~liis/SingleTopJoosep/stpol/out_step3_05_31_18_43/ele/iso/Nominal/"
    infilePathData = "~liis/SingleTopJoosep/stpol/out_step3_05_31_18_43/ele/iso/Nominal/"
#    infilePathMC = "~liis/SingleTopJoosep/stpol/out_step3_05_31_18_43/ele/antiiso/Nominal/"
#    infilePathData = "~liis/SingleTopJoosep/stpol/out_step3_05_31_18_43/ele/antiiso/Nominal/"
elif channel == "muon_channel":
    infilePathMC = "~liis/SingleTopJoosep/stpol/out_step3_05_31_18_43/mu/iso/Nominal/"
    infilePathData = "~liis/SingleTopJoosep/stpol/out_step3_05_31_18_43/mu/iso/Nominal/"
#    infilePathMC = "~liis/SingleTopJoosep/stpol/out_step3_05_31_18_43/mu/antiiso/Nominal/"
#    infilePathData = "~liis/SingleTopJoosep/stpol/out_step3_05_31_18_43/mu/antiiso/Nominal/"
else:
    print "Specify either electron_channel or muon_channel"
    sys.exit(1)

#----------------------------get files---------------------
if channel == "electron_channel":
    Lumi = sum(dataLumi_ele.values())
if channel == "muon_channel":
    Lumi = sum(dataLumi_mu.values())

files_data = {}
print("Loading files")

if channel == "electron_channel":
    dataFiles = dataFiles_ele
if channel == "muon_channel":
    dataFiles = dataFiles_mu

for key in dataFiles:
    filename = dataFiles[key]
    infile = infilePathData + filename
    print "Opening file: " + infile
    files_data[key] = ROOT.TFile(infile)

file_data_anti = ROOT.TFile( infilePathData + "qcd_temp.root")

files_mc = {}
for key in mcFiles:
    if channel == "muon_channel" and (key[-5:] == "BCtoE" or key[-10:] == "EMEnriched"):
        continue
    if channel == "electron_channel" and key == "QCDMu":
        continue
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
    if channel == "muon_channel":
        w_eltr = "muon_TriggerWeight"
        w_eliso = "muon_IsoWeight*muon_IDWeight"
    else:
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
        if channel == "electron_channel" and ():
            continue
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
    elif mode == "_lep":
        hist_final[hist_name]["signal"] = histos[hist_name]["T_t_ToLeptons"].Clone("signal")
        hist_final[hist_name]["signal"].Add(histos[hist_name]["Tbar_t_ToLeptons"])
    else:
        print "Insert either _incl or _lep as mode"
        sys.exit(1)
        
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

    hist_final[hist_name]["gjets"] = histos[hist_name]["GJets2"].Clone("gjets")
    hist_final[hist_name]["gjets"].Add(histos[hist_name]["GJets1"])

    hist_final[hist_name]["zjets"] = histos[hist_name]["DYJets"].Clone("zjets")

    if channel == "electron_channel":
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

    if channel == "muon_channel":
        hist_final[hist_name]["qcd_mc"] = histos[hist_name]["QCDMu"].Clone("qcd_mc")

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
outfilepath = "Histograms/" + channel + "/" + cutstring  + "/"

# If the path doesn't exist, make it...
if not os.path.exists(outfilepath):
    os.makedirs(outfilepath)

outfile = outfilepath + cutstring + weightstring + mode + ".root"
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
if channel == "electron_channel":
    fit_var = "met"
if channel == "muon_channel":
    fit_var = "mt_mu"

outfile = outfilepath + cutstring + weightstring + mode + "_templates.root"
t = ROOT.TFile(outfile,"recreate")
print "writing templates for qcd-fit: " + outfile

met__ewk = hist_final[fit_var]["signal"].Clone("met__ewk")
for key in hist_final[fit_var]:
    if key != "signal" and key != "data" and key != "data_anti" and key != "QCD":
        met__ewk.Add(hist_final[fit_var][key])
        
met__DATA = hist_final[fit_var]["data"].Clone("met__DATA") #apply the appropriate naming scheme for theta_auto input
met__qcd = hist_final[fit_var]["data_anti"].Clone("met__qcd")
      
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
                                
