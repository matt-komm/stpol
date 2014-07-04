from optparse import OptionParser
import math
import sys
import numpy
import os
import logging
import ROOT
import shutil
import subprocess
import random
from generateCosThetaModel import *

logging.basicConfig(format="%(levelname)s - %(message)s",level=logging.DEBUG)
#logging.basicConfig(filename="run.log",format="%(levelname)s - %(message)s",level=logging.DEBUG)

ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetStatX(0.4)
ROOT.gStyle.SetStatY(0.98)
ROOT.gStyle.SetOptStat(0)

def parseFitResult(inputfile):
    signalSetDict={}
    backgroundSetDict={}
    dataSetDict={}
    yieldSysDict={}
    shapeSysDict={}
    corrList=[]
    file = open(inputfile,"r")
    ln=0
    for line in file:
        ln+=1
        line=line.replace("\r","").replace("\n","").replace(" ","")
        if line=="" or line.startswith("#"):
            continue
        splitted=line.split(",")
        
        try:
            if splitted[0]=="set":
                if len(splitted)<4:
                    logging.error("Error while reading the fitresult file: "+line)
                    sys.exit(-1)
                if splitted[1]=="signal":
                    signalSetDict[splitted[2]]=splitted[3:]
                elif splitted[1]=="background":
                    backgroundSetDict[splitted[2]]=splitted[3:]
                elif splitted[1]=="data":
                    dataSetDict[splitted[2]]=splitted[3:]
                else:
                    logging.warning("type can only be 'signal' or 'background' - found '"+splitted[1]+"' in line "+str(ln))
            elif splitted[0]=="rate":
                if len(splitted)!=4:
                    logging.error("Error while reading the fitresult file: "+line)
                    sys.exit(-1)
                yieldSysDict[splitted[1]]={"mean":float(splitted[2]),"unc":float(splitted[3])}
            elif splitted[0]=="shape":
                if len(splitted)<4:
                    logging.error("Error while reading the fitresult file: "+line)
                    sys.exit(-1)
                shapeSysDict[splitted[1]]={"mean":float(splitted[2]),"unc":float(splitted[3]),"norm":False, "independent":False}
                for i in range(len(splitted)-4):
                    if splitted[i+4]=="normalize":
                        shapeSysDict[splitted[1]]["norm"]=True
                    elif splitted[i+4]=="independent":
                        shapeSysDict[splitted[1]]["independent"]=True
                    else:
                        logging.error("Error while reading the fitresult file: "+line+" | unreconized command")
                        sys.exit(-1)
            elif splitted[0]=="corr":
                if len(splitted)!=4:
                    logging.error("Error while reading the fitresult file: "+line)
                    sys.exit(-1)
                corrList.append({"name":[splitted[1],splitted[2]],"rho":float(splitted[3])})
            else:
                logging.warning("type not regonized: "+splitted[0])
        except ValueError, e:
            logging.error("parsing of '"+inputfile+"' failed at line "+str(ln))
            logging.error("cannot parse: '"+line+"'")
            logging.error(e.message)
            sys.exit(-1)
    file.close()
    return signalSetDict,backgroundSetDict,dataSetDict,yieldSysDict,shapeSysDict,corrList
    
def getResponseMatrixBinning(responseMatrix):
    fileName,objectName=responseMatrix.rsplit(":",1)
    rootFile = ROOT.TFile(fileName,"r")
    responseMatrix = rootFile.Get(objectName)
    if (not responseMatrix):
        logging.error("response matrix '"+objectName+"' could not be read from file '"+fileName+"'")
        sys.exit(-1)
    measured =  responseMatrix.ProjectionY()
    truth =  responseMatrix.ProjectionX()
    nbinsMeasured=measured.GetNbinsX()
    nbinsTruth=truth.GetNbinsX()
    binningMeasured=numpy.zeros(nbinsMeasured+1)
    binningTruth=numpy.zeros(nbinsMeasured+1)
    for ibin in range(nbinsMeasured+1):
        binningMeasured[ibin]=measured.GetBinLowEdge(ibin+1)
    for ibin in range(nbinsTruth+1):
        binningTruth[ibin]=truth.GetBinLowEdge(ibin+1)
    return binningMeasured,binningTruth
    
def getMeasuredHistogramBinning(histogram):
    fileName,objectName=histogram.rsplit(":",1)
    rootFile = ROOT.TFile(fileName,"r")
    signalHistogram = rootFile.Get(objectName)
    if (not signalHistogram):
        logging.error("histogram '"+objectName+"' in file '"+fileName+"' could not be read")
        sys.exit(-1)
    nbins = signalHistogram.GetNbinsX()
    binning=numpy.zeros(nbins+1)
    for ibin in range(nbins+1):
        binning[ibin]=signalHistogram.GetBinLowEdge(ibin+1)
    return binning
    
def rebinHistograms(fileName,prefix,binningMeasured,folder):
    histo=ROOT.TH1D()
    histoBG=ROOT.TH1D()
    file=ROOT.TFile(os.path.join(folder,fileName))
    tree=file.Get("products")
    
    tree.SetBranchAddress("pd__data_obs_"+prefix, histo)
    #histo.SetDirectory(0)
    
    fileOut=ROOT.TFile(os.path.join(folder,"subtracted_"+fileName),"RECREATE")
    treeOut=ROOT.TTree("subtracted","subtracted")


    histoRebinned=ROOT.TH1D("rebinned","",len(binningMeasured)-1,binningMeasured)
    treeOut.Branch("histos", histoRebinned)
    
    for cnt in range(int(tree.GetEntries())):
        tree.GetEntry(cnt)
        
        for ibin in range(len(binningMeasured)-1):
            y=histo.GetBinContent(ibin+1)
            if (y<0):
                #logging.debug("WARNING: yield after background subtraction smaller than 0: yield="+str(y))
                histoRebinned.SetBinContent(ibin+1,0)
            else:
                histoRebinned.SetBinContent(ibin+1,y)
        treeOut.Fill()
    
    treeOut.Write()
    fileOut.Close()
    file.Close()
    
def plotThetaHistograms(thetaFile):
    histo=ROOT.TH1D()
    inFile = ROOT.TFile(thetaFile)
    tree=inFile.Get("products")
    #tree.SetBranchAddress("pd__data_obs_"+prefix, histo)
    branchList = tree.GetListOfBranches()
    for index in range(branchList.GetEntries()):
        if (branchList[index].GetName().startswith("pd__data_obs")):
            #print branchList[index].GetName()
            tree.SetBranchAddress(branchList[index].GetName(),histo)
            tree.GetEntry(0)
            cv = ROOT.TCanvas("cv"+str(random.random()),"",800,600)
            histo.Draw()
            histo.GetYaxis().SetRangeUser(0.0,histo.GetMaximum()*1.1)
            cv.Print(thetaFile.rsplit(".",1)[0]+".pdf")
    inFile.Close()
    
def testAfterSubtraction(prefix,folder,subtractedFile,signalFile):
    histoSub=ROOT.TH1D()
    histoSub.SetName("sub")
    histoNorm=ROOT.TH1D()
    histoNorm.SetName("norm")
    
    file=ROOT.TFile(os.path.join(folder,subtractedFile))
    tree=file.Get("subtracted")
    tree.SetBranchAddress("histos", histoSub)
    
    file2=ROOT.TFile(os.path.join(folder,signalFile))
    tree2=file2.Get("products")
    tree2.SetBranchAddress("pd__data_obs_"+prefix, histoNorm)
    
    tree.GetEntry(0)
    tree2.GetEntry(0)
    
    binDistList=[]
    for ibin in range(histoSub.GetNbinsX()):
        binDistList.append(numpy.zeros(tree.GetEntries()))
    
    for cnt in range(int(tree.GetEntries())):
        tree.GetEntry(cnt)
        for ibin in range(histoSub.GetNbinsX()):
            binDistList[ibin][cnt]=histoSub.GetBinContent(ibin+1)
            
    histSubMean = ROOT.TH1D(histoNorm)
    histSubMean.SetName("histSubMean")
    
    for ibin in range(histoSub.GetNbinsX()):
        result = numpy.percentile(binDistList[ibin], [15.89,50.0,84.15])
        histSubMean.SetBinContent(ibin+1,result[1])
        histSubMean.SetBinError(ibin+1,math.sqrt((result[0]-result[1])**2+(result[2]-result[1])**2))
    cv=ROOT.TCanvas("subClos","",800,600)
    cv.cd()
    tree2.GetEntry(0)
    
    histoNorm.Draw("hist")
    histoNorm.GetYaxis().Set(500,0.0,histoNorm.GetMaximum()*1.4)
    histoNorm.GetYaxis().SetRangeUser(0.0,histoNorm.GetMaximum()*1.4)
    histSubMean.SetLineColor(ROOT.kGreen+1)
    histSubMean.Draw("Same hist PE")
    cv.Update()
    cv.Print(os.path.join(folder,"subtractedDist.pdf"))
    file.Close()
    file2.Close()
    
def run2DUnfolding(peFile,responseMatrixFile,responseMatrixName, outputFile):
    histoPE=ROOT.TH1D()
    histoOut=ROOT.TH1D("out","",2,-1.0,1.0)
    
    filein=ROOT.TFile(peFile)
    treein=filein.Get("subtracted")
    treein.SetBranchAddress("histos", histoPE)
    
    fileout=ROOT.TFile(outputFile,"RECREATE")
    treeout=ROOT.TTree("unfolded","")
    treeout.Branch("tunfold",histoOut)
    
    responseFile = ROOT.TFile(responseMatrixFile)
    tmRAW = responseFile.Get(responseMatrixName)
    
    treeout.SetDirectory(fileout)
    
    responseMatrix = [[0.0,0.0],[0.0,0.0]]
    efficencies=[0.0,0.0]
    
    measuredHist=[0.0,0.0]
    truthHist=[0.0,0.0]
    
    rebinnedResponse = tmRAW.Rebin2D(tmRAW.GetNbinsX()/2,tmRAW.GetNbinsY()/2)
    for xbin in range(3):
        for ybin in range(3):
            print xbin,",",ybin,": ",rebinnedResponse.GetBinContent(xbin,ybin)
    
    for ibinT in range(tmRAW.GetNbinsX()):
        rebinT=0
        if (tmRAW.GetXaxis().GetBinCenter(ibinT+1)>0.0):
            rebinT=1
        efficencies[rebinT]+=tmRAW.GetBinContent(ibinT+1,0)
        truthHist[rebinT]+=tmRAW.GetBinContent(ibinT+1,0)
        for ibinM in range(tmRAW.GetNbinsY()):
            rebinM=0
            if (tmRAW.GetYaxis().GetBinCenter(ibinM+1)>0.0):
                rebinM=1
            responseMatrix[rebinT][rebinM]+=tmRAW.GetBinContent(ibinT+1,ibinM+1)
            measuredHist[rebinM]+=tmRAW.GetBinContent(ibinT+1,ibinM+1)
            truthHist[rebinT]+=tmRAW.GetBinContent(ibinT+1,ibinM+1)
    print responseMatrix
    for ibinT in range(2):
        print "detected",ibinT,": ",responseMatrix[0][ibinT]+responseMatrix[1][ibinT]
        print "missing",ibinT,": ",efficencies[ibinT]
        print "truth",ibinT,": ",truthHist[ibinT]
        efficencies[ibinT]=(responseMatrix[ibinT][0]+responseMatrix[ibinT][1])/(responseMatrix[ibinT][0]+responseMatrix[ibinT][1]+efficencies[ibinT])
    for ibinT in range(2):
        bin0=responseMatrix[ibinT][0]/(responseMatrix[ibinT][0]+responseMatrix[ibinT][1])
        bin1=responseMatrix[ibinT][1]/(responseMatrix[ibinT][0]+responseMatrix[ibinT][1])
        responseMatrix[ibinT][0]=bin0
        responseMatrix[ibinT][1]=bin1

    det = responseMatrix[0][0]*responseMatrix[1][1]-responseMatrix[0][1]*responseMatrix[1][0]
    responseMatrix_inv = [[responseMatrix[1][1]/det,-responseMatrix[0][1]/det],[-responseMatrix[1][0]/det,responseMatrix[0][0]/det]]
    
    print "response:"
    print responseMatrix
    print "response inv:"
    print responseMatrix_inv
    print "efficiencies:"
    print efficencies
    print "reco:"
    print measuredHist
    
    covarianceMatrix = numpy.dot(responseMatrix_inv,numpy.dot([[(measuredHist[0]),0.0],[0.0,(measuredHist[1])]],numpy.transpose(responseMatrix_inv)))
    correlation=covarianceMatrix[0][1]/math.sqrt(covarianceMatrix[0][0]*covarianceMatrix[1][1])
    print "covariance:"
    print covarianceMatrix
    print "correlation:"
    print correlation
   
   
    
    for cnt in range(int(treein.GetEntries())):
        treein.GetEntry(cnt)
        m=[0.0,0.0]
        t=[0.0,0.0]
        for ibin in range(histoPE.GetNbinsX()):
            ibinM=0
            if (histoPE.GetBinCenter(ibin+1)>0):
                ibinM=1
            m[ibinM]+=histoPE.GetBinContent(ibin+1)
        for i in range(2):
            # need to multiply with the transposed response matrix because the truth bins are on the x axis
            t[i]=responseMatrix_inv[0][i]*m[0]+responseMatrix_inv[1][i]*m[1]
            
            t[i]=t[i]/efficencies[i]
            histoOut.SetBinContent(i+1,t[i])
        treeout.Fill()
    fileout.cd()
    treeout.SetDirectory(fileout)
    treeout.Write()
    
    responseFile.Close()
    fileout.Close()
    filein.Close()

def dataAfterSubtraction(prefix,folder,subtractedFile,signalFile):
    histoSub=ROOT.TH1D()
    histoSub.SetName("sub")
    histoNorm=ROOT.TH1D()
    histoNorm.SetName("norm")
    
    file=ROOT.TFile(os.path.join(folder,subtractedFile))
    tree=file.Get("subtracted")
    tree.SetBranchAddress("histos", histoSub)
    
    file2=ROOT.TFile(os.path.join(folder,signalFile))
    tree2=file2.Get("products")
    tree2.SetBranchAddress("pd__data_obs_"+prefix, histoNorm)
    
    tree.GetEntry(0)
    tree2.GetEntry(0)
    
    
    cv=ROOT.TCanvas("subClos","",800,600)
    cv.cd()
    tree2.GetEntry(0)
    
    histoNorm.Draw("hist")
    histoNorm.GetYaxis().Set(500,0.0,histoNorm.GetMaximum()*1.4)
    histoNorm.GetYaxis().SetRangeUser(0.0,histoNorm.GetMaximum()*1.4)
    histoSub.SetLineColor(ROOT.kGreen+1)
    histoSub.Draw("Same hist PE")
    cv.Update()
    cv.Print(os.path.join(folder,"subtractedDist.pdf"))
    file.Close()
    file2.Close()
    
def subtrackNominalBackground(fileName,nominalFileName,prefix,binningMeasured,folder):
    histo=ROOT.TH1D()
    histo.SetName("signal")
    histoBG=ROOT.TH1D()
    histoBG.SetName("background")
    file=ROOT.TFile(os.path.join(folder,fileName))
    tree=file.Get("products")
    
    tree.SetBranchAddress("pd__data_obs_"+prefix, histo)
    #histo.SetDirectory(0)
    
    file2=ROOT.TFile(os.path.join(folder,nominalFileName))
    
    tree2=file2.Get("products")
    tree2.SetBranchAddress("pd__data_obs_"+prefix, histoBG)
    #histoBG.SetDirectory(0)
    
    fileOut=ROOT.TFile(os.path.join(folder,"subtracted_"+fileName),"RECREATE")
    treeOut=ROOT.TTree("subtracted","subtracted")
    histAsymmetryPreSubtraction=ROOT.TH1F("asymmetryPreSubtraction","asymmetryPreSubtraction",500,-0.2,0.8)
    histAsymmetryPostSubtraction=ROOT.TH1F("asymmetryPostSubtraction","asymmetryPostSubtraction",500,-0.2,0.8)
    histBinPreDistList=[]
    histBinPostDistList=[]
    
    histoSubtracted=ROOT.TH1D("hist","",len(binningMeasured)-1,binningMeasured)
    for cnt in range(len(binningMeasured)-1):
        histBinPreDistList.append(ROOT.TH1F("binPreSubtraction_"+str(cnt+1),"binPreSubtraction_"+str(cnt+1),1000,0.0,5000))
        histBinPostDistList.append(ROOT.TH1F("binPostSubtraction_"+str(cnt+1),"binPostSubtraction_"+str(cnt+1),1000,0.0,5000))
    treeOut.Branch("histos", histoSubtracted)
    biasCount=numpy.zeros(len(binningMeasured)-1)
    for cnt in range(int(tree.GetEntries())):
        tree.GetEntry(cnt)
        tree2.GetEntry(0)
        histAsymmetryPreSubtraction.Fill(calcAsymmetry(histo))
        for ibin in range(len(binningMeasured)-1):
            histBinPreDistList[ibin].Fill(histo.GetBinContent(ibin+1))
            histBinPostDistList[ibin].Fill(histo.GetBinContent(ibin+1)-histoBG.GetBinContent(ibin+1))
            y=histo.GetBinContent(ibin+1)-histoBG.GetBinContent(ibin+1)
            #y=histo.GetBinContent(ibin+1)-histoBG.Integral()/(len(binningMeasured)-1)
            if (y<0):
                biasCount[ibin]+=1.0
                #logging.debug("WARNING: yield after background subtraction smaller than 0: yield="+str(y))
                histoSubtracted.SetBinContent(ibin+1,0)
            else:
                histoSubtracted.SetBinContent(ibin+1,y)
        histAsymmetryPostSubtraction.Fill(calcAsymmetry(histoSubtracted))
        treeOut.Fill()
    for ibin in range(len(binningMeasured)-1):
        biasCount[ibin]=(1.0*biasCount[ibin])/(1.0*tree.GetEntries())
        if biasCount[ibin]>0.01:
            logging.warning("backgroundsubtraction: bin="+str(ibin+1)+" setToZero="+str(round(biasCount[ibin],3)))
    treeOut.Write()
    histAsymmetryPreSubtraction.Write()
    histAsymmetryPostSubtraction.Write()
    
    nUpPre=0.0
    nUpPre_sig=0.0
    nDownPre=0.0
    nDownPre_sig=0.0
    
    nUpPost=0.0
    nUpPost_sig=0.0
    nDownPost=0.0
    nDownPost_sig=0.0

    for cnt in range(len(binningMeasured)-1):
        if histoSubtracted.GetBinCenter(cnt+1)>0:
            nUpPre+=histBinPreDistList[cnt].GetMean()
            nUpPre_sig+=(histBinPreDistList[cnt].GetRMS())**2
            nUpPost+=histBinPostDistList[cnt].GetMean()
            nUpPost_sig+=(histBinPostDistList[cnt].GetRMS())**2
        else:
            nDownPre+=histBinPreDistList[cnt].GetMean()
            nDownPre_sig+=(histBinPreDistList[cnt].GetRMS())**2
            nDownPost+=histBinPostDistList[cnt].GetMean()
            nDownPost_sig+=(histBinPostDistList[cnt].GetRMS())**2
        
        cv = ROOT.TCanvas("cv_"+histBinPreDistList[cnt].GetName(),"",800,600)
        histBinPreDistList[cnt].Draw()
        histBinPreDistList[cnt].Fit("gaus","Q")
        tfPoisson = ROOT.TF1("possion_"+histBinPreDistList[cnt].GetName(),str(histBinPreDistList[cnt].Integral())+"*5.0*TMath::Poisson(x,"+str(histBinPreDistList[cnt].GetMean())+")",0,10000)
        tfPoisson.Draw("Same")
        cv.Write()

        histBinPreDistList[cnt].Write()
        histBinPostDistList[cnt].Write()
    
    nUpPre_sig=math.sqrt(nUpPre_sig)
    nUpPost_sig=math.sqrt(nUpPost_sig)
    nDownPre_sig=math.sqrt(nDownPre_sig)
    nDownPost_sig=math.sqrt(nDownPost_sig)
    #logging.debug("asymmtery pre subtraction (analy.): "+str(round((nUpPre-nDownPre)/(nUpPre+nDownPre),4))+" +- "+str(round(calcAsymmetryAnalytic(nUpPre,nUpPre_sig,nDownPre,nDownPre_sig),4)))
    #logging.debug("asymmtery post subtraction (analy.): "+str(round((nUpPost-nDownPost)/(nUpPost+nDownPost),4))+" +- "+str(round(calcAsymmetryAnalytic(nUpPost,nUpPost_sig,nDownPost,nDownPost_sig),4)))
    fileOut.Close()
    file2.Close()
    file.Close()
    
    
    
def runCommand(cmd,breakOnErr=True,cwd=""):
    process = subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,cwd=cwd)
    
    cout=""
    while True:
        nextline = process.stdout.readline()
        if nextline == '' and process.poll() != None:
            break
        cout+=nextline
        sys.stdout.write(nextline)
        sys.stdout.flush()
    
    
    err=""
    while (True):
        line=process.stderr.readline()
        if line=="":
            break
        err+=line+"\r\n"
        
    if (err!="" and breakOnErr):
        logging.error("error during command execution: '"+str(cmd)+"'")
        logging.error(err)
        sys.exit(-1)
    return err,cout
    
def writeLogFile(filename,err,cout):
    thetaLog=open(filename+".stdout","w")
    thetaLog.write(cout)
    thetaLog.close()
    thetaLog=open(filename+".stderr","w")
    thetaLog.write(err)
    thetaLog.close()
    
def runUnfolding(inputFile,treeName,branchName,reponseFile,reponseMatrixName,outputFile,reg=1.0,cwd="",diceTMUnc=0, bootstrap=0):
    return runCommand(["./execute_unfolding.sh",
                        inputFile,
                        treeName,
                        branchName,
                        reponseFile,
                        reponseMatrixName,
                        outputFile,
                        str(reg),str(diceTMUnc),str(bootstrap)],
                        False,cwd=cwd)

def calcAsymmetry(histo):
    sumUp=0.0
    sumDown=0.0
    for i in range(histo.GetNbinsX()):
        if histo.GetBinCenter(i+1)>0:
            sumUp+=histo.GetBinContent(i+1)
        else:
            sumDown+=histo.GetBinContent(i+1)
    return (sumUp-sumDown)/(sumUp+sumDown)

def calcAsymmetryAnalytic(N1,sigN1,N2,sigN2):
    return math.sqrt((1/(N1+N2)-(N1-N2)/(N1+N2)**2)**2*sigN1**2+(-1/(N1+N2)-(N1-N2)/(N1+N2)**2)**2*sigN2**2)
'''
def closureTest(histoGen,fileName,branchName,histoTreeName,outputName=None):
    file=ROOT.TFile(fileName)
    tree=file.Get(branchName)
    histo=ROOT.TH1D()
    tree.SetBranchAddress(histoTreeName, histo)
    n=int(tree.GetEntries())
    histoBinInfoList=[]
    for ibin in range(histo.GetNbinsX()):
        histoBinInfoList.append({"mean":0.0,"mean2":0.0})  

    for cnt in range(n):
        tree.GetEntry(cnt)
        for ibin in range(histo.GetNbinsX()):
            content=histo.GetBinContent(ibin+1)
            histoBinInfoList[ibin]["mean"]+=content
            histoBinInfoList[ibin]["mean2"]+=content*content
    for ibin in range(histo.GetNbinsX()):   
        histoBinInfoList[ibin]["rms"]=math.sqrt(math.fabs(histoBinInfoList[ibin]["mean2"]/n-histoBinInfoList[ibin]["mean"]**2/(n**2)))
    chi2=0.0
    for cnt in range(n):
        tree.GetEntry(cnt)
        for ibin in range(histo.GetNbinsX()):
            content=histo.GetBinContent(ibin+1)
            contentNorm=histoGen.GetBinContent(ibin+1)
            chi2=(content-contentNorm)**2/histoBinInfoList[ibin]["rms"]**2
'''

def getRootObject(name):
    fileName,objectName=name.rsplit(":",1)
    
    rootFile = ROOT.TFile(fileName,"r")
    obj = rootFile.Get(objectName)
    obj.SetDirectory(0)
    logging.debug("get: "+objectName+" from file '"+fileName+"': "+str(obj))
    rootFile.Close()
    return obj

def closureTest(asymmetryResult,truth,scale=1.0,outputName=None):
    histoBinInfoList=asymmetryResult["info"]
    print histoBinInfoList
    canvasDist=ROOT.TCanvas("canvas","",800,600)
    histMean=ROOT.TH1D(truth)
    for ibin in range(truth.GetNbinsX()):
        print truth.GetBinCenter(ibin+1),truth.GetBinContent(ibin+1)
        histMean.SetBinContent(ibin+1, histoBinInfoList[ibin]["mean"])
        histMean.SetBinError(ibin+1, histoBinInfoList[ibin]["rms"])
    histMean.SetMarkerStyle(21)
    histMean.SetMarkerSize(1.1)

    ymin = min(min(histoBinInfoList[0]["min"],truth.GetMinimum()),0.0)*1.1
    ymax = max(histoBinInfoList[1]["max"],truth.GetMaximum())*1.1
    print ymin,ymax
    axis=ROOT.TH2F("axis",";cos #theta;",50,-1,1,50,ymin,ymax)
    axis.Draw("AXIS")
    histMean.SetLineWidth(2)
    histMean.Draw("Same PE1")
    truth.Scale(scale)
    truth.SetLineWidth(2)
    truth.SetLineColor(ROOT.kGreen+1)
    truth.SetLineStyle(3)
    truth.Draw("histSame")
    canvasDist.Print(outputName+"_dist.pdf")
    
    #logging.info("-----pull and bias--------")
    for ibin in range(truth.GetNbinsX()):
        bias=(histoBinInfoList[ibin]["mean"]-truth.GetBinContent(ibin+1))/truth.GetBinContent(ibin+1)
        pull=(histoBinInfoList[ibin]["mean"]-truth.GetBinContent(ibin+1))/histoBinInfoList[ibin]["rms"]
        #logging.info("bin: "+str(ibin+1)+": bias="+str(round(bias,3))+", pull="+str(round(pull,3)))
    
    truthAsymmetry=calcAsymmetry(truth)
    measuredAsymmetry=asymmetryResult["mean"]
    measuredRMS=asymmetryResult["mean"]
    #logging.info("asy: bias="+str(round((measuredAsymmetry-truthAsymmetry)/truthAsymmetry,3))+", pull="+str(round((measuredAsymmetry-truthAsymmetry)/measuredRMS,3)))
    #logging.info("--------------------------")
    
    
def getAsymmetry(fileName,branchName,histoTreeName,outputName=None):
    file=ROOT.TFile(fileName)
    tree=file.Get(branchName)
    histo=ROOT.TH1D()
    tree.SetBranchAddress(histoTreeName, histo)
    n=int(tree.GetEntries())
    asymmetryList=numpy.zeros(n)
    tree.GetEntry(0)
    
    histoBinInfoList=[]
    for ibin in range(histo.GetNbinsX()):
        histoBinInfoList.append({"max":histo.GetBinContent(ibin+1),"min":histo.GetBinContent(ibin+1)})  
    for cnt in range(n):
        tree.GetEntry(cnt)
        for ibin in range(histo.GetNbinsX()):
            content=histo.GetBinContent(ibin+1)
            if (histoBinInfoList[ibin]["min"])>content:
                histoBinInfoList[ibin]["min"]=content
            if (histoBinInfoList[ibin]["max"])<content:
                histoBinInfoList[ibin]["max"]=content
        asy=calcAsymmetry(histo)
        asymmetryList[cnt]=asy
    for ibin in range(histo.GetNbinsX()): 
        histoBinInfoList[ibin]["dist"]=ROOT.TH1F("dist_"+str(ibin),"bin "+str(ibin+1)+";yield;",100,histoBinInfoList[ibin]["min"],histoBinInfoList[ibin]["max"])
    sortedList=numpy.sort(asymmetryList)
    asymmetryHist = ROOT.TH1F("asymmetryHist",";asymmetry;",200,sortedList[0]-0.1,sortedList[-1]+0.1)
    for cnt in range(n):
        tree.GetEntry(cnt)
        asymmetryHist.Fill(sortedList[cnt])
        if outputName!=None:
            for ibin in range(histo.GetNbinsX()):
                content=histo.GetBinContent(ibin+1)
                histoBinInfoList[ibin]["dist"].Fill(content)
    for ibin in range(histo.GetNbinsX()):
        histoBinInfoList[ibin]["mean"]=histoBinInfoList[ibin]["dist"].GetMean()
        histoBinInfoList[ibin]["rms"]=histoBinInfoList[ibin]["dist"].GetRMS()
    if outputName!=None:
        canvas=ROOT.TCanvas("canvas","",800,600)
        asymmetryHist.Draw();
        canvas.Print(outputName+"_asymmetry.pdf")
        canvasBins=ROOT.TCanvas("canvasBins","",800,600)
        nx=int(math.ceil(math.sqrt(histo.GetNbinsX())))
        ny=int(math.floor(math.sqrt(histo.GetNbinsX())))
        if nx*ny<histo.GetNbinsX():
            nx+=1
        canvasBins.Divide(nx,ny)
        for ibin in range(histo.GetNbinsX()):
            canvasBins.cd(ibin+1)
            histoBinInfoList[ibin]["dist"].Draw()
            
        canvasBins.Print(outputName+"_bins.pdf") 
    
    '''
    quantilProb=numpy.zeros(3)
    quantilProb[0]=0.1584
    quantilProb[1]=0.5000
    quantilProb[2]=0.8415
    quantiles=numpy.zeros(len(quantilProb))
    index=numpy.zeros(n,dtype=numpy.int32)
    ROOT.TMath.Quantiles(n, 3,asymmetryList,quantiles, quantilProb, False, index,4)
    '''
    return {"mean":asymmetryHist.GetMean(),"rms":asymmetryHist.GetRMS(),"info":histoBinInfoList}
     
if __name__=="__main__":
    parser=OptionParser()
    parser.add_option("--modelName",action="store", type="string", default="mymodel", dest="modelName", help="name of the model, all subsequent produced files will included that name")
    parser.add_option("--histFile",action="store", type="string", dest="histFile", help="input file from where all histogramms are taken, e.g. data.root")
    parser.add_option("--responseMatrix",action="store", type="string", dest="responseMatrix", help="point to response matrix, e.g. martix.root:matrix")
    parser.add_option("--fitResult",action="store", type="string", dest="fitResult", help="the file which contains the fit result")
    parser.add_option("--excludeSys",action="append", type="string", default=[], dest="excludedSystematic", help="exclude this or more systematics from the PE generation.")
    parser.add_option("--includeSys",action="append", type="string", default=[], dest="includedSystematic", help="include only this or more systematics from PE generation.")
    parser.add_option("--prefix",action="store", type="string", default="cos_theta", dest="prefix", help="prefix")
    parser.add_option("-f","--force",action="store_true", default=False, dest="force", help="deletes old output folder")
    parser.add_option("--output",action="store", type="string", default=None, dest="output", help="output directory, default is {modelName}")
    parser.add_option("--runOnData",action="store_true", dest="runOnData",default=False, help="should data be unfolded (PEs otherwise)")
    parser.add_option("--noStatUncertainty",action="store_true",default=False, dest="noStatUncertainty", help="turn off statistical uncertainty")
    parser.add_option("--noMCUncertainty",action="store_true",default=False, dest="noMCUncertainty", help="turn off MC statistics uncertainty")
    
    parser.add_option("--scaleRegularization",action="store", type="float", default=1.0, dest="regScale", help="manipulate the estimated regularization parameter: tau=tau*regScale")
    parser.add_option("--noBackground",action="store_true",default=False, dest="noBackground", help="assumes only signal, background and its subtractions is not considered")
    
    parser.add_option("--genHist",action="store", type="string", dest="genHist", default=None, help="optional gen histogram")
    
    parser.add_option("--only-2bins",action="store_true", dest="only_2bins", default=False, help="optional merged to 2x2 bin inversion")
    
    ### currently not yet supported options
    parser.add_option("--signal",action="store", type="string", dest="signalHistogram", help="input signal sample, e.g. data.root:cos_theta__tchan")



    (options, args)=parser.parse_args()
    #-----------------------------------------------------------------------------
    logging.info("!!! checking specified run options !!!")
    logging.info("use modelname: "+options.modelName)
    if options.output==None:
        options.output=options.modelName
    options.output=os.path.abspath(options.output)
    logging.info("output path: "+options.output)
    if os.path.exists(options.output):
        logging.warning("output directory '"+options.output+"'")
        if options.force:
            logging.warning("forced override specified - old folder will be deleted")
            shutil.rmtree(options.output)
        else:
            sys.exit(-1)
    os.mkdir(options.output)
            
    
    filesToCheck=[]
    if (options.histFile==None):
        logging.error("Error - 'histfile' needs to be specified")
        sys.exit(-1)
    logging.info("take histograms from: "+options.histFile)
    filesToCheck.append(options.histFile)

    if options.signalHistogram:
        logging.warning("will use '"+options.signalHistogram+"' for signal instead")
        filesToCheck.append(options.signalHistogram.rsplit(":",1)[0]) #removes root path to object within root file
        logging.error("separate signal histogram not supported yet")
        sys.exit(-1)

    if options.genHist:
        logging.info("optional genHist: "+str(options.genHist))

    logging.info("run on data: "+str(options.runOnData))
    if (options.runOnData):
        logging.info("will run on data")
    else:
        logging.info("will run PE")
  
    if (options.fitResult==None):
        logging.error("no 'fitResult' specified")
        sys.exit(-1)
    filesToCheck.append(options.fitResult)
    logging.info("use fit result from: "+options.fitResult)

    if (options.responseMatrix==None):
        logging.error("'responseMatrix' needs to be specified")
        sys.exit(-1)
    logging.info("response matrix: "+options.responseMatrix)
    filesToCheck.append(options.responseMatrix.rsplit(":",1)[0])
    
    
    if options.includedSystematic!=[]:
        logging.info("include only the following systematics: "+str(options.includedSystematic))
    if options.excludedSystematic!=[] and options.includedSystematic==[]:
        logging.info("excluded systematics: "+str(options.excludedSystematic))
    
    if not options.runOnData:
        logging.info("run statistical uncertainty: "+str(not options.noStatUncertainty))
        logging.info("run MC statstics uncertainty: "+str(not options.noMCUncertainty))
        
    logging.info("regularization scale: "+str(options.regScale))
    
    
    #-----------------------------------------------------------------------------
    logging.info("!!! check if all input files exist !!!")
    for f in filesToCheck:
        if not  os.path.exists(f):
            logging.error("necessary file: '"+f+"' does not exist!")
            sys.exit(-1)  
    
          
    #-----------------------------------------------------------------------------
    logging.info("!!! parsing fit result !!!")
    corrListForTheta=[]
    signalSetDict,backgroundSetDict,dataSetDict,yieldSysDict,shapeSysDict,corrList=parseFitResult(options.fitResult)
    
    logging.info("signal sets:")
    for key in signalSetDict.keys():
        logging.info("    "+key+": "+str(signalSetDict[key])) 
    logging.info("background sets:")
    for key in backgroundSetDict.keys():
        logging.info("    "+key+": "+str(backgroundSetDict[key]))
    logging.info("yield systematics:")
    for key in yieldSysDict.keys():
        if not (key in signalSetDict.keys() or key in backgroundSetDict.keys()):
            yieldSysDict.pop(key)
            logging.warning("    yield "+key+" has no set of hists defined -> removed")
            continue
        if (options.includedSystematic != [] and key not in options.includedSystematic):
            yieldSysDict[key]["unc"]=0.0000000001
        if (key in options.excludedSystematic):
            yieldSysDict[key]["unc"]=0.0000000001
        logging.info("    "+key+": "+str(yieldSysDict[key]["mean"])+" +- "+str(yieldSysDict[key]["unc"]))
    logging.info("shape systematics:")
    for key in shapeSysDict.keys():
        if (options.includedSystematic != [] and key not in options.includedSystematic):
            shapeSysDict[key]["unc"]=0.0000000001  
        if (key in options.excludedSystematic):
            shapeSysDict[key]["unc"]=0.0000000001
        msg ="    "+key+": "+str(shapeSysDict[key]["mean"])+" +- "+str(shapeSysDict[key]["unc"])
        if shapeSysDict[key]["norm"]:
            msg += ", normalized"
        if shapeSysDict[key]["independent"]:
            msg += ", independent"
        logging.info(msg)
    logging.info("correlations:")
    for corr in corrList:
        if not ((corr["name"][0] in yieldSysDict.keys()) or (corr["name"][0] in shapeSysDict.keys())):
            logging.warning("    "+corr["name"][0]+" not found -> correlation ignored")
        elif not ((corr["name"][1] in yieldSysDict.keys()) or (corr["name"][1] in shapeSysDict.keys())):
            logging.warning("    "+corr["name"][1]+" not found -> correlation ignored")
        else:
            logging.info("    "+str(corr["name"])+": "+str(corr["rho"]))
            corrListForTheta.append(corr)
            
      
    #-----------------------------------------------------------------------------
    logging.info("!!! check binning of response matrix and MC !!!")
    binningHist=None
    binningMeasured,binningTruth=getResponseMatrixBinning(options.responseMatrix)
    for signalSet in signalSetDict.values():
        for signalHistName in signalSet:
            binningHist=getMeasuredHistogramBinning(options.histFile+":"+signalHistName)
            if len(binningHist)!=len(binningMeasured):
                logging.error("response matrix (N="+str(len(binningMeasured))+") and MC (N="+str(len(binningHist))+") differ in number of bins")
                sys.exit(-1)
            for i in range(len(binningHist)):
                if math.fabs(binningHist[i]-binningMeasured[i])>0.000001:
                    logging.error("different bin edges in response matrix and MC")
                    sys.exit(-1)
     

    #-----------------------------------------------------------------------------
    logging.info("!!! generate theta models !!!")
    
    if not options.noBackground or options.runOnData:
        generateNominalBackground(
            modelName=options.modelName+"_backgroundNominal",
            outputFolder=options.output,
            histFile=options.histFile,
            signalSetDict=signalSetDict,
            backgroundSetDict=backgroundSetDict,
            yieldSysDict=yieldSysDict,
            shapeSysDict=shapeSysDict,
            corrList=corrListForTheta,
            prefix=options.prefix,
            binning=len(binningHist)-1,
            ranges=[binningHist[0],binningHist[-1]],
            dicePoisson=not options.noStatUncertainty,
            mcUncertainty=not options.noMCUncertainty
        )
                    
    if options.runOnData:
        generateModelData(modelName=options.modelName,
            outputFolder=options.output,
            histFile=options.histFile,
            dataSetDict=dataSetDict,
            prefix=options.prefix,
            binning=len(binningHist)-1,
            ranges=[binningHist[0],binningHist[-1]],
            dicePoisson=not options.noStatUncertainty,
            mcUncertainty=not options.noMCUncertainty)
    else:
        generateModelPE(
            modelName=options.modelName,
            outputFolder=options.output,
            histFile=options.histFile,
            signalSetDict=signalSetDict,
            backgroundSetDict=backgroundSetDict,
            yieldSysDict=yieldSysDict,
            shapeSysDict=shapeSysDict,
            corrList=corrListForTheta,
            prefix=options.prefix,
            binning=len(binningHist)-1,
            ranges=[binningHist[0],binningHist[-1]],
            dicePoisson=not options.noStatUncertainty,
            mcUncertainty=not options.noMCUncertainty
        )
    
    generateNominalSignal(modelName=options.modelName+"_signalNominal",
            outputFolder=options.output,
            histFile=options.histFile,
            signalSetDict=signalSetDict,
            backgroundSetDict=backgroundSetDict,
            yieldSysDict=yieldSysDict,
            shapeSysDict=shapeSysDict,
            corrList=corrListForTheta,
            prefix=options.prefix,
            binning=len(binningHist)-1,
            ranges=[binningHist[0],binningHist[-1]],
            dicePoisson=not options.noStatUncertainty,
            mcUncertainty=not options.noMCUncertainty)

    


    #-----------------------------------------------------------------------------
    logging.info("!!! run theta !!!")
    shutil.copy("execute_theta.sh", os.path.join(options.output,"execute_theta.sh"))    
    #nominal background
    if not options.noBackground or options.runOnData:
        err,out=runCommand(["./execute_theta.sh",options.modelName+"_backgroundNominal.cfg"],cwd=options.output)
        if not os.path.exists(os.path.join(options.output,options.modelName+"_backgroundNominal.root")):
            logging.error("theta output was not created")
            logging.error(err)
            logging.error(out)
            sys.exit(-1)
        writeLogFile(os.path.join(options.output,"theta_"+options.modelName+"_backgroundNominal"),err,out)
    plotThetaHistograms(os.path.join(options.output,options.modelName+"_backgroundNominal.root"))
    
    #nominal signal
    err,out=runCommand(["./execute_theta.sh",options.modelName+"_signalNominal.cfg"],cwd=options.output)
    if not os.path.exists(os.path.join(options.output,options.modelName+"_signalNominal.root")):
        logging.error("theta output was not created")
        logging.error(err)
        logging.error(out)
        sys.exit(-1)
    writeLogFile(os.path.join(options.output,"theta_"+options.modelName+"_signalNominal"),err,out)
    plotThetaHistograms(os.path.join(options.output,options.modelName+"_signalNominal.root"))
    
    #PEs or data (using same output name)
    err,out=runCommand(["./execute_theta.sh",options.modelName+".cfg"],cwd=options.output)
    if not os.path.exists(os.path.join(options.output,options.modelName+".root")):
        logging.error("theta output was not created")
        logging.error(err)
        logging.error(out)
        sys.exit(-1)
    writeLogFile(os.path.join(options.output,"theta_"+options.modelName),err,out)
    plotThetaHistograms(os.path.join(options.output,options.modelName+".root"))
    
    #-----------------------------------------------------------------------------
    logging.info("!!! run subtract !!!")
    #change for data the nominal model name!
    if options.noBackground:
        rebinHistograms(options.modelName+".root",options.prefix,binningMeasured,options.output)
    else:
        subtrackNominalBackground(options.modelName+".root",options.modelName+"_backgroundNominal.root",options.prefix,binningMeasured,options.output)
    
    if not os.path.exists(os.path.join(options.output,"subtracted_"+options.modelName+".root")):
        logging.error("unfolding output was not created")
        logging.error(err)
        logging.error(out)
        sys.exit(-1)
    if options.runOnData:
        dataAfterSubtraction(options.prefix,options.output,"subtracted_"+options.modelName+".root",options.modelName+"_signalNominal.root")
    else:
        testAfterSubtraction(options.prefix,options.output,"subtracted_"+options.modelName+".root",options.modelName+"_signalNominal.root")
    
    #-----------------------------------------------------------------------------
    logging.info("!!! run unfolding !!!")
    responseMatrixFile,responseMatrixName=options.responseMatrix.split(":",1)
    if (options.only_2bins):
        run2DUnfolding(os.path.join(options.output,"subtracted_"+options.modelName+".root"),responseMatrixFile,responseMatrixName, os.path.join(options.output,"unfolded_"+options.modelName+".root"))
    else:    
        shutil.copy("execute_unfolding.sh", os.path.join(options.output,"execute_unfolding.sh"))  
        err,out=runUnfolding(os.path.join(options.output,"subtracted_"+options.modelName+".root"),"subtracted","histos",responseMatrixFile,responseMatrixName,os.path.join(options.output,"unfolded_"+options.modelName+".root"),reg=options.regScale,diceTMUnc=1,bootstrap=0,cwd=options.output)
        if not os.path.exists(os.path.join(options.output,"unfolded_"+options.modelName+".root")):
            logging.error("unfolding output was not created")
            logging.error(err)
            logging.error(out)
            sys.exit(-1)
        writeLogFile(os.path.join(options.output,"unfolding_"+options.modelName),err,out)
    #-----------------------------------------------------------------------------
    logging.info("!!! calculate asymmetry !!!")
    
    asymmetryResult = getAsymmetry(os.path.join(options.output,"unfolded_"+options.modelName+".root"),"unfolded","tunfold",outputName=os.path.join(options.output,options.modelName))
    if (not options.runOnData):
        compareHist=None
        if options.genHist:
            compareHist= getRootObject(options.genHist)
        else:
            compareHist=getRootObject(options.responseMatrix).ProjectionX()
        if (options.only_2bins):
            rebinnedCompareHist=ROOT.TH1D("compHistT","",2,-1,1)
            for ibin in range(compareHist.GetNbinsX()):
                if compareHist.GetBinCenter(ibin+1)<0:
                    rebinnedCompareHist.Fill(-0.5,compareHist.GetBinContent(ibin+1))
                else:
                    rebinnedCompareHist.Fill(0.5,compareHist.GetBinContent(ibin+1))
            compareHist=rebinnedCompareHist
        closureTest(asymmetryResult,compareHist,scale=1.0,outputName=os.path.join(options.output,options.modelName))
    logging.info("final asymmetry: mean="+str(asymmetryResult["mean"])+", rms="+str(asymmetryResult["rms"]))

    file=open(os.path.join(options.output,"asymmetry.txt"),"w")
    file.write("mean, "+str(round(asymmetryResult["mean"],7))+"\n")
    file.write("rms, "+str(round(asymmetryResult["rms"],7))+"\n")
    if (not options.runOnData):
        if options.genHist:
            file.write("gen, "+str(round(calcAsymmetry(getRootObject(options.genHist)),7))+"\n") 
        else:
            file.write("gen, "+str(round(calcAsymmetry(getRootObject(options.responseMatrix).ProjectionX()),7))+"\n") 
    file.close()
    
