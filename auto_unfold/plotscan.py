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
    
    
def setStyle(graph,color):
    graph.SetMarkerStyle(21)
    graph.SetLineColor(color)
    graph.SetLineWidth(2)
    graph.SetMarkerColor(color)
    graph.SetMarkerSize(0.5)
    
rootObj=[]
    
def createGraphRMSDiff(asymmetryDict,total,sys):
    rmsDiff=numpy.zeros(len(asymmetryDict[total]["rms"]))
    for i in range(len(asymmetryDict[total]["rms"])):
        
        rmsDiff[i]=math.sqrt(max(0.0,asymmetryDict[total]["rms"][i]**2-asymmetryDict[sys]["rms"][i]**2))
    graph=ROOT.TGraph(len(asymmetryDict["bdt"]),numpy.array(asymmetryDict["bdt"]),rmsDiff)
    rootObj.append(graph)
    return graph
    
def createGraphRMS(asymmetryDict,sys):
    graph=ROOT.TGraph(len(asymmetryDict["bdt"]),numpy.array(asymmetryDict["bdt"]),numpy.array(asymmetryDict[sys]["rms"]))
    rootObj.append(graph)
    return graph
    
def createGraphMean(asymmetryDict,sys,shift=0.01):
    bdtshift=numpy.zeros(len(asymmetryDict["bdt"]))
    
    for i in range(len(asymmetryDict["bdt"])):
        bdtshift[i]=asymmetryDict["bdt"][i]#+shift
    
    #graph=ROOT.TGraphErrors(len(asymmetryDict["bdt"]),bdtshift,numpy.array(asymmetryDict[sys]["mean"]),numpy.zeros(len(asymmetryDict["bdt"])),numpy.array(asymmetryDict[sys]["rms"]))
    graph=ROOT.TGraph(len(asymmetryDict["bdt"]),bdtshift,numpy.array(asymmetryDict[sys]["mean"]))
    rootObj.append(graph)
    return graph
    
def getAsymmetry(folder,basefolder=""):
    try:
        asymmetryDict ={"bdt":[folder[1]]}
        
        modeList = os.listdir(os.path.join(basefolder,folder[0]))
        for m in modeList:
            
            f = open(os.path.join(basefolder,folder[0],m,"asymmetry.txt"),"r")
            result=readKeys(f)
            f.close()
            asymmetryDict[m]=result
        
        return asymmetryDict
    except Exception,e :
        print folder,e
    return None
    
basefolder="ele/scan"
folderList=[]
for f in os.listdir(basefolder):
    if (os.path.isdir(os.path.join(basefolder,f))):
        try:
            n=float(f)
            folderList.append([f,n])
        except Exception,e :
            print f,e


sorted(folderList,key=itemgetter(1))
'''
folderList=[
    ["-0.20000",-0.2],
    ["-0.15000",-0.15],
    ["-0.10000",-0.1],
    ["-0.05000",-0.05],
    ["0.00000",0.0],
    ["-0.05000",0.05],
    ["0.10000",0.1],
    ["0.15000",0.15],
    ["0.20000",0.2],
    ["0.25000",0.25],
    ["0.30000",0.3],
    ["0.35000",0.35],
    ["0.40000",0.4],
    ["0.45000",0.45],
    ["0.50000",0.5],
    ["0.55000",0.55],
    ["0.60000",0.6],
    ["0.65000",0.65],
    ["0.70000",0.7],
    ["0.75000",0.75],
    ["0.80000",0.8],
    ["0.85000",0.85],
    ["0.90000",0.9]
]
'''

ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetHistLineWidth(3)

asymmetryDict ={}
for folder in folderList:
    resultDict=getAsymmetry(folder,basefolder=basefolder)
    if (resultDict==None):
        continue
    for key in resultDict.keys():
        if type(resultDict[key])==types.DictType:
            if not asymmetryDict.has_key(key):
                asymmetryDict[key]={}
            for key2 in resultDict[key].keys():
                if not asymmetryDict[key].has_key(key2):
                    asymmetryDict[key][key2]=[]
                asymmetryDict[key][key2].append(resultDict[key][key2])
        elif type(resultDict[key])==types.ListType:
            if not asymmetryDict.has_key(key):
                asymmetryDict[key]=[]
            asymmetryDict[key].append(resultDict[key][0])
        

indices=numpy.argsort(asymmetryDict["bdt"])
for key in asymmetryDict.keys():
    if type(resultDict[key])==types.DictType:
        for key2 in asymmetryDict[key].keys():
            asymmetryDict[key][key2]=numpy.array(asymmetryDict[key][key2])[indices]
    if type(resultDict[key])==types.ListType:
        asymmetryDict[key]=numpy.array(asymmetryDict[key])[indices]


Number = 5
Red   = [0.00, 0.00, 0.87, 1.00, 0.71]
Green = [ 0.00, 0.81, 1.00, 0.20, 0.00]
Blue   =[  0.71, 1.00, 0.12, 0.00, 0.00]
Length = [ 0.00, 0.34, 0.61, 0.84, 1.00 ]
nb=12
start = ROOT.TColor.CreateGradientColorTable(Number,numpy.array(Length),numpy.array(Red),numpy.array(Green),numpy.array(Blue),nb)



canvas1 = ROOT.TCanvas("canvas1","",800,600)
canvas1.SetRightMargin(0.23)
canvas1.SetGrid(2,2)
axis1=ROOT.TH2F("axis1",";BDT cut; uncertainty",50,-0.25,0.85,50,0.0,max(asymmetryDict["total"]["rms"])*1.1)
axis1.GetYaxis().SetTitleOffset(1.1)
axis1.GetXaxis().SetTitleOffset(1.1)
axis1.Draw("AXIS")

legend1=ROOT.TLegend(0.78,0.95,0.98,0.45)
legend1.SetTextFont(42)
legend1.SetFillColor(ROOT.kWhite)
legend1.SetBorderSize(0)

graphTotal1=ROOT.TGraph(len(asymmetryDict["bdt"]),numpy.array(asymmetryDict["bdt"]),numpy.array(asymmetryDict["total"]["rms"]))
setStyle(graphTotal1,ROOT.kBlack)
graphTotal1.Draw("CP")
legend1.AddEntry(graphTotal1,"total uncertainty","LP")

systematics = [
    ["sysexcl","all systematics",ROOT.kGray],
    ["statexcl","statistical",start+1],
    ["btagexcl","b-tagging",start+2],
    ["jesexcl","JES",start+3],
    ["massexcl","top mass",start+4],
    ["matchingexcl","matching",start+5],
    ["mcexcl","limited MC",start+6],
    ["puexcl","PU",start+7],
    ["scaleexcl","Q scale",start+8],
    ["wjets_shapeexcl","WJets shape",start+9],
    ["xsecexcl","fit uncertainties",start+10],
    ["topptexcl","top pT",start+11]
]

for i in range(len(systematics)):
    sys = systematics[i]
    graph = createGraphRMSDiff(asymmetryDict,"total",sys[0])
    setStyle(graph,sys[2])
    graph.SetLineStyle(1+i%2)
    graph.Draw("CP")
    legend1.AddEntry(graph,sys[1],"LP")
    
legend1.Draw("Same")

canvas1.Update()
canvas1.Print(os.path.join(basefolder,"scan_ex.pdf"))
#canvas.WaitPrimitive()



canvas2 = ROOT.TCanvas("canvas2","",800,600)
canvas2.SetRightMargin(0.23)
canvas2.SetGrid(2,2)
axis2=ROOT.TH2F("axis2",";BDT cut; uncertainty",50,-0.25,0.85,50,0.0,max(asymmetryDict["total"]["rms"])*1.1)
axis2.GetYaxis().SetTitleOffset(1.1)
axis2.GetXaxis().SetTitleOffset(1.1)
axis2.Draw("AXIS")

legend2=ROOT.TLegend(0.78,0.95,0.98,0.45)
legend2.SetTextFont(42)
legend2.SetFillColor(ROOT.kWhite)
legend2.SetBorderSize(0)

graphTotal2=ROOT.TGraph(len(asymmetryDict["bdt"]),numpy.array(asymmetryDict["bdt"]),numpy.array(asymmetryDict["total"]["rms"]))
setStyle(graphTotal2,ROOT.kBlack)
graphTotal2.Draw("CP")
legend2.AddEntry(graphTotal2,"total uncertainty","LP")
   
    
systematics = [
    ["statexcl","all systematics",ROOT.kGray],
    ["sysexcl","statistical",start+1],
    ["btaginc","b-tagging",start+2],
    ["jesinc","JES",start+3],
    ["massinc","top mass",start+4],
    ["matchinginc","matching",start+5],
    ["mcinc","limited MC",start+6],
    ["puinc","PU",start+7],
    ["scaleinc","Q scale",start+8],
    ["wjets_shapeinc","WJets shape",start+9],
    ["xsecinc","fit uncertainties",start+10],
    ["topptinc","top pT",start+11]
]


for i in range(len(systematics)):
    sys = systematics[i]
    graph = createGraphRMS(asymmetryDict,sys[0])
    setStyle(graph,sys[2])
    graph.SetLineStyle(1+i%2)
    graph.Draw("CP")
    
    legend2.AddEntry(graph,sys[1],"LP")

legend2.Draw("Same")

canvas2.Update()
canvas2.Print(os.path.join(basefolder,"scan_inc.pdf"))








canvas3 = ROOT.TCanvas("canvas3","",800,600)
canvas3.SetRightMargin(0.23)
canvas3.SetGrid(2,2)
axis3=ROOT.TH2F("axis3",";BDT cut; asymmetry",50,-0.25,0.85,50,(min(asymmetryDict["total"]["mean"])-max(asymmetryDict["total"]["rms"]))*0.9,(max(asymmetryDict["total"]["mean"])+max(asymmetryDict["total"]["rms"]))*1.1)
axis3.GetYaxis().SetTitleOffset(1.1)
axis3.GetXaxis().SetTitleOffset(1.1)
axis3.Draw("AXIS")

legend3=ROOT.TLegend(0.78,0.95,0.98,0.45)
legend3.SetTextFont(42)
legend3.SetFillColor(ROOT.kWhite)
legend3.SetBorderSize(0)

graphTotal3=ROOT.TGraphErrors(len(asymmetryDict["bdt"]),numpy.array(asymmetryDict["bdt"]),numpy.array(asymmetryDict["total"]["mean"]),numpy.zeros(len(asymmetryDict["total"]["rms"])),numpy.array(asymmetryDict["total"]["rms"]))
setStyle(graphTotal3,ROOT.kBlack)
graphTotal3.Draw("CP")
legend3.AddEntry(graphTotal3,"total uncertainty","LP")
   
    
systematics = [
    ["statexcl","all systematics",ROOT.kGray],
    ["sysexcl","statistical",start+1],
    ["btaginc","b-tagging",start+2],
    ["jesinc","JES",start+3],
    ["massinc","top mass",start+4],
    ["matchinginc","matching",start+5],
    ["mcinc","limited MC",start+6],
    ["puinc","PU",start+7],
    ["scaleinc","Q scale",start+8],
    ["wjets_shapeinc","WJets shape",start+9],
    ["xsecinc","fit uncertainties",start+10],
    ["topptinc","top pT",start+11]
]

systematics = [
    ["sysexcl","all systematics",ROOT.kGray],
    ["statexcl","statistical",start+1],
    ["btagexcl","b-tagging",start+2],
    ["jesexcl","JES",start+3],
    ["massexcl","top mass",start+4],
    ["matchingexcl","matching",start+5],
    ["mcexcl","limited MC",start+6],
    ["puexcl","PU",start+7],
    ["scaleexcl","Q scale",start+8],
    ["wjets_shapeexcl","WJets shape",start+9],
    ["xsecexcl","fit uncertainties",start+10],
    ["topptexcl","top pT",start+11]
]

for i in range(len(systematics)):
    sys = systematics[i]
    graph = createGraphMean(asymmetryDict,sys[0],i*0.004+0.004)
    setStyle(graph,sys[2])
    graph.SetLineStyle(1+i%2)
    graph.Draw("CP")
    
    legend3.AddEntry(graph,sys[1],"LP")

legend3.Draw("Same")

canvas3.Update()
canvas3.Print(os.path.join(basefolder,"scan_mean.pdf"))
canvas3.WaitPrimitive()




















