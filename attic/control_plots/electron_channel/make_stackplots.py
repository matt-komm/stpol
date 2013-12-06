import sys
import os

#Need to add parent dir to python path to import plots
try:
    sys.path.append(os.environ["STPOL_DIR"] )
except KeyError:
    print "Could not find the STPOL_DIR environment variable, did you run `source setenv.sh` in the code base directory?"
    sys.exit(1)

import tdrstyle
tdrstyle.tdrstyle()

import ROOT
from plots.common.sample_style import Styling
from plots.common.utils import lumi_textbox
from plots.common.legend import legend
from plots.common.pretty_names import variable_names

#channel = "electron_channel"
channel = "muon_channel" 

if channel == "muon_channel":
    from plot_defs_mu import hist_def
else:
    from plot_defs_ele import hist_def

from file_names import dataLumi_ele, dataLumi_mu
if channel == "electron_channel":
    Lumi = sum(dataLumi_ele.values())
if channel == "muon_channel":
    Lumi = sum(dataLumi_mu.values())

# choose cut region
mode1 = "final"
#mode1 = "2j1t"
#mode1 = "2j0t"
#mode1 = "3j1t"
#mode1 = "3j2t"
#mode1 = "final_nomet_antiiso"

mode1a = ""
#mode1a = "_nomet"

#choose whether inclusive or leptonic ttbar and signal samples are used
#mode2 = "_incl" 
mode2 = "_lep"
mode = mode1 + mode1a + mode2

do_ratio = False
qcd_from_mc = False
apply_PUw = True
apply_Elw = True
apply_Bw = True

weight = ""
if  apply_PUw:
    weight += "_PUw"
if apply_Bw:
    weight += "_Bw"
if apply_Elw:
    weight += "_Elw_ElTrw"

from plots.common.utils import merge_cmds
process_names = merge_cmds.keys()
process_names.insert(1,"QCD")

#--------------------open file ------------------------
filename = mode1 + mode1a + weight + mode2 +".root"
histograms = "Histograms/" + channel + "/" + mode1 + mode1a + "/" + filename
print "Opening input file: " + histograms
h = ROOT.TFile(histograms)

#------------------------------------------------------

for hist_name in hist_def:
    hist_to_plot = hist_def[hist_name][0]
    print "Plotting:" + hist_to_plot

    from plots.common.odict import OrderedDict as dict
    mc_to_plot = dict()

    mc_to_plot["diboson"] = h.Get("diboson/" + hist_to_plot)
    mc_to_plot["WJets_inclusive"] = h.Get("wjets/" + hist_to_plot)
    mc_to_plot["DYJets"] = h.Get("zjets/" + hist_to_plot)
    mc_to_plot["TTJets"] = h.Get("ttjets/" + hist_to_plot)
    mc_to_plot["T_tW"] = h.Get("tW/" + hist_to_plot)
    mc_to_plot["T_s"] = h.Get("sch/" + hist_to_plot)
    mc_to_plot["signal"] = h.Get("signal/" + hist_to_plot)
        
    data = h.Get("data/" + hist_to_plot)

    if qcd_from_mc:
        print "Get QCD from MC"
        qcd = h.Get("qcd_mc/" + hist_to_plot)
    else:
        print "Get QCD from data"
        qcd = h.Get("data_anti/" + hist_to_plot)
        
#----------calculate QCD yield from data--------
    qcd_mode = mode1 + mode2 #omit possible "_nomet" extension as it is always used for the fit
    qcd_norm = 0

    print "QCD template yield = " + str(qcd.Integral())
    if ( qcd_from_mc == False and hist_to_plot != "el_mother_id"):
        from qcd_yields import getQCDYield

        if channel == "electron_channel":
            qcd_norm = getQCDYield( qcd, qcd_mode, True, "ele")
        if channel == "muon_channel":
            qcd_norm = getQCDYield( qcd, qcd_mode, True, "mu")
        
        print "QCD estimated from data = " + str(qcd_norm)

        if qcd.Integral() != 0:
            qcd.Scale(qcd_norm/qcd.Integral()) #rescale qcd template according to the best-fit value

#--------------Rebin----------------
    if hist_name == "cos_theta" or hist_name == "pt_lj" or hist_name == "eta_lj" or hist_name == "el_mva": #<--sometimes need to change rebin to 1, if plots are weird (QCD not shown)
        nrebin = 4
    elif hist_name == "met" or hist_name == "mt_mu" or hist_name == "el_pt" or hist_name == "top_mass" or hist_name == "deltaR_lj" or hist_name == "deltaR_bj":
        nrebin = 2
    else:
        nrebin =1

    for key in mc_to_plot:
        mc_to_plot[key].Rebin(nrebin)
        Styling.mc_style(mc_to_plot[key],key)

    qcd.Rebin(nrebin)
    Styling.mc_style(qcd,"QCD")

    data.Rebin(nrebin)
    Styling.data_style(data)

#--------------stack----------------------------
    sum = ROOT.THStack("sum","")
    h_sumMC = mc_to_plot["signal"].Clone("h_sumMC")

    for key in mc_to_plot:
        if key != "signal":
            h_sumMC.Add(mc_to_plot[key])
    h_sumMC.Add(qcd)

    sum.Add(qcd)
    for sample in mc_to_plot.values():
        sum.Add( sample )

#-------------------style------------------------
    h_sumMC.SetTitle("")
    h_sumMC.SetStats(False)
    h_sumMC.SetLineWidth(2)
    h_sumMC.SetMaximum(  1.3*max( h_sumMC.GetMaximum(), data.GetMaximum() ))
    if hist_name == "cos_theta" and  ( mode1 == "3j2t" or mode1 == "3j1t"):
        h_sumMC.SetMaximum(  1.5*max( h_sumMC.GetMaximum(), data.GetMaximum() ))
                                       

 #   if hist_name == "el_mva":
 #       h_sumMC.SetMaximum( 5*max( h_sumMC.GetMaximum(), data.GetMaximum() )) 

    h_sumMC.SetLineColor(ROOT.kBlack)
    h_sumMC.SetFillStyle(0)
    h_sumMC.GetXaxis().SetTitle(variable_names[hist_name]);    
#---------------------Draw----------------------------
    if do_ratio:
        print "Make ratio plot"
        c = ROOT.TCanvas("c","",800,800)
        mainC = ROOT.TPad("main","Main plot",0,0.25,1,1)
        mainC.Draw()
        ratioC = ROOT.TPad("ratio","ratio",0,0,1,0.24)
        ratioC.Draw()

        hRange = hist_def[hist_name][1]
        ratio_hist = "h_" + hist_name
        r = ROOT.TH1D(ratio_hist, "", hRange[0], hRange[1], hRange[2])

        u1 = ROOT.TH1D(r)
        u1.Reset()

        u1.Draw("lsame")
        
    else:
        c = ROOT.TCanvas("c","")
#        if hist_to_plot == "el_mva":
#            c.SetLogy()
        h_sumMC.Draw("hist")
        sum.Draw("histsame")
        h_sumMC.Draw("histsame")
        data.Draw("epsame")
#--------------- lumi box and legend-----------------
    if hist_name == "cos_theta" or hist_name == "el_mva":
        legend_pos = "top-left"
    else:
        legend_pos = "top-right"

    if legend_pos == "top-right":
        lumibox = lumi_textbox(Lumi,"top-left")
    if legend_pos == "top-left":
        lumibox = lumi_textbox(Lumi,"top-right")
    
    hist_list = mc_to_plot.values()
    hist_list.reverse() # reverse order of mc histograms for the legend entry
    hist_list.append(qcd)
    hist_list.insert(0,data)
    
    leg = legend(
        hist_list,
        names = process_names,
        styles=["p", "f"],
        width=0.25,
        pos = legend_pos
        )

    outfilename = "Plots/" + channel + "/" + mode1 + mode1a + "/" + hist_to_plot + mode2 + weight + ".pdf"
    if not os.path.exists(os.path.dirname(outfilename)):
        os.makedirs(os.path.dirname(outfilename))
    c.SaveAs(outfilename)
    c.Close()

    #----------------Signal PDG ID information------------------
#    nr_W = 0
#    nr_tau = 0
    if hist_to_plot == "el_mother_id" or hist_to_plot == "mu_mother_id":
        nr_W = mc_to_plot["signal"].GetBinContent(2) + mc_to_plot["signal"].GetBinContent(50)
        nr_tau = mc_to_plot["signal"].GetBinContent(11) + mc_to_plot["signal"].GetBinContent(41)
        print "nr tau- = " + str(mc_to_plot["signal"].GetBinContent(41))
        print "nr tau+ = " + str(mc_to_plot["signal"].GetBinContent(11))

 #------------------------------print cut flow--------------------------

    if hist_to_plot == "cos_theta":
        print("CUT FLOW:")
        print("----------------------")
        err = {}
        for key in mc_to_plot:
            try:
                err[key] = mc_to_plot[key].Integral()/(mc_to_plot[key].GetEntries()**0.5) 
            except ZeroDivisionError:
                err[key] = 0.0
            print key + ": " + str( mc_to_plot[key].Integral() ) + " +- " + str(err[key])
            
        try:
            err_qcd = qcd.Integral()/(qcd.GetEntries()**0.5)     
        except ZeroDivisionError:
            err_qcd = 0.0
            
        print("QCD: " + str(qcd.Integral()) + " +- " + str( err_qcd ))

        err_tot2 = 0
        for e in err.values():
            err_tot2 = err_tot2 + e**2
        err_tot = (err_tot2 + err_qcd**2)**0.5

        print("----------------------")
        print("sum MC: " + str(h_sumMC.Integral()) + "+-" + str(err_tot) )
        print("Data: " + str(data.Integral()) + " +- " + str( data.Integral()**0.5 ) )
        print("----------------------")
        print 
        
print "Electron mother pdgID in signal sample"
print("----------------------")

try:
    print "nr of prompt electrons from W: " +  str(nr_W ) + " (" + str(nr_W/mc_to_plot["signal"].Integral()*100) + "%)"
    print "nr of electrons from tau decays: " + str( nr_tau ) + " (" + str(nr_tau/mc_to_plot["signal"].Integral()*100) + "%)"
    print "Other decays: " + str( mc_to_plot["signal"].Integral() - (nr_W + nr_tau) ) + " (" + str( (mc_to_plot["signal"].Integral() - (nr_W + nr_tau) )/mc_to_plot["signal"].Integral()*100) + "%)"
except NameError:
    print "Not Available"

print "---------------------------------------"
