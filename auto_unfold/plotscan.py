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
    
def getAsymmetry(folderList,basefolder=""):
    asymmetryDict ={
                    "bdt":[],"asymmetry_total":{"mean":[], "rms":[]},
                    "asymmetry_nominal":{"mean":[], "rms":[]},
                    "asymmetry_stat":{"mean":[], "rms":[]},
                    "asymmetry_sys":{"mean":[], "rms":[]},
                    "asymmetry_mc":{"mean":[], "rms":[]}
                    }
    for folder in folderList:
        asymmetryDict["bdt"].append(folder[1])
        
        f = open(os.path.join(basefolder,folder[0],"nosys","asymmetry.txt"),"r")
        result=readKeys(f)
        f.close()
        nominal_mean=result["mean"]
        nominal_rms=result["rms"]
        asymmetryDict["asymmetry_nominal"]["mean"].append(result["mean"])
        asymmetryDict["asymmetry_nominal"]["rms"].append(result["rms"])
        
        
        f = open(os.path.join(basefolder,folder[0],"total","asymmetry.txt"),"r")
        result=readKeys(f)
        f.close()
        total_mean=result["mean"]
        total_rms=result["rms"]
        asymmetryDict["asymmetry_total"]["mean"].append(result["mean"])
        asymmetryDict["asymmetry_total"]["rms"].append(total_rms)
        
        f = open(os.path.join(basefolder,folder[0],"statexcl","asymmetry.txt"),"r")
        result=readKeys(f)
        f.close()
        asymmetryDict["asymmetry_stat"]["mean"].append(result["mean"])
        asymmetryDict["asymmetry_stat"]["rms"].append(math.sqrt(total_rms**2-result["rms"]**2))
        
        f = open(os.path.join(basefolder,folder[0],"sysexcl","asymmetry.txt"),"r")
        result=readKeys(f)
        f.close()
        asymmetryDict["asymmetry_sys"]["mean"].append(result["mean"])
        asymmetryDict["asymmetry_sys"]["rms"].append(math.sqrt(total_rms**2-result["rms"]**2))
        
        f = open(os.path.join(basefolder,folder[0],"mcexcl","asymmetry.txt"),"r")
        result=readKeys(f)
        f.close()
        asymmetryDict["asymmetry_mc"]["mean"].append(result["mean"])
        asymmetryDict["asymmetry_mc"]["rms"].append(math.sqrt(total_rms**2-result["rms"]**2))
    
    return asymmetryDict
    
basefolder="muon/scan"
folderList=[
    ["-0.20000",-0.2],
    ["-0.15000",-0.15],
    ["-0.10000",-0.1],
    ["-0.05000",-0.05],
    ["-0.00000",0.0],
    ["-0.05000",0.05],
    ["0.10000",0.1],
    ["0.15000",0.15],
    ["0.20000",0.2],
    ["0.25000",0.25],
    ["0.30000",0.3],
    ["0.35000",0.35],
    ["0.40000",0.4],
    ["0.45000",0.45],
    ["0.50000",0.5]
]


ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetHistLineWidth(3)

asymmetryDict=getAsymmetry(folderList,basefolder=basefolder)
canvas = ROOT.TCanvas("canvas","",800,600)
canvas.SetRightMargin(0.23)
canvas.SetGrid(2,2)
axis=ROOT.TH2F("axis",";BDT cut; uncertainty",50,-0.25,0.55,50,min(0.0,min(asymmetryDict["asymmetry_stat"]["rms"]))*1.2,max(asymmetryDict["asymmetry_total"]["rms"])*1.2)
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
canvas.Print(os.path.join(basefolder,"scan.pdf"))
canvas.WaitPrimitive()




















