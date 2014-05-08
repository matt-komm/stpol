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
    graph.SetMarkerSize(0.5)
    
def getAsymmetry(folder,basefolder=""):
    asymmetryDict ={
                    "gen":[],"asymmetry":{"mean":[], "rms":[]},"vl":[],"vr":[]
                    }
    
    f = open(os.path.join(basefolder,folder[0],"asymmetry.txt"),"r")
    result=readKeys(f)
    f.close()
    asymmetryDict["gen"].append(result["gen"])
    asymmetryDict["asymmetry"]["mean"].append(result["mean"])
    asymmetryDict["asymmetry"]["rms"].append(result["rms"])
    asymmetryDict["vl"].append(folder[1])
    asymmetryDict["vr"].append(folder[2])
    return asymmetryDict
    
    
basefolder="muon/neyman_cplx"



folderList=[]
n=21
for i in range(n):
    vl=1.0
    vr=1.0*i/(n-1)
    folderName="VL_%04i__VR_%04i"%(int(vl*1000),int(vr*1000))
    folderList.append([folderName,vl,vr])

ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetHistLineWidth(3)

asymmetryDict ={
    "gen":[],"asymmetry":{"mean":[], "rms":[]},"vl":[],"vr":[]
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
asymmetryDict["vl"]=numpy.array(asymmetryDict["vl"])[indices]
asymmetryDict["vr"]=numpy.array(asymmetryDict["vr"])[indices]

canvas = ROOT.TCanvas("canvas","",800,600)
canvas.SetRightMargin(0.23)
canvas.SetGrid(2,2)
axis=ROOT.TH2F("axis","; A_{reco}; A_{gen}",50,0.0,0.52,50,0.0,0.52)
axis.GetYaxis().SetTitleOffset(1.1)
axis.GetXaxis().SetTitleOffset(1.1)
axis.Draw("AXIS")

errorX=[]
errorY=[]
for i in range(len(asymmetryDict["gen"])):
    rms = asymmetryDict["asymmetry"]["rms"][i]
    errorX.append(asymmetryDict["asymmetry"]["mean"][i]-rms)
    errorY.append(asymmetryDict["gen"][i])
for i in range(1,len(asymmetryDict["gen"])+1):
    rms = asymmetryDict["asymmetry"]["rms"][-i]
    errorX.append(asymmetryDict["asymmetry"]["mean"][-i]+rms)
    errorY.append(asymmetryDict["gen"][-i])
polyError = ROOT.TPolyLine(len(errorX),numpy.array(errorX),numpy.array(errorY))
polyError.SetFillColor(ROOT.kGray)
polyError.SetFillStyle(1001)
polyError.Draw("F")

graphTotal=ROOT.TGraph(len(asymmetryDict["gen"]),numpy.array(asymmetryDict["asymmetry"]["mean"]),numpy.array(asymmetryDict["gen"]))
setStyle(graphTotal,ROOT.kBlack)
graphTotal.Draw("L")

legend=ROOT.TLegend(0.78,0.95,0.98,0.15)
legend.SetTextFont(42)
legend.SetFillColor(ROOT.kWhite)
legend.SetBorderSize(0)


Number = 5
Red   = [0.00, 0.00, 0.87, 1.00, 0.71]
Green = [ 0.00, 0.81, 1.00, 0.20, 0.00]
Blue   =[  0.71, 1.00, 0.12, 0.00, 0.00]
Length = [ 0.00, 0.34, 0.61, 0.84, 1.00 ]
nb=len(asymmetryDict["gen"])
start = ROOT.TColor.CreateGradientColorTable(Number,numpy.array(Length),numpy.array(Red),numpy.array(Green),numpy.array(Blue),nb)


rootObj=[]
for i in range(len(asymmetryDict["gen"])):
    genA=asymmetryDict["gen"][i]
    recoA=asymmetryDict["asymmetry"]["mean"][i]
    vl=asymmetryDict["vl"][i]
    vr=asymmetryDict["vr"][i]
    legendName="VL=%4.3f VR=%4.3f"%(vl,vr)
    marker = ROOT.TMarker(recoA,genA,21)
    rootObj.append(marker)
    marker.SetMarkerColor(start+i)
    marker.Draw("Same")
    legend.AddEntry(marker,legendName,"P")

angleBi=ROOT.TF1("angleBi","x",-1.0,1.0)
angleBi.SetLineColor(ROOT.kRed+1)
angleBi.SetLineStyle(2)
angleBi.SetLineWidth(3)
angleBi.Draw("SameL")

fit=ROOT.TF1("fit","pol1",-1.0,1.0)
fit.SetLineColor(ROOT.kBlue+1)
fit.SetLineStyle(2)
fit.SetLineWidth(3)
graphTotal.Fit(fit,"NQR")
fit.Draw("SameL")

axis.Draw("Same AXIS")

legend.AddEntry(polyError,"stat. uncertainty","F")
legend.AddEntry(angleBi,"angle bisector","L")
legend.AddEntry(fit,"linear fit","L")
legend.Draw("Same")

canvas.Update()
canvas.Print(os.path.join(basefolder,"neyman.pdf"))
canvas.WaitPrimitive()




















