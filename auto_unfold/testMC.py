import ROOT
import math
import numpy
ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetPaintTextFormat(".2f")
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetPadTopMargin(0.02)
ROOT.gStyle.SetPadLeftMargin(0.12)
ROOT.gStyle.SetPadRightMargin(0.15)
ROOT.gStyle.SetPadBottomMargin(0.1)
ROOT.gStyle.SetTitleSize(0.04,"XYZ")
ROOT.gStyle.SetLabelSize(0.05,"XY")
ROOT.gStyle.SetLabelSize(0.03,"Z")


def calculateAsymmetry(hist):
    sumUp=0.0
    sumUpStatError=0.0
    sumUpMCError=0.0
    sumDown=0.0
    sumDownStatError=0.0
    sumDownMCError=0.0
    for ibin in range(hist.GetNbinsX()):
        if hist.GetBinCenter(ibin+1)>0.0:
            sumUp+=hist.GetBinContent(ibin+1)
            sumUpStatError+=hist.GetBinContent(ibin+1)
            sumUpMCError+=hist.GetBinError(ibin+1)**2
        else:
            sumDown+=hist.GetBinContent(ibin+1)
            sumDownStatError+=hist.GetBinContent(ibin+1)
            sumDownMCError+=hist.GetBinError(ibin+1)**2
    sumUpStatError=math.sqrt(sumUpStatError)
    sumDownStatError=math.sqrt(sumDownStatError)
    sumUpMCError=math.sqrt(sumUpMCError)
    sumDownMCError=math.sqrt(sumDownMCError)
    
    asymmetry=(sumUp-sumDown)/(sumUp+sumDown)
    asymmetryStatError=math.sqrt((2*sumDown/(sumUp+sumDown)**2)**2*sumUpStatError**2+(2*sumUp/(sumUp+sumDown)**2)**2*sumDownStatError**2)
    asymmetryMCError=math.sqrt((2*sumDown/(sumUp+sumDown)**2)**2*sumUpMCError**2+(2*sumUp/(sumUp+sumDown)**2)**2*sumDownMCError**2)
    return asymmetry,asymmetryStatError,asymmetryMCError

def copyBinning(hist):
    nbins=hist.GetNbinsX()
    binning=numpy.zeros(nbins+1)
    for ibin in range(nbins+1):
        binning[ibin]=float(hist.GetBinLowEdge(ibin+1))
    #print binning
    return ROOT.TH1F(hist.GetName()+"_copy","",nbins,binning)
                
def sumHistograms(fileWeighted,fileUnweighted,nameList,output):
    histSum=copyBinning(fileWeighted.Get(nameList[0]))

    histIndividualErrorsMC=ROOT.TH2F("indMC","",histSum.GetNbinsX(),0.0,histSum.GetNbinsX(),len(nameList)+1,0.0,len(nameList)+1)
    histIndividualErrorsMC.GetXaxis().SetTitle("bin")
    histIndividualErrorsMC.GetZaxis().SetTitle("MC")
    histIndividualErrorsStat=ROOT.TH2F("indStat","",histSum.GetNbinsX(),0.0,histSum.GetNbinsX(),len(nameList)+1,0.0,len(nameList)+1)
    histIndividualErrorsStat.GetXaxis().SetTitle("bin")
    histIndividualErrorsStat.GetZaxis().SetTitle("stat.")
    for ihist in range(len(nameList)):
        binName=nameList[ihist].rsplit("_",1)[1]
        histIndividualErrorsMC.GetYaxis().SetBinLabel(ihist+1,binName)
        histIndividualErrorsStat.GetYaxis().SetBinLabel(ihist+1,binName)
    histIndividualErrorsMC.GetYaxis().SetBinLabel(len(nameList)+1,"sum")
    histIndividualErrorsStat.GetYaxis().SetBinLabel(len(nameList)+1,"sum")
    for ibin in range(histSum.GetNbinsX()):
        histIndividualErrorsMC.GetXaxis().SetBinLabel(ibin+1,str(ibin+1))
        histIndividualErrorsStat.GetXaxis().SetBinLabel(ibin+1,str(ibin+1))
    
    for ibin in range(histSum.GetNbinsX()):
        binSum=0.0
        binSumError=0.0
        for iName in range(len(nameList)):
            histName=nameList[iName]
            histWeighted=fileWeighted.Get(histName)
            obs=histWeighted.GetBinContent(ibin+1)
            obsError=histWeighted.GetBinError(ibin+1)
            histUnweighted=fileUnweighted.Get(histName)
            n=histUnweighted.GetBinContent(ibin+1)
            
            binSum+=obs
            if n>0:
                binSumError+=obsError**2
            else:
                
                obsError=histWeighted.Integral()/math.sqrt(histUnweighted.Integral())/16.0
                obs=0.5
            histIndividualErrorsMC.SetBinContent(ibin+1,iName+1,obsError)
            histIndividualErrorsStat.SetBinContent(ibin+1,iName+1,math.sqrt(obs))
        binSumError=math.sqrt(binSumError)
        
        histIndividualErrorsMC.SetBinContent(ibin+1,len(nameList)+1,binSumError)
        histIndividualErrorsStat.SetBinContent(ibin+1,len(nameList)+1,math.sqrt(binSum))
        
        histSum.SetBinContent(ibin+1,binSum)
        histSum.SetBinError(ibin+1,binSumError)
    canvasInd=ROOT.TCanvas("individual"+nameList[0],"",1000,800)
    canvasInd.Divide(2,2)
    canvasInd.cd(1)
    histIndividualErrorsMC.Draw("colz text")
    canvasInd.cd(2)
    histIndividualErrorsStat.Draw("colz text")
    canvasInd.cd(3)
    histIndividualErrorsRatio=histIndividualErrorsMC.Clone()
    histIndividualErrorsRatio.GetZaxis().SetTitle("MC / stat.")
    histIndividualErrorsRatio.Divide(histIndividualErrorsStat)
    histIndividualErrorsRatio.Draw("colz text")
    
    
    canvasInd.cd(4)
    weightSummary=sanityCheck(fileWeighted,fileUnweighted,nameList)
    paveWeight=ROOT.TPaveText(0.1,0.9,0.45,0.1,"NDC")
    paveWeight.SetBorderSize(0)
    paveWeight.SetFillColor(ROOT.kWhite)
    paveWeight.SetTextFont(42)
    paveWeight.AddText("weights")
    for i in range(len(nameList)):
        paveWeight.AddText(weightSummary["name"][i]+": <w>="+str(round(weightSummary["avgw"][i],4)))
    
    paveWeight.Draw()
    
    
    asymmetry,asymmetryStatError,asymmetryMCError=calculateAsymmetry(histSum)
    paveAsymmetry=ROOT.TPaveText(0.6,0.9,0.95,0.6,"NDC")
    paveAsymmetry.SetBorderSize(0)
    paveAsymmetry.SetFillColor(ROOT.kWhite)
    paveAsymmetry.SetTextFont(42)
    paveAsymmetry.AddText("asymmetry (reco)")
    paveAsymmetry.AddText(str(round(asymmetryStatError,4))+" (stat.)")
    paveAsymmetry.AddText(str(round(asymmetryMCError,4))+" (MC)")
    paveAsymmetry.Draw("Same")
    
    
    
    canvasInd.Update()
    canvasInd.Print(output)
    canvasInd.WaitPrimitive()
    return histSum
    
def sanityCheck(fileWeighted,fileUnweighted,nameList):
    result={"name":[],"avgw":[],"relrms":[]}
    for histName in nameList:
        histWeighted=fileWeighted.Get(histName)
        histUnweighted=fileUnweighted.Get(histName)
        avgWeight=0.0
        avgWeight2=0.0
        nWeight=0
        for ibin in range(histWeighted.GetNbinsX()):
            
            obs=histWeighted.GetBinContent(ibin+1)
            obsErr=histWeighted.GetBinError(ibin+1)
            n=histUnweighted.GetBinContent(ibin+1)
            if n>0:
                avgWeight+=obsErr**2/obs
                avgWeight2+=(obsErr**2/obs)**2
                nWeight+=1
        print histName,"avg w=",round(avgWeight/nWeight,4)#,"relrms=",round(math.sqrt(avgWeight2/nWeight-(avgWeight/nWeight)**2)/(avgWeight/nWeight)*100.0,1),"%"
        result["name"].append(histName.rsplit("_",1)[1])
        result["avgw"].append(avgWeight/nWeight)
        #result["relrms"].append(math.sqrt(avgWeight2/nWeight-(avgWeight/nWeight)**2)/(avgWeight/nWeight))
    return result


histList=[
"cos_theta__tchan",
"cos_theta__dyjets",
"cos_theta__qcd",
"cos_theta__ttbar",
"cos_theta__schan",
"cos_theta__tWchan",
"cos_theta__wjets",
"cos_theta__dibosons"
]
#checkHistError(fileWeighted,fileUnweighted,backgroundList)
fileWeighted=ROOT.TFile("/home/fynu/mkomm/mu__cos_theta__mva_0_0__all_components_weighted/data.root")
fileUnweighted=ROOT.TFile("/home/fynu/mkomm/mu__cos_theta__mva_0_0__all_components_unweighted/data.root")
sumHistograms(fileWeighted,fileUnweighted,histList,"uncertaintyAnalysis__mu__mva_0_0.pdf")




