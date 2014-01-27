import ROOT
import os
import numpy
import math
import sys

def readKeys(inputfile):
    ret={}
    for line in inputfile:
        key,value=line.replace(" ","").replace("\n","").replace("\r","").split(",")
        ret[key]=float(value)
    if ret.has_key("mean") and ret.has_key("rms"):
        return ret
    else:
        print "error - could not read keys"
        sys.exit(-1)
        return None
    
def diff(rms1,rms2,mean1,mean2):
    
    #return rms1-rms2
    ret =0
    if (rms1**2-rms2**2+math.fabs(mean1-mean2)**2)>0:
        ret = math.sqrt(rms1**2-rms2**2+math.fabs(mean1-mean2)**2)
    return ret
    
def setStyle(graph,color):
    graph.SetMarkerStyle(21)
    graph.SetLineColor(color)
    graph.SetLineWidth(2)
    graph.SetMarkerColor(color)
    graph.SetMarkerSize(1.2)
    
def getAsymmetry(folderList):
    asymmetryDict ={
                    "bdt":[],"asymmetry_total":{"mean":[], "rms":[]},
                    "asymmetry_nominal":{"mean":[], "rms":[]},
                    "asymmetry_stat":{"mean":[], "rms":[]},
                    "asymmetry_sys":{"mean":[], "rms":[]},
                    "asymmetry_mc":{"mean":[], "rms":[]}
                    }
    for folder in folderList:
        asymmetryDict["bdt"].append(folder[1])
        
        f = open(os.path.join(folder[0],"nothing","asymmetry.txt"),"r")
        result=readKeys(f)
        f.close()
        nominal_mean=result["mean"]
        nominal_rms=result["rms"]
        asymmetryDict["asymmetry_nominal"]["mean"].append(result["mean"])
        asymmetryDict["asymmetry_nominal"]["rms"].append(result["rms"])
        
        
        f = open(os.path.join(folder[0],"total","asymmetry.txt"),"r")
        result=readKeys(f)
        f.close()
        total_mean=result["mean"]
        total_rms=result["rms"]
        asymmetryDict["asymmetry_total"]["mean"].append(result["mean"])
        asymmetryDict["asymmetry_total"]["rms"].append(diff(result["rms"],0.0,result["mean"],nominal_mean))
        
        f = open(os.path.join(folder[0],"statonly","asymmetry.txt"),"r")
        result=readKeys(f)
        f.close()
        asymmetryDict["asymmetry_stat"]["mean"].append(result["mean"])
        asymmetryDict["asymmetry_stat"]["rms"].append(diff(total_rms,result["rms"],result["mean"],nominal_mean))
        
        f = open(os.path.join(folder[0],"sysonly","asymmetry.txt"),"r")
        result=readKeys(f)
        f.close()
        asymmetryDict["asymmetry_sys"]["mean"].append(result["mean"])
        asymmetryDict["asymmetry_sys"]["rms"].append(diff(total_rms,result["rms"],result["mean"],nominal_mean))
        
        f = open(os.path.join(folder[0],"mconly","asymmetry.txt"),"r")
        result=readKeys(f)
        f.close()
        asymmetryDict["asymmetry_mc"]["mean"].append(result["mean"])
        asymmetryDict["asymmetry_mc"]["rms"].append(diff(total_rms,result["rms"],result["mean"],nominal_mean))
    
    return asymmetryDict
    
folderList=[
    ["mu__cos_theta__mva_-0_2",-0.2],
    ["mu__cos_theta__mva_-0_17",-0.17],
    ["mu__cos_theta__mva_-0_15",-0.15],
    ["mu__cos_theta__mva_-0_12",-0.12],
    ["mu__cos_theta__mva_-0_1",-0.1],
    ["mu__cos_theta__mva_-0_07",-0.07],
    ["mu__cos_theta__mva_-0_05",-0.05],
    ["mu__cos_theta__mva_-0_02",-0.02],
    ["mu__cos_theta__mva_0_0",0.0],
    ["mu__cos_theta__mva_0_02",0.02],
    ["mu__cos_theta__mva_0_05",0.05],
    ["mu__cos_theta__mva_0_07",0.07],
    ["mu__cos_theta__mva_0_1",0.1],
    ["mu__cos_theta__mva_0_12",0.12],
    ["mu__cos_theta__mva_0_15",0.15],
    ["mu__cos_theta__mva_0_17",0.17],
    ["mu__cos_theta__mva_0_2",0.2],
    ["mu__cos_theta__mva_0_22",0.22],
    ["mu__cos_theta__mva_0_25",0.25],
    ["mu__cos_theta__mva_0_27",0.27],
    ["mu__cos_theta__mva_0_3",0.3],
    ["mu__cos_theta__mva_0_32",0.32],
    ["mu__cos_theta__mva_0_35",0.35],
    ["mu__cos_theta__mva_0_37",0.37],
    ["mu__cos_theta__mva_0_4",0.4]
]

folderList=[
    ["mu__cos_theta__mva_-0_4",-0.4],
    ["mu__cos_theta__mva_-0_3",-0.3],
    ["mu__cos_theta__mva_-0_2",-0.2],
    ["mu__cos_theta__mva_-0_1",-0.1],
    ["mu__cos_theta__mva_0_0",0.0],
    ["mu__cos_theta__mva_0_1",0.1],
    ["mu__cos_theta__mva_0_2",0.2],
    ["mu__cos_theta__mva_0_3",0.3],
    ["mu__cos_theta__mva_0_4",0.4],
    ["mu__cos_theta__mva_0_5",0.5]

]

ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetHistLineWidth(3)

asymmetryDict=getAsymmetry(folderList)
canvas = ROOT.TCanvas("canvas","",800,600)
canvas.SetRightMargin(0.23)
canvas.SetGrid(2,2)
axis=ROOT.TH2F("axis",";BDT cut; uncertainty",50,-0.3,0.5,50,min(0.0,min(asymmetryDict["asymmetry_stat"]["rms"]))*1.2,max(asymmetryDict["asymmetry_total"]["rms"])*1.2)
axis.GetYaxis().SetTitleOffset(1.1)
axis.GetXaxis().SetTitleOffset(1.1)
axis.Draw("AXIS")

graphTotal=ROOT.TGraph(len(asymmetryDict["bdt"]),numpy.array(asymmetryDict["bdt"]),numpy.array(asymmetryDict["asymmetry_total"]["rms"]))
setStyle(graphTotal,ROOT.kBlack)
graphTotal.Draw("LP")

graphStat=ROOT.TGraph(len(asymmetryDict["bdt"]),numpy.array(asymmetryDict["bdt"]),numpy.array(asymmetryDict["asymmetry_stat"]["rms"]))
setStyle(graphStat,ROOT.kTeal+2)
graphStat.Draw("LP")

graphSys=ROOT.TGraph(len(asymmetryDict["bdt"]),numpy.array(asymmetryDict["bdt"]),numpy.array(asymmetryDict["asymmetry_sys"]["rms"]))
setStyle(graphSys,ROOT.kAzure-4)
graphSys.Draw("LP")

graphMC=ROOT.TGraph(len(asymmetryDict["bdt"]),numpy.array(asymmetryDict["bdt"]),numpy.array(asymmetryDict["asymmetry_mc"]["rms"]))
setStyle(graphMC,ROOT.kOrange+8)
graphMC.Draw("LP")



legend=ROOT.TLegend(0.78,0.95,0.98,0.6)
legend.SetTextFont(42)
legend.SetFillColor(ROOT.kWhite)
legend.SetBorderSize(0)
legend.AddEntry(graphTotal,"total uncertainty","LP")
legend.AddEntry(graphStat,"statistical","LP")
legend.AddEntry(graphSys,"systematic","LP")
legend.AddEntry(graphMC,"limited MC stat","LP")
legend.Draw("Same")

canvas.Update()
canvas.Print("scan.pdf")
canvas.WaitPrimitive()




















