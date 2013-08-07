from optparse import OptionParser
import math
import sys
import numpy
import os
import logging
import ROOT
import subprocess
from generateCosThetaModel import *

logging.basicConfig(format="%(levelname)s - %(message)s",level=logging.DEBUG)
#logging.basicConfig(filename="run.log",format="%(levelname)s - %(message)s",level=logging.DEBUG)

#processes to consider
SIGNAL=["tchan"]
BACKGROUND=["top","wzjets","qcd",]
#will search which of the following systematics are present in the input root file
SYS=["Res","En","UnclusteredEn","btaggingBD","btaggingL","leptonID","leptonIso","leptonTrigger","wjets_flat","wjets_shape"]

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
    
    
def subtrackNominalBackground(modelName,modelNominalName,histPrefix,binningMeasured):
    histo=ROOT.TH1D()
    histoBG=ROOT.TH1D()
    file=ROOT.TFile(modelName+".root")
    tree=file.Get("products")
    
    tree.SetBranchAddress("pd__data_obs_"+histPrefix, histo)
    #histo.SetDirectory(0)
    
    file2=ROOT.TFile(modelNominalName+".root")
    
    tree2=file2.Get("products")
    tree2.SetBranchAddress("pd__data_obs_"+histPrefix+"BG", histoBG)
    #histoBG.SetDirectory(0)
    
    fileOut=ROOT.TFile("subtracted_"+modelName+".root","RECREATE")
    treeOut=ROOT.TTree("subtracted","subtracted")


    histoSubtracted=ROOT.TH1D("subtracted","",len(binningMeasured)-1,binningMeasured)
    treeOut.Branch("histos", histoSubtracted)
    
    for cnt in range(int(tree.GetEntries())):
        tree.GetEntry(cnt)
        tree2.GetEntry(cnt)
        
        for ibin in range(len(binningMeasured)-1):
            y=histo.GetBinContent(ibin+1)-histoBG.GetBinContent(ibin+1)
            if (y<0):
                logging.debug("WARNING: yield after background subtraction smaller than 0: yield="+str(y))
                histoSubtracted.SetBinContent(ibin+1,0)
            else:
                histoSubtracted.SetBinContent(ibin+1,y)
        treeOut.Fill()
    
    treeOut.Write()
    fileOut.Close()
    file2.Close()
    file.Close()
    
    
    
def runCommand(cmd,breakOnErr=True):
    process = subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
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
    
def runUnfolding(inputFile,treeName,branchName,reponseFile,reponseMatrixName,outputFile,reg=1.0):
    return runCommand(["./execute_unfolding.sh",
                        inputFile,
                        treeName,
                        branchName,
                        reponseFile,
                        reponseMatrixName,
                        outputFile,
                        str(reg)],
                        False)

     
if __name__=="__main__":
    parser=OptionParser()
    parser.add_option("--modelName",action="store", type="string", default="mymodel", dest="modelName", help="name of the model, all subsequent produced files will included that name")
    parser.add_option("--histFile",action="store", type="string", dest="histFile", help="input file from where all histogramms are taken, e.g. data.root")
    #TODO: runOnData
    parser.add_option("--runOnData",action="store_true", dest="runOnData",default=False, help="should data be unfolded (PEs otherwise)")
    parser.add_option("--responseMatrix",action="store", type="string", dest="responseMatrix", help="point to response matrix, e.g. martix.root:matrix")
    parser.add_option("--fitResult",action="store", type="string", dest="fitResult", help="the file which contains the fit result")
    parser.add_option("--excludeSys",action="append", type="string", default=[], dest="excludedSystematic", help="point to response matrix, e.g. martix.root:matrix")
    parser.add_option("--histogramPrefix",action="store", type="string", default="cos_theta", dest="histogramPrefix", help="prefix for all histograms")
    
    
    ### currently not yet supported options
    parser.add_option("--signal",action="store", type="string", dest="signalHistogram", help="input signal sample, e.g. data.root:cos_theta__tchan")
    parser.add_option("--data",action="store", type="string", dest="dataHistogram", help="input data sample, e.g. data.root:cos_theta__DATA")

    (options, args)=parser.parse_args()
    #-----------------------------------------------------------------------------
    logging.info("!!! checking specified run options !!!")
    logging.info("use modelname: "+options.modelName)
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
        logging.error("separate data histogram not supported yet")
        sys.exit(-1)

    logging.info("run on data: "+str(options.runOnData))
    if (not options.runOnData):
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

    logging.info("excluded systematics: "+str(options.excludedSystematic))
    
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
    logging.info("!!! parse fit result !!!")
    yieldSys,shapeSysList,correlations=parseFitResult(options.fitResult,options.excludedSystematic)
    signalYieldList=[]
    backgroundYieldList=[]
    for systematic in yieldSys:
        if systematic["name"] in SIGNAL:
            logging.debug("signal: "+systematic["name"]+": "+str(systematic["mean"])+" +- "+str(systematic["unc"])+" (rate)")
            signalYieldList.append(systematic)
        if systematic["name"] in BACKGROUND:
            logging.debug("background: "+systematic["name"]+": "+str(systematic["mean"])+" +- "+str(systematic["unc"])+" (rate)")
            backgroundYieldList.append(systematic)
    for systematic in shapeSysList:
        logging.debug(systematic["name"]+": "+str(systematic["mean"])+" +- "+str(systematic["unc"])+" (shape)")
    for systematic in correlations:
        logging.debug(str(systematic["name"])+": "+str(systematic["rho"])+" (correlation)")  
    
    #-----------------------------------------------------------------------------
    logging.info("!!! generate theta models !!!")
    #generateModelData(name=,histFile=,signalYieldList=,backgroundYieldList=,shapeSysList=,correlations=,dicePoisson=,)
    generateModelPE(  modelName=options.modelName,
                        histFile=options.histFile,
                        histPrefix=options.histogramPrefix,
                        signalYieldList=signalYieldList,
                        backgroundYieldList=backgroundYieldList,
                        shapeSysList=shapeSysList,
                        correlations=correlations,
                        binning=len(binningHist)-1,
                        ranges=[binningHist[0],binningHist[-1]],
                        dicePoisson=False,
                        bbUncertainties=True)
    
    #-----------------------------------------------------------------------------
    logging.info("!!! run theta !!!")           
    err,out=runCommand(["./execute_theta.sh",options.modelName+".cfg"])
    if not os.path.exists(options.modelName+".root"):
        logging.error("theta output was not created")
        logging.error(err)
        logging.error(out)
        sys.exit(-1)
        
    #-----------------------------------------------------------------------------
    logging.info("!!! run subtract !!!")
    #change for data the nominal model name!
    subtrackNominalBackground(options.modelName,options.modelName,options.histogramPrefix,binningMeasured)
    if not os.path.exists("subtracted_"+options.modelName+".root"):
        logging.error("unfolding output was not created")
        logging.error(err)
        logging.error(out)
        sys.exit(-1)
    #-----------------------------------------------------------------------------
    logging.info("!!! run unfolding !!!")
    responseMatrixFile,responseMatrixName=options.responseMatrix.split(":",1)
    err,out=runUnfolding("subtracted_"+options.modelName+".root","subtracted","histos",responseMatrixFile,responseMatrixName,"unfolded_"+options.modelName+".root",reg=0.35)
    if not os.path.exists("unfolded_"+options.modelName+".root"):
        logging.error("unfolding output was not created")
        logging.error(err)
        logging.error(out)
        sys.exit(-1)
    
    
