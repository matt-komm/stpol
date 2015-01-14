#from rootpy.io import File
from os.path import join
#import argparse
#from plots.common.tdrstyle import tdrstyle
from ROOT import TCanvas, THStack, TFile, TH1D
import ROOT


from fit_components import *
from colors import *


def get_histos(fname, channel, isovar=None):
    f = TFile(fname)
    histos = {}
    for cut in ["qcdcut", "nocut", "reversecut"]:
        for var in ["qcd_mva", "met", "mtw"]:
            for jt in ["2j1t", "2j0t", "3j1t", "3j2t"]:
                for iso in ["iso", "antiiso"]:
                    for dataset in all_datasets_reproc:
                        if dataset == "QCD":continue
                        name = "qcd__%s__%s__%s__%s__%s__%s" % (cut, channel, var, jt, iso, dataset)
                        if not isovar==None and iso == "antiiso":
                            name += "__isovar__%s" % isovar
                            #print "ISOVAR"
                        print fname, name, cut+var+jt+iso+dataset
                        histos[cut+var+jt+iso+dataset] = f.Get(name)
                        histos[cut+var+jt+iso+dataset].SetLineColor(sample_colors_same[dataset])
                        #histos[cut+var+jt+iso+dataset].Rebin()
    return histos

def subtract_MC(hQCD, histos, cut, var, jt, variation=None):
    for dataset in fit_components_regular_reproc["non_qcd"]:
        h = histos[cut+var+jt+"antiiso"+dataset]
        coeff = -1
        if variation == "up":
            coeff *= (1+priors[dataset])
        elif variation == "down":
            coeff *= (1-priors[dataset])
        hQCD.Add(h, coeff)
        #print variation, dataset, priors[dataset]
        #print hQCD.Integral()

    for bin in range(hQCD.GetNbinsX()+1):
        if hQCD.GetBinContent(bin) < 0:
            hQCD.SetBinContent(bin, 0)
            hQCD.SetBinError(bin, 10.)

def subtract_MC_with_stack(hQCD, stack, variation=None):
    for h in stack.GetHists():
        coeff = -1
        if variation == "up":
            coeff *= (1+priors[dataset])
        elif variation == "down":
            coeff *= (1-priors[dataset])
        hQCD.Add(h, coeff)
        #print hQCD.Integral()

    for bin in range(hQCD.GetNbinsX()+1):
        if hQCD.GetBinContent(bin) < 0:
            hQCD.SetBinContent(bin, 0)
            hQCD.SetBinError(bin, 1.)

def add_other_components(histos, cut, var, jt, components = "regular"):
    others = []
    for (comp, datasets) in fit_components_reproc[components].items():
        hist = histos[cut+var+jt+"iso"+datasets[0]].Clone()
        name = hist.GetName().split("__")
        new_name = "__".join([var, comp])
        hist.SetNameTitle(new_name, new_name)
        print datasets[0], hist.Integral()
        for i in range(1, len(datasets)):
            h = histos[cut+var+jt+"iso"+datasets[i]].Clone()
            hist.Add(h)
            print datasets[i], h.GetEntries(), h.Integral()
        others.append(hist)
    return others
        
    

def make_histos(histos, channel, var, jt, cut, components, isovar=None, variateMC=None):
    hData = histos[cut+var+jt+"iso"+"data"]
    print "data", isovar, hData.GetEntries(), hData.Integral()
    hData.SetNameTitle("%s__DATA" % var, "%s__DATA" % var)
    if variateMC == "QCDMC":
        hQCD = histos[cut+var+jt+"iso"+"QCD"]
    elif variateMC == "QCDMC2J0T":
        hQCD = histos[cut+var+"2j0t"+"iso"+"QCD"]
    else:
        hQCD = histos[cut+var+jt+"antiiso"+"data"]
        print "qcd", isovar, hQCD.GetEntries(), hQCD.Integral()
        subtract_MC(hQCD, histos, cut, var, jt, variateMC)
        print "qcd_sub", isovar, hQCD.GetEntries(), hQCD.Integral()
        
    hQCD.SetNameTitle("%s__QCD" % var, "%s__QCD" % var)
    print hQCD.GetEntries(), hData.Integral()
    others = add_other_components(histos, cut, var, jt, components)
    return (hData, hQCD, others)

def plot_templates():
    """canv1 = TCanvas("canvas", "canvas", 800,800)
     h.SetAxisRange(0, 0.25, "Y")
      h.GetXaxis().SetTitle(varname)                                                          
    hQCD.SetLineWidth(2)
                    leg = ROOT.TLegend(0.65,0.6,0.9,0.90)
                    #leg.SetTextSize(0.037)
                    leg.SetBorderSize(0)
                    leg.SetLineStyle(0)
                    leg.SetTextSize(0.015)
                    leg.SetFillColor(0)
                    
                    leg.AddEntry(hData,"Data","pl")
                    #leghistos.items()[1].Draw("hist")
                    for (name, histos) in hists[jt].items():
                        if "_iso" in name:
                            for (histoname, h) in hists[jt][name].items():
                                if varname in histoname:
                                    print h, h.GetTitle()
                                    leg.AddEntry(h, h.GetTitle().split("__")[1],"l")
                    leg.AddEntry(hQCD,"QCD","l")
                    leg.Draw()

                    #print "normQCD", normQCD.Integral()
                    #normQCD.Draw("same hist")        
                    canv1.SaveAs("plots/"+varname+"_shapes_"+args.channel+"_"+jt+"_"+cuttype+"_"+added+".pdf")
                    canv1.SaveAs("plots/"+varname+"_shapes_"+args.channel+"_"+jt+"_"+cuttype+"_"+added+".png")
    """                    

if __name__=="__main__":
    #parser = argparse.ArgumentParser(description='')
    #parser.add_argument('--path', dest='path', default="/".join([os.environ["STPOL_DIR"], "src", "qcd_ntuples", "histos"]))
    #parser.add_argument('--channel', dest='channel' , default='mu')
    #args = parser.parse_args()
    components = "regular"

    ROOT.TH1.AddDirectory(False)
    ROOT.gROOT.SetStyle("Plain")
    ROOT.gStyle.SetOptStat(0)
    ROOT.gROOT.SetBatch()
    for channel in ["mu", "ele"]:
        myvars = ["qcd_mva", "met"]
        if channel == "mu":
            myvars.append("mtw")
        added = "11Jan_deltaR" ##Nov_reproc"
    	for varname in myvars:
            for jt in ["2j1t", "2j0t", "3j1t", "3j2t"]:
                for cut in ["reversecut", "nocut"]:#, "qcdcut"]:
                    for variateMC in [None]:#, "up", "down", "QCDMC", "QCDMC2J0T"]:
                        for isovar in [None, "up", "down"]:
                            histos = get_histos("input_histos/%s/%s.root" % (added, channel), channel, isovar)  
                            if not variateMC and not isovar:
                                outfile = TFile("templates/%s__%s__%s__%s__%s.root" % (varname, jt, channel, cut, added), "recreate")
                            else:
                                if not isovar:
                                    outfile = TFile("templates/%s__%s__%s__%s__%s__%s.root" % (varname, jt, channel, cut, added, "varMC_"+variateMC), "recreate")
                                else:
                                    outfile = TFile("templates/%s__%s__%s__%s__%s__%s.root" % (varname, jt, channel, cut, added, "isovar_"+isovar), "recreate")
        
                            #print "OUTFILE", "templates/"+varname+"__"+jt+"__"+channel+"__"+cut+"__"+added+".root"
                            (hData, hQCD, others) = make_histos(histos, channel, varname, jt, cut, components, isovar, variateMC)
                            #if not variateMC and not isovar:
                            #    plot_QCD_template(hQCD, channel, varname, jt, cut)
                            outfile.cd()
                            hData.Write()
                            print "write", outfile.GetName(), isovar, hQCD.Integral()
                            hQCD.Write()
                            for h in others:
                                h.Write()
                            #plot_templates()    
                            outfile.Close()            
