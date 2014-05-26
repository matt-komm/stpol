import ROOT
import os
import numpy
import math
import sys
import types
from operator import itemgetter, attrgetter

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
    graph.SetFillColor(ROOT.kAzure-4)
    graph.SetMarkerColor(color)
    graph.SetMarkerSize(1.0)
    
def getAsymmetry(folder,basefolder=""):
    asymmetryDict ={
                    "gen":[],"asymmetry":{"mean":[], "rms":[], "data":[]},"tau":[]
                    }
    
    f = open(os.path.join(basefolder,str(folder),"asymmetry.txt"),"r")
    result=readKeys(f)
    f.close()
    asymmetryDict["gen"].append(result["gen"])
    asymmetryDict["asymmetry"]["mean"].append(result["mean"])
    asymmetryDict["asymmetry"]["rms"].append(result["rms"])
    asymmetryDict["tau"].append(folder)
    f = open(os.path.join(basefolder,str(folder)+"_data","asymmetry.txt"),"r")
    result=readKeys(f)
    f.close()
    asymmetryDict["asymmetry"]["data"].append(result["mean"])
    return asymmetryDict
    
    
basefolder="muon/tauscan"



folderList=[0.001,0.005,0.1,0.5,1.0,2.0,5.0,10.0,50.0,100.0]

ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetHistLineWidth(3)

asymmetryDict ={
    "gen":[],"asymmetry":{"mean":[], "rms":[], "data":[]},"tau":[]
}
for folder in folderList:
    try:
        resultDict=getAsymmetry(folder,basefolder=basefolder)
        for key in asymmetryDict.keys():
            if type(asymmetryDict[key])==types.DictType:
                for key2 in asymmetryDict[key].keys():
                    asymmetryDict[key][key2].extend(resultDict[key][key2])
            elif type(asymmetryDict[key])==types.ListType:
                asymmetryDict[key].extend(resultDict[key])
    except Exception, e:
        print e
        
indices=numpy.argsort(asymmetryDict["gen"])
asymmetryDict["gen"]=numpy.array(asymmetryDict["gen"])[indices]
asymmetryDict["asymmetry"]["mean"]=numpy.array(asymmetryDict["asymmetry"]["mean"])[indices]
asymmetryDict["asymmetry"]["rms"]=numpy.array(asymmetryDict["asymmetry"]["rms"])[indices]
asymmetryDict["asymmetry"]["data"]=numpy.array(asymmetryDict["asymmetry"]["data"])[indices]
asymmetryDict["tau"]=numpy.array(asymmetryDict["tau"])[indices]
print asymmetryDict["tau"]
print asymmetryDict["asymmetry"]

canvas = ROOT.TCanvas("canvas","",800,600)
canvas.SetRightMargin(0.23)
canvas.SetGrid(2,2)
axis=ROOT.TH2F("axis","; scale/#tau_{global};A",50,0.0005,200.0,50,0.15,0.6)
axis.GetYaxis().SetTitleOffset(1.1)
axis.GetXaxis().SetTitleOffset(1.1)
axis.Draw("AXIS")
ROOT.gPad.SetLogx(1)


graphTotal=ROOT.TGraphErrors(len(asymmetryDict["tau"]),numpy.array(asymmetryDict["tau"]),numpy.array(asymmetryDict["asymmetry"]["mean"]),numpy.zeros(len(asymmetryDict["tau"])),numpy.array(asymmetryDict["asymmetry"]["rms"]))
setStyle(graphTotal,ROOT.kBlack)
graphTotal.Draw("LP")
graphData=ROOT.TGraph(len(asymmetryDict["tau"]),numpy.array(asymmetryDict["tau"]),numpy.array(asymmetryDict["asymmetry"]["data"]))
setStyle(graphData,ROOT.kMagenta)
graphData.Draw("LP Same")

axis.Draw("Same AXIS")
legend=ROOT.TLegend(0.78,0.95,0.98,0.8)
legend.SetTextFont(42)
legend.SetFillColor(ROOT.kWhite)
legend.SetBorderSize(0)
legend.AddEntry(graphTotal,"MC PE (stat. only)","LPE")
legend.AddEntry(graphData,"data","LP")
legend.Draw("Same")

canvas.Update()
canvas.Print(os.path.join(basefolder,"tauscan.pdf"))
canvas.WaitPrimitive()



















