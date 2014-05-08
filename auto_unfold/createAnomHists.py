from optparse import OptionParser
import ROOT
from ROOT import *
import math
import numpy
import random
import os

gROOT.Reset()
gStyle.SetOptStat(0)
gStyle.SetOptFit(0)
gROOT.Reset()
gROOT.SetStyle("Plain")
gStyle.SetOptStat(0)
gStyle.SetOptFit(1111)
gStyle.SetPadLeftMargin(0.07)
gStyle.SetPadRightMargin(0.25)
gStyle.SetPadBottomMargin(0.15)
gStyle.SetMarkerSize(0.16)
gStyle.SetHistLineWidth(1)
gStyle.SetStatFontSize(0.025)
gStyle.SetTitleFontSize(0.05)
gStyle.SetTitleSize(0.06, "XYZ")
gStyle.SetLabelSize(0.05, "XYZ")
gStyle.SetNdivisions(510, "XYZ")

gStyle.SetOptFit()
gStyle.SetOptStat(0)

# For the canvas:
gStyle.SetCanvasBorderMode(0)
gStyle.SetCanvasColor(TStyle.kWhite)
gStyle.SetCanvasDefH(600) #Height of canvas
gStyle.SetCanvasDefW(600) #Width of canvas
gStyle.SetCanvasDefX(0)   #POsition on screen
gStyle.SetCanvasDefY(0)

# For the Pad:
gStyle.SetPadBorderMode(0)
# gStyle.SetPadBorderSize(Width_t size = 1)
gStyle.SetPadColor(TStyle.kWhite)
gStyle.SetPadGridX(False)
gStyle.SetPadGridY(False)
gStyle.SetGridColor(0)
gStyle.SetGridStyle(2)
gStyle.SetGridWidth(1)

# For the frame:

gStyle.SetFrameBorderMode(0)
gStyle.SetFrameBorderSize(0)
gStyle.SetFrameFillColor(0)
gStyle.SetFrameFillStyle(0)
gStyle.SetFrameLineColor(1)
gStyle.SetFrameLineStyle(1)
gStyle.SetFrameLineWidth(0)

# For the histo:
# gStyle.SetHistFillColor(1)
# gStyle.SetHistFillStyle(0)
gStyle.SetHistLineColor(1)
gStyle.SetHistLineStyle(0)
gStyle.SetHistLineWidth(1)
# gStyle.SetLegoInnerR(Float_t rad = 0.5)
# gStyle.SetNumberContours(Int_t number = 20)

gStyle.SetEndErrorSize(2)
#gStyle.SetErrorMarker(20)
gStyle.SetErrorX(0.)

gStyle.SetMarkerStyle(20)
#gStyle.SetMarkerStyle(20)

#For the fit/function:
gStyle.SetOptFit(1)
gStyle.SetFitFormat("5.4g")
gStyle.SetFuncColor(2)
gStyle.SetFuncStyle(1)
gStyle.SetFuncWidth(1)

#For the date:
gStyle.SetOptDate(0)
# gStyle.SetDateX(Float_t x = 0.01)
# gStyle.SetDateY(Float_t y = 0.01)

# For the statistics box:
gStyle.SetOptFile(0)
gStyle.SetOptStat(0) # To display the mean and RMS:   SetOptStat("mr")
gStyle.SetStatColor(TStyle.kWhite)
gStyle.SetStatFont(42)
gStyle.SetStatFontSize(0.025)
gStyle.SetStatTextColor(1)
gStyle.SetStatFormat("6.4g")
gStyle.SetStatBorderSize(1)
gStyle.SetStatH(0.1)
gStyle.SetStatW(0.15)
# gStyle.SetStatStyle(Style_t style = 1001)
# gStyle.SetStatX(Float_t x = 0)
# gStyle.SetStatY(Float_t y = 0)


#gROOT.ForceStyle(True)
#end modified

# For the Global title:

gStyle.SetOptTitle(0)
gStyle.SetTitleFont(42)
gStyle.SetTitleColor(1)
gStyle.SetTitleTextColor(1)
gStyle.SetTitleFillColor(10)
gStyle.SetTitleFontSize(0.03)
# gStyle.SetTitleH(0) # Set the height of the title box
# gStyle.SetTitleW(0) # Set the width of the title box
#gStyle.SetTitleX(0.35) # Set the position of the title box
#gStyle.SetTitleY(0.986) # Set the position of the title box
# gStyle.SetTitleStyle(Style_t style = 1001)
#gStyle.SetTitleBorderSize(0)

# For the axis titles:
gStyle.SetTitleColor(1, "XYZ")
gStyle.SetTitleFont(42, "XYZ")
#gStyle.SetTitleSize(0.06, "XYZ")
gStyle.SetTitleSize(0.05, "XYZ")
# gStyle.SetTitleXSize(Float_t size = 0.02) # Another way to set the size?
# gStyle.SetTitleYSize(Float_t size = 0.02)
gStyle.SetTitleXOffset(0.95)
gStyle.SetTitleYOffset(1.2)
#gStyle.SetTitleOffset(1.1, "Y") # Another way to set the Offset

# For the axis labels:

gStyle.SetLabelColor(1, "XYZ")
gStyle.SetLabelFont(42, "XYZ")
gStyle.SetLabelOffset(0.0075, "XYZ")
gStyle.SetLabelSize(0.04, "XYZ")
#gStyle.SetLabelSize(0.04, "XYZ")

# For the axis:

gStyle.SetAxisColor(1, "XYZ")
gStyle.SetStripDecimals(True)
gStyle.SetTickLength(0.03, "XYZ")
gStyle.SetNdivisions(510, "XYZ")

gStyle.SetPadTickX(1)  # To get tick marks on the opposite side of the frame
gStyle.SetPadTickY(1)

# Change for log plots:
gStyle.SetOptLogx(0)
gStyle.SetOptLogy(0)
gStyle.SetOptLogz(0)

#gStyle.SetPalette(1) #(1,0)

# another top group addition
gStyle.SetHatchesSpacing(1.0)

# Postscript options:
#gStyle.SetPaperSize(20., 20.)
#gStyle.SetPaperSize(TStyle.kA4)
#gStyle.SetPaperSize(27., 29.7)
#gStyle.SetPaperSize(27., 29.7)
TGaxis.SetMaxDigits(3)
gStyle.SetLineScalePS(2)

# gStyle.SetLineStyleString(Int_t i, const char* text)
# gStyle.SetHeaderPS(const char* header)
# gStyle.SetTitlePS(const char* pstitle)
#gStyle.SetColorModelPS(1)

# gStyle.SetBarOffset(Float_t baroff = 0.5)
# gStyle.SetBarWidth(Float_t barwidth = 0.5)
# gStyle.SetPaintTextFormat(const char* format = "g")
# gStyle.SetPalette(Int_t ncolors = 0, Int_t* colors = 0)
# gStyle.SetTimeOffset(Double_t toffset)
# gStyle.SetHistMinimumZero(kTRUE)



rootObj=[]

def reweightVLVR(name,vl,vr,histSM,histUnPhys,histBSM):
    if type(histSM)==type(ROOT.TH1D()):
        result = ROOT.TH1D(histSM)
    elif type(histSM)==type(ROOT.TH2D()):
        result = ROOT.TH2D(histSM)
    name = name+"__VL_%04i__VR_%04i"%(int(vl*1000),int(vr*1000))
    #print name
    result.SetName(name)
    rootObj.append(result)
    gammaTop=1.49
    w1000=gammaTop
    wart=gammaTop
    w0100=gammaTop
    wtot=gammaTop*(vl**2+vr**2)
    m=vl**4*w1000/wtot
    n=vl**2*vr**2*wart/wtot
    k=vr**4*w0100/wtot
    result.Scale(0.0)
    result.Add(histSM,m)
    result.Add(histUnPhys,n)
    result.Add(histBSM,k)
    #result.Scale(1.0/result.Integral())
    #print "vl=",vl,", vr=",vr,"| (m,n,k)=",m,n,k
    return result
    
def asymmetry(hist):
    sumUp=0.0
    sumDown=0.0
    for ibin in range(hist.GetNbinsX()):
        if hist.GetBinCenter(ibin+1)>0.0:
            sumUp+=hist.GetBinContent(ibin+1)
        else:
            sumDown+=hist.GetBinContent(ibin+1)
    return (sumUp-sumDown)/(sumUp+sumDown)
    
if __name__=="__main__":
    parser=OptionParser()
    parser.add_option("--input", action="store", type="string", dest="input", help="name of the input file")
    parser.add_option("--addinput", action="store", type="string", default="bla", dest="addinput", help="name of add. input file")
    parser.add_option("--output", action="store", type="string", dest="output", help="name of the output file")
    parser.add_option("--inputHistSMCuts", action="store", type="string", dest="inputHistSMCuts", help="name of the nominal SM signal after cuts")
    parser.add_option("--inputHistUnPhysCuts", action="store", type="string", dest="inputHistUnPhysCuts", help="name of the unphys. signal after cuts")
    parser.add_option("--inputHistBSMCuts", action="store", type="string", dest="inputHistBSMCuts", help="name of the BSM signal after cuts")
    parser.add_option("--inputHistSM", action="store", type="string", dest="inputHistSM", help="name of the nominal SM signal")
    parser.add_option("--inputHistUnPhys", action="store", type="string", dest="inputHistUnPhys", help="name of the unphys. signal")
    parser.add_option("--inputHistBSM", action="store", type="string", dest="inputHistBSM", help="name of the BSM signal")
    
    parser.add_option("--inputTMSM", action="store", type="string", dest="inputTMSM", help="name of the nominal SM signal TM")
    parser.add_option("--inputTMUnPhys", action="store", type="string", dest="inputTMUnPhys", help="name of the unphys. signal TM")
    parser.add_option("--inputTMBSM", action="store", type="string", dest="inputTMBSM", help="name of the BSM signal TM")
    
    parser.add_option("--VLVR",action="store_true", default=False, dest="runVLVR", help="use VLVR reweighting equation")
    parser.add_option("-n","--number",action="store", type="int", default=2, dest="number", help="number of points")
    (options, args)=parser.parse_args()
    
    inputFile=ROOT.TFile(options.input,"R")
    print inputFile
    inputFileAdd=ROOT.TFile(options.addinput,"R")
    outputFile=ROOT.TFile(options.output,"RECREATE")
    objectList = [key.GetName() for key in inputFile.GetListOfKeys()]
    #print objectList
    
    
    for objName in objectList:
        print "copy",objName
        objRef = inputFile.Get(objName)
        objRef.SetDirectory(outputFile)
        objRef.Write()
    
    
    if inputFileAdd:
        objectList = [key.GetName() for key in inputFileAdd.GetListOfKeys()]
        for objName in objectList:
            print "copy",objName
            objRef = inputFileAdd.Get(objName)
            objRef.SetDirectory(outputFile)
            objRef.Write()
    inputFileAdd.Close()
    '''
    Number = 5
    Red   = [0.00, 0.00, 0.87, 1.00, 0.71]
    Green = [ 0.00, 0.81, 1.00, 0.20, 0.00]
    Blue   =[  0.71, 1.00, 0.12, 0.00, 0.00]
    Length = [ 0.00, 0.34, 0.61, 0.84, 1.00 ]
    nb=options.number
    start = ROOT.TColor.CreateGradientColorTable(Number,numpy.array(Length),numpy.array(Red),numpy.array(Green),numpy.array(Blue),nb)
    '''
    histSMCuts=inputFile.Get(options.inputHistSMCuts)
    histUnPhysCuts=inputFile.Get(options.inputHistUnPhysCuts)
    histBSMCuts=inputFile.Get(options.inputHistBSMCuts)
    
    histSM=inputFile.Get(options.inputHistSM)
    histUnPhys=inputFile.Get(options.inputHistUnPhys)
    histBSM=inputFile.Get(options.inputHistBSM)
    
    tmSM=inputFile.Get(options.inputTMSM)
    tmUnPhys=inputFile.Get(options.inputTMUnPhys)
    tmBSM=inputFile.Get(options.inputTMBSM)
    
    print histSMCuts,histUnPhysCuts,histBSMCuts
    print histSM,histUnPhys,histBSM
    print tmSM,tmUnPhys,tmBSM
    
    histSMCuts.SetDirectory(outputFile)
    histUnPhysCuts.SetDirectory(outputFile)
    histBSMCuts.SetDirectory(outputFile)
    
    histSM.SetDirectory(outputFile)
    histUnPhys.SetDirectory(outputFile)
    histBSM.SetDirectory(outputFile)
    
    tmSM.SetDirectory(outputFile)
    tmUnPhys.SetDirectory(outputFile)
    tmBSM.SetDirectory(outputFile)

    for i in range(options.number):
        vl = 1.0#-1.0*i/(options.number-1)
        vr = 0.0+1.0*i/(options.number-1)
        if math.fabs(vl)<0.1 and math.fabs(vr)<0.1:
            continue
        resultGen = reweightVLVR("gen",vl,vr,histSM,histUnPhys,histBSM)
        resultCuts = reweightVLVR("cuts",vl,vr,histSMCuts,histUnPhysCuts,histBSMCuts)
        resultTM = reweightVLVR("tm",vl,vr,tmSM,tmUnPhys,tmBSM)
        print "vl=",vl,", vr=",vr," A=",round(asymmetry(resultGen),3)
        resultGen.SetDirectory(outputFile)
        resultGen.Write()
        resultCuts.SetDirectory(outputFile)
        resultCuts.Write()
        resultTM.SetDirectory(outputFile)
        resultTM.Write()
    outputFile.Close()
    inputFile.Close()
    
    
    
