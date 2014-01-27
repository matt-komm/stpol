from optparse import OptionParser
import math
import sys
import numpy
import os
import logging
import ROOT
import shutil
import subprocess
from generateCosThetaModel import *

logging.basicConfig(format="%(levelname)s - %(message)s",level=logging.DEBUG)
#logging.basicConfig(filename="run.log",format="%(levelname)s - %(message)s",level=logging.DEBUG)

#processes to consider
SIGNAL=["tchan"]
BACKGROUND=["top","wzjets","qcd","other"]
#will search which of the following systematics are present in the input root file
SYS=["Res","En","UnclusteredEn","btaggingBC","btaggingL","leptonID",
     "leptonIso","leptonTrigger","wjets_flat","wjets_shape",
     "ttbar_matching","ttbar_scale","top_pt","mass","pileup"]
FULL=[]
FULL.extend(SIGNAL)
FULL.extend(BACKGROUND)
FULL.extend(SYS)


ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetStatX(0.4)
ROOT.gStyle.SetStatY(0.98)


def parseFitResult(inputfile,excludeSysList):
    yieldSys=[]
    shapeSys=[]
    corr=[]
    file = open(inputfile,"r")
    ln=0
    for line in file:
        ln+=1
        splitted=line.replace("\r","").replace("\n","").replace(" ","").split(",")
        if len(splitted)!=4:
            loggging.error("Error while reading the fitresult file: "+line)
            sys.exit(-1)
        try:
            if splitted[0]=="rate":
                if splitted[1] in excludeSysList:
                    yieldSys.append({"name":splitted[1],"mean":float(splitted[2]),"unc":0.00000001})
                else:
                    yieldSys.append({"name":splitted[1],"mean":float(splitted[2]),"unc":float(splitted[3])})
            elif splitted[0]=="shape":
                if splitted[1] in excludeSysList:
                    shapeSys.append({"name":splitted[1],"mean":float(splitted[2]),"unc":0.00000001})
                else:
                    shapeSys.append({"name":splitted[1],"mean":float(splitted[2]),"unc":float(splitted[3])})
            elif splitted[0]=="corr":
                if (splitted[1] not in excludeSysList) and (splitted[2] not in excludeSysList):
                    corr.append({"name":[splitted[1],splitted[2]],"rho":float(splitted[3])})
            else:
                logging.warning("type not regonized: "+splitted[0])
        except ValueError, e:
            logging.error("parsing of '"+inputfile+"' failed at line "+str(ln))
            logging.error("cannot parse: '"+line+"'")
            logging.error(e.message)
            sys.exit(-1)
    file.close()
    return yieldSys,shapeSys,corr
    
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
        logging.error("signal histogram '"+objectName+"' in file '"+fileName+"' could not be read")
        sys.exit(-1)
    nbins = signalHistogram.GetNbinsX()
    binning=numpy.zeros(nbins+1)
    for ibin in range(nbins+1):
        binning[ibin]=signalHistogram.GetBinLowEdge(ibin+1)
    return binning
    
def rebinHistograms(fileName,histPrefix,binningMeasured,folder):
    histo=ROOT.TH1D()
    histoBG=ROOT.TH1D()
    file=ROOT.TFile(os.path.join(folder,fileName))
    tree=file.Get("products")
    
    tree.SetBranchAddress("pd__data_obs_"+histPrefix, histo)
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
    
    
def subtrackNominalBackground(fileName,nominalFileName,histPrefix,binningMeasured,folder):
    histo=ROOT.TH1D()
    histoBG=ROOT.TH1D()
    file=ROOT.TFile(os.path.join(folder,fileName))
    tree=file.Get("products")
    
    tree.SetBranchAddress("pd__data_obs_"+histPrefix, histo)
    #histo.SetDirectory(0)
    
    file2=ROOT.TFile(os.path.join(folder,nominalFileName))
    
    tree2=file2.Get("products")
    tree2.SetBranchAddress("pd__data_obs_"+histPrefix, histoBG)
    #histoBG.SetDirectory(0)
    
    fileOut=ROOT.TFile(os.path.join(folder,"subtracted_"+fileName),"RECREATE")
    treeOut=ROOT.TTree("subtracted","subtracted")


    histoSubtracted=ROOT.TH1D("subtracted","",len(binningMeasured)-1,binningMeasured)
    treeOut.Branch("histos", histoSubtracted)
    biasCount=numpy.zeros(len(binningMeasured)-1)
    for cnt in range(int(tree.GetEntries())):
        tree.GetEntry(cnt)
        tree2.GetEntry(0)
        
        for ibin in range(len(binningMeasured)-1):
            y=histo.GetBinContent(ibin+1)-histoBG.GetBinContent(ibin+1)
            
            if (y<0):
                biasCount[ibin]+=1.0
                #logging.debug("WARNING: yield after background subtraction smaller than 0: yield="+str(y))
                histoSubtracted.SetBinContent(ibin+1,0)
            else:
                histoSubtracted.SetBinContent(ibin+1,y)
        treeOut.Fill()
    for ibin in range(len(binningMeasured)-1):
        biasCount[ibin]=(1.0*biasCount[ibin])/(1.0*tree.GetEntries())
        #logging.info("backgroundsubtraction: bin="+str(ibin+1)+" setToZero="+str(round(biasCount[ibin],3)))
    treeOut.Write()
    fileOut.Close()
    file2.Close()
    file.Close()
    
    
    
def runCommand(cmd,breakOnErr=True,cwd=""):
    process = subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,cwd=cwd)
    process.wait()
    err=""
    while (True):
        line=process.stderr.readline()
        if line=="":
            break
        err+=line+"\r\n"
        
    cout=""
    while (True):
        line=process.stdout.readline()
        if line=="":
            break
        cout+=line+"\r\n"
        
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
    
def runUnfolding(inputFile,treeName,branchName,reponseFile,reponseMatrixName,outputFile,reg=1.0,cwd=""):
    return runCommand(["./execute_unfolding.sh",
                        inputFile,
                        treeName,
                        branchName,
                        reponseFile,
                        reponseMatrixName,
                        outputFile,
                        str(reg)],
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

def closureTest(asymmetryResult,responseMatrix,outputName=None):
    histoBinInfoList=asymmetryResult["info"]
    fileName,objectName=options.responseMatrix.rsplit(":",1)
    rootFile = ROOT.TFile(fileName,"r")
    responseMatrix = rootFile.Get(objectName)
    truth =  responseMatrix.ProjectionX()
    canvasDist=ROOT.TCanvas("canvas","",800,600)
    histMean=ROOT.TH1D(truth)
    for ibin in range(truth.GetNbinsX()):
        histMean.SetBinContent(ibin+1, histoBinInfoList[ibin]["mean"])
        histMean.SetBinError(ibin+1, histoBinInfoList[ibin]["rms"])
    histMean.SetMarkerStyle(21)
    histMean.SetMarkerSize(1.2)
    histMean.Draw("PE1")
    truth.SetLineColor(ROOT.kGreen)
    #truth.Scale(histMean.Integral()/truth.Integral())
    truth.Draw("LSame")
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
    parser.add_option("--excludeSys",action="append", type="string", default=[], dest="excludedSystematic", help="exclude this or more systematics from the PE generation. Possible values: "+str(FULL))
    parser.add_option("--includeSys",action="append", type="string", default=[], dest="includedSystematic", help="include only this or more systematics from PE generation. Possible values: "+str(FULL))
    parser.add_option("--histogramPrefix",action="store", type="string", default="cos_theta", dest="histogramPrefix", help="prefix for all histograms")
    parser.add_option("-f","--force",action="store_true", default=False, dest="force", help="deletes old output folder")
    parser.add_option("--output",action="store", type="string", default=None, dest="output", help="output directory, default is {modelName}")
    parser.add_option("--data",action="store", type="string", dest="dataHistogram", help="input data sample, e.g. data.root:cos_theta__DATA")
    parser.add_option("--runOnData",action="store_true", dest="runOnData",default=False, help="should data be unfolded (PEs otherwise)")
    parser.add_option("--noStatUncertainty",action="store_true",default=False, dest="noStatUncertainty", help="turn off statistical uncertainty")
    parser.add_option("--noMCUncertainty",action="store_true",default=False, dest="noMCUncertainty", help="turn off MC statistics uncertainty")
    
    parser.add_option("--scaleRegularization",action="store", type="float", default=1.0, dest="regScale", help="manipulate the estimated regularization parameter: tau=tau*regScale")
    parser.add_option("--noBackground",action="store_true",default=False, dest="noBackground", help="assumes only signal, background and its subtractions is not considered")
    
    
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
            logging.warning("force specified - old folder will be deleted")
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
    if options.dataHistogram:
        logging.warning("will use '"+options.dataHistogram+"' for data instead")
        filesToCheck.append(options.dataHistogram.rsplit(":",1)[0]) #removes root path to object within root file
    else:
        options.dataHistogram=options.histFile+":"+options.histogramPrefix+"__DATA"

    logging.info("run on data: "+str(options.runOnData))
    if (options.runOnData):
        logging.info("will run on data from '"+options.dataHistogram+"'")
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
        for systematic in SIGNAL:
            if (systematic not in options.excludedSystematic) and (systematic not in options.includedSystematic):
                options.excludedSystematic.append(systematic)
        for systematic in BACKGROUND:
            if (systematic not in options.excludedSystematic) and (systematic not in options.includedSystematic):
                options.excludedSystematic.append(systematic)
        for systematic in SYS:
            if (systematic not in options.excludedSystematic) and (systematic not in options.includedSystematic):
                options.excludedSystematic.append(systematic)
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
    logging.info("!!! check binning of response matrix and MC !!!")
    binningHist=getMeasuredHistogramBinning(options.histFile+":"+options.histogramPrefix+"__"+SIGNAL[0])
    binningMeasured,binningTruth=getResponseMatrixBinning(options.responseMatrix)
    if len(binningHist)!=len(binningMeasured):
        logging.error("response matrix (N="+str(len(binningMeasured))+") and MC (N="+str(len(binningHist))+") differ in number of bins")
        sys.exit(-1)
    for i in range(len(binningHist)):
        if math.fabs(binningHist[i]-binningMeasured[i])>0.000001:
            logging.error("different bin edges in response matrix and MC")
            sys.exit(-1)
            
    #-----------------------------------------------------------------------------
    signalYieldList=[]
    backgroundYieldList=[]
    sysList=[]
    corrList=[]
    logging.info("!!! parse fit result !!!")
    yieldSys,shapeSysList,correlations=parseFitResult(options.fitResult,options.excludedSystematic)
    for systematic in yieldSys:
        if systematic["name"] in SIGNAL:
            logging.debug("signal: "+systematic["name"]+": "+str(systematic["mean"])+" +- "+str(systematic["unc"])+" (rate)")
            signalYieldList.append(systematic)
        if systematic["name"] in BACKGROUND:
            logging.debug("background: "+systematic["name"]+": "+str(systematic["mean"])+" +- "+str(systematic["unc"])+" (rate)")
            backgroundYieldList.append(systematic)
    for systematic in shapeSysList:
        if systematic["name"] in SYS:
            sysList.append(systematic)
            logging.debug(systematic["name"]+": "+str(systematic["mean"])+" +- "+str(systematic["unc"])+" (shape)")
    for systematic in correlations:
        if ((systematic["name"][0] in SYS) or (systematic["name"][0] in SIGNAL) or(systematic["name"][0] in BACKGROUND)) and((systematic["name"][1] in SYS) or (systematic["name"][1] in SIGNAL) or(systematic["name"][1] in BACKGROUND)):
            logging.debug(str(systematic["name"])+": "+str(systematic["rho"])+" (correlation)")  
            corrList.append(systematic)
    #-----------------------------------------------------------------------------
    logging.info("!!! generate theta models !!!")
    if not options.noBackground:
        generateNominalBackground(modelName=options.modelName+"_backgroundNominal",
                    outputFolder=options.output,
                    histFile=options.histFile,
                    histPrefix=options.histogramPrefix,
                    backgroundYieldList=backgroundYieldList,
                    binning=len(binningHist)-1,
                    ranges=[binningHist[0],binningHist[-1]])
    if options.runOnData:
        generateModelData(modelName=options.modelName,
                    outputFolder=options.output,
                    dataHist=options.dataHistogram,
                    histPrefix=options.histogramPrefix,
                    binning=len(binningHist)-1,
                    ranges=[binningHist[0],binningHist[-1]])
    elif options.noBackground:
         generateNominalSignal(modelName=options.modelName,
                    outputFolder=options.output,
                    histFile=options.histFile,
                    histPrefix=options.histogramPrefix,
                    signalYieldList=signalYieldList,
                    binning=len(binningHist)-1,
                    ranges=[binningHist[0],binningHist[-1]],
                    dicePoisson=not options.noStatUncertainty,
                    mcUncertainty=not options.noMCUncertainty)
    else:
        generateModelPE(  modelName=options.modelName,
                        outputFolder=options.output,
                        histFile=options.histFile,
                        histPrefix=options.histogramPrefix,
                        signalYieldList=signalYieldList,
                        backgroundYieldList=backgroundYieldList,
                        shapeSysList=sysList,
                        correlations=corrList,
                        binning=len(binningHist)-1,
                        ranges=[binningHist[0],binningHist[-1]],
                        dicePoisson=not options.noStatUncertainty,
                        mcUncertainty=not options.noMCUncertainty)
    
    
    #-----------------------------------------------------------------------------
    logging.info("!!! run theta !!!")
    shutil.copy("execute_theta.sh", os.path.join(options.output,"execute_theta.sh"))    
    if not options.noBackground:
        err,out=runCommand(["./execute_theta.sh",options.modelName+"_backgroundNominal.cfg"],cwd=options.output)
        if not os.path.exists(os.path.join(options.output,options.modelName+"_backgroundNominal.root")):
            logging.error("theta output was not created")
            logging.error(err)
            logging.error(out)
            sys.exit(-1)
        writeLogFile(os.path.join(options.output,"theta_"+options.modelName+"_backgroundNominal"),err,out)
        
    err,out=runCommand(["./execute_theta.sh",options.modelName+".cfg"],cwd=options.output)
    if not os.path.exists(os.path.join(options.output,options.modelName+".root")):
        logging.error("theta output was not created")
        logging.error(err)
        logging.error(out)
        sys.exit(-1)
    writeLogFile(os.path.join(options.output,"theta_"+options.modelName),err,out)
        
    
    #-----------------------------------------------------------------------------
    logging.info("!!! run subtract !!!")
    #change for data the nominal model name!
    if options.noBackground:
        rebinHistograms(options.modelName+".root",options.histogramPrefix,binningMeasured,options.output)
    else:
        subtrackNominalBackground(options.modelName+".root",options.modelName+"_backgroundNominal.root",options.histogramPrefix,binningMeasured,options.output)
    if not os.path.exists(os.path.join(options.output,"subtracted_"+options.modelName+".root")):
        logging.error("unfolding output was not created")
        logging.error(err)
        logging.error(out)
        sys.exit(-1)
    #-----------------------------------------------------------------------------
    logging.info("!!! run unfolding !!!")
    responseMatrixFile,responseMatrixName=options.responseMatrix.split(":",1)
    shutil.copy("execute_unfolding.sh", os.path.join(options.output,"execute_unfolding.sh"))  
    err,out=runUnfolding(os.path.join(options.output,"subtracted_"+options.modelName+".root"),"subtracted","histos",responseMatrixFile,responseMatrixName,os.path.join(options.output,"unfolded_"+options.modelName+".root"),reg=options.regScale,cwd=options.output)
    if not os.path.exists(os.path.join(options.output,"unfolded_"+options.modelName+".root")):
        logging.error("unfolding output was not created")
        logging.error(err)
        logging.error(out)
        sys.exit(-1)
    writeLogFile(os.path.join(options.output,"unfolding_"+options.modelName),err,out)
    #-----------------------------------------------------------------------------
    logging.info("!!! calculate asymmetry !!!")
    
    asymmetryResult = getAsymmetry(os.path.join(options.output,"unfolded_"+options.modelName+".root"),"unfolded","tunfold",outputName=os.path.join(options.output,options.modelName))
    closureTest(asymmetryResult,options.responseMatrix,outputName=os.path.join(options.output,options.modelName))
    logging.info("final asymmetry: mean="+str(asymmetryResult["mean"])+", rms="+str(asymmetryResult["rms"]))
    file=open(os.path.join(options.output,"asymmetry.txt"),"w")
    file.write("mean, "+str(round(asymmetryResult["mean"],7))+"\n")
    file.write("rms, "+str(round(asymmetryResult["rms"],7))+"\n")
    file.close()
    
    
