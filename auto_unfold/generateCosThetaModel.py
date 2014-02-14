


from ModelClasses import *
from optparse import OptionParser
import math
import sys
import os
import logging
import random
import ROOT

ROOT.gROOT.SetBatch(True)

def getHistogram(fileName,histName):
    f=ROOT.TFile(fileName)
    hist = f.Get(histName)
    if (hist==None):
        f.Close()
        return None
    hist.SetDirectory(0)
    return hist

def plotSysTemplates(fileName,signalSetDict,backgroundSetDict,shapeSysDict,outputFolder):
    colorDict={
        "beta_signal":ROOT.kMagenta,
        "qcd":ROOT.kGray,
        "ttjets":ROOT.kRed+1,
        "wzjets":ROOT.kGreen+1
    }
    histStackNominal=ROOT.THStack("stackNominal"+str(random.random()),"stack")
    sysStackDictUP={}
    sysStackDictDOWN={}
    for sysName in shapeSysDict.keys():
        sysStackDictUP[sysName]=ROOT.THStack(sysName+"up"+str(random.random()),"")
        sysStackDictDOWN[sysName]=ROOT.THStack(sysName+"up"+str(random.random()),"")
    legend=ROOT.TLegend(0.76,0.6,0.99,0.95)
    for backgroundSet in backgroundSetDict.keys():
        for histName in backgroundSetDict[backgroundSet]:
            hist=getHistogram(fileName,histName)
            hist.SetLineWidth(0)
            hist.SetFillStyle(1001)
            if colorDict.has_key(backgroundSet):
                hist.SetFillColor(colorDict[backgroundSet])
            else:
                hist.SetFillColor(ROOT.kAzure-4)
            histStackNominal.Add(hist,"hist F")
            
                        
            for sysName in shapeSysDict.keys():
                histSysUP=getHistogram(fileName,histName+"__"+sysName+"__up")
                histSysDOWN=getHistogram(fileName,histName+"__"+sysName+"__down")
                #use nominal template if sys variation not yet present
                if histSysUP==None:
                    histSysUP=ROOT.TH1D(hist)
                if histSysDOWN==None:
                    histSysDOWN=ROOT.TH1D(hist)
                    
                histSysUP.SetMarkerSize(1.0)
                histSysUP.SetMarkerStyle(22)
                histSysUP.SetFillStyle(0)
                histSysUP.SetLineColor(ROOT.kGray+2)
                histSysUP.SetMarkerColor(ROOT.kGray+1)
                sysStackDictUP[sysName].Add(histSysUP,"P")
                
                histSysDOWN.SetMarkerSize(1.0)
                histSysDOWN.SetMarkerStyle(23)
                histSysDOWN.SetFillStyle(0)
                histSysDOWN.SetLineColor(ROOT.kGray+2)
                histSysDOWN.SetMarkerColor(ROOT.kGray+1)
                sysStackDictDOWN[sysName].Add(histSysDOWN,"P")
            
        legend.AddEntry(hist,backgroundSet,"F")
        
        
    for signalSet in signalSetDict.keys():
        for histName in signalSetDict[signalSet]:
            hist=getHistogram(fileName,histName)
            hist.SetLineWidth(0)
            hist.SetFillStyle(1001)
            if colorDict.has_key(signalSet):
                hist.SetFillColor(colorDict[signalSet])
            else:
                hist.SetFillColor(ROOT.kAzure-4)
            histStackNominal.Add(hist,"hist F")
            
            for sysName in shapeSysDict.keys():
                histSysUP=getHistogram(fileName,histName+"__"+sysName+"__up")
                histSysDOWN=getHistogram(fileName,histName+"__"+sysName+"__down")
                #use nominal template if sys variation not yet present
                if histSysUP==None:
                    histSysUP=ROOT.TH1D(hist)
                if histSysDOWN==None:
                    histSysDOWN=ROOT.TH1D(hist)
                    
                histSysUP.SetMarkerSize(1.0)
                histSysUP.SetMarkerStyle(22)
                histSysUP.SetFillStyle(0)
                histSysUP.SetLineColor(ROOT.kGray+2)
                histSysUP.SetMarkerColor(ROOT.kGray+1)
                sysStackDictUP[sysName].Add(histSysUP,"P")
                
                histSysDOWN.SetMarkerSize(1.0)
                histSysDOWN.SetMarkerStyle(23)
                histSysDOWN.SetFillStyle(0)
                histSysDOWN.SetLineColor(ROOT.kGray+2)
                histSysDOWN.SetMarkerColor(ROOT.kGray+1)
                sysStackDictDOWN[sysName].Add(histSysDOWN,"P")
                
        legend.AddEntry(hist,signalSet,"F")
        
    
    for sysName in shapeSysDict.keys():
        canvas=ROOT.TCanvas("canvas"+sysName+str(random.random()),"",800,600)
        canvas.cd(1)
        ROOT.gPad.SetRightMargin(0.25)
        histStackNominal.SetTitle(sysName)
        histStackNominal.Draw()
        histStackNominal.SetMaximum(histStackNominal.GetMaximum()*1.4)
        histStackNominal.Draw()
        sysStackDictDOWN[sysName].Draw("Same")
        sysStackDictUP[sysName].Draw("Same")
        legend.Draw("Same")
        canvas.Print(os.path.join(outputFolder,"sysTempl__"+sysName+".pdf"))
    
def checkHistogramExistence(fileName,histoName,debug=False):
    if not os.path.exists(fileName):
        logging.warning("file '"+fileName+"' does not exists containing histogram '"+histoName+"', will be ignored")
        return False
    file = ROOT.TFile(fileName,"r")
    obj=file.Get(histoName)
    if (obj==None):
        logging.warning("histogram '"+histoName+"' does not exits in file '"+fileName+"', will be ignored")
        return False
    if obj.GetEntries()==0:
        logging.warning("histogram '"+histoName+"' in file '"+fileName+"' contains 0 entries, will be ignored")
        return False
    if not debug:
        return True
    weightSum=0.0
    sumMC=0.0
    #print histoName
    for ibin in range(obj.GetNbinsX()):
        obs=max(obj.GetBinContent(ibin+1),0.0000001)
        err=max(obj.GetBinError(ibin+1),0.000000000000000001)
        w=err**2/obs
        n=obs**2/err**2
        weightSum+=w
        sumMC+=n
        #print "\tobs:",round(obs,2),"\terr:",round(err,3),"\tw:",round(w,4),"\tn:",round(n,1)
    avg_weight=weightSum/obj.GetNbinsX()
    
    return True
    
def generateModelPE(modelName="mymodel",
                    outputFolder="mymodel",
                    histFile=None,
                    prefix="cos_theta",
                    signalSetDict={},
                    backgroundSetDict={},
                    yieldSysDict={},
                    shapeSysDict={},
                    corrList=[],
                    binning=1,
                    ranges=[-1.0,1.0],
                    dicePoisson=True,
                    mcUncertainty=True):
                    
    if histFile==None:
        logging.error("no input histfile specified during model generation")
        sys.exit(-1)
    
    file=open(os.path.join(outputFolder,modelName+".cfg"), "w")
    
    sysDistributions=MultiDistribution("sysDist")
    for key in yieldSysDict.keys():
        name = "sys_"+key
        mean = yieldSysDict[key]["mean"]
        unc = yieldSysDict[key]["unc"]
        sysDistributions.addParameter(name,mean,unc)
    for key in shapeSysDict.keys():
        name ="sys_"+key
        mean =shapeSysDict[key]["mean"]
        unc=shapeSysDict[key]["unc"]
        sysDistributions.addParameter(name,mean,unc)
    for corr in corrList:
        name1="sys_"+corr["name"][0]
        name2="sys_"+corr["name"][1]
        rho=corr["rho"]
        sysDistributions.setCorrelation(name1,name2,rho)
    
    file.write(sysDistributions.toConfigString())
    
    plotSysTemplates(histFile,signalSetDict,backgroundSetDict,shapeSysDict,outputFolder)
    
    model=Model(modelName)
    if mcUncertainty:
        model=Model(modelName, {"bb_uncertainties":"true"})

    #yield_lumi=Distribution("beta_LUMI", "gauss", {"mean": "1.0", "width":"0.022", "range":"(\"-inf\",\"inf\")"})
    #file.write(yield_lumi.toConfigString())
    totalSetDict={}
    totalSetDict.update(signalSetDict)
    totalSetDict.update(backgroundSetDict)
    
    obs=Observable(prefix, binning, ranges)
    for histSet in totalSetDict.keys():
        for histName in totalSetDict[histSet]:
            if not checkHistogramExistence(histFile,histName,debug=True):
                continue
            comp=ObservableComponent(histName)
            coeff=CoefficientMultiplyFunction()
            coeff.addDistribution(sysDistributions,"sys_"+histSet)
            comp.setCoefficientFunction(coeff)
 
            hist=RootHistogram(histName+"-NOMINAL",{"use_errors":"true"})
            hist.setFileName(histFile)
            hist.setHistoName(histName)
            file.write(hist.toConfigString())
            comp.setNominalHistogram(hist)
            
            for sysName in shapeSysDict.keys():
                if not checkHistogramExistence(histFile,histName+"__"+sysName+"__up"):
                    continue
                if not checkHistogramExistence(histFile,histName+"__"+sysName+"__down"):
                    continue
                histUP=RootHistogram(histName+"-"+sysName+"-UP",{"use_errors":"true"})
                histUP.setFileName(histFile)
                histUP.setHistoName(histName+"__"+sysName+"__up")
                
                histDOWN=RootHistogram(histName+"-"+sysName+"-DOWN",{"use_errors":"true"})
                histDOWN.setFileName(histFile)
                histDOWN.setHistoName(histName+"__"+sysName+"__down")
                comp.addUncertaintyHistograms(histUP, histDOWN, sysDistributions,"sys_"+sysName)
                file.write(histUP.toConfigString())
                file.write(histDOWN.toConfigString())
            file.write("\n")
            
            obs.addComponent(comp)
           
        
    model.addObservable(obs)
    file.write(model.toConfigString())
    _writeFile(file,outputFolder,modelName,dicePoisson=dicePoisson,mcUncertainty=mcUncertainty)
    file.close()
    
    
def generateNominalSignal(modelName="mymodel",
                    outputFolder="mymodel",
                    histFile=None,
                    prefix="cos_theta",
                    signalSetDict={},
                    backgroundSetDict={},
                    yieldSysDict={},
                    shapeSysDict={},
                    corrList=[],
                    binning=1,
                    ranges=[-1.0,1.0],
                    dicePoisson=True,
                    mcUncertainty=True):
                    
    if histFile==None:
        logging.error("no input histfile specified during model generation")
        sys.exit(-1)
    
    file=open(os.path.join(outputFolder,modelName+".cfg"), "w")
    
    sysDistributions=MultiDistribution("sysDist")
    for key in signalSetDict.keys():
        name = "sys_"+key
        mean = yieldSysDict[key]["mean"]
        unc = 0.000000001
        sysDistributions.addParameter(name,mean,unc)
    
    file.write(sysDistributions.toConfigString())
    
    
    model=Model(modelName)
    if mcUncertainty:
        model=Model(modelName, {"bb_uncertainties":"true"})

    #yield_lumi=Distribution("beta_LUMI", "gauss", {"mean": "1.0", "width":"0.022", "range":"(\"-inf\",\"inf\")"})
    #file.write(yield_lumi.toConfigString())
    totalSetDict={}
    totalSetDict.update(signalSetDict)
    
    obs=Observable(prefix, binning, ranges)
    for histSet in totalSetDict.keys():
        for histName in totalSetDict[histSet]:
            if not checkHistogramExistence(histFile,histName,debug=True):
                continue
            comp=ObservableComponent(histName)
            coeff=CoefficientMultiplyFunction()
            coeff.addDistribution(sysDistributions,"sys_"+histSet)
            comp.setCoefficientFunction(coeff)
 
            hist=RootHistogram(histName+"-NOMINAL",{"use_errors":"true"})
            hist.setFileName(histFile)
            hist.setHistoName(histName)
            file.write(hist.toConfigString())
            comp.setNominalHistogram(hist)
            
            obs.addComponent(comp)
           
        
    model.addObservable(obs)
    file.write(model.toConfigString())
    _writeFile(file,outputFolder,modelName,dicePoisson=False,mcUncertainty=False,experiments=1)
    file.close()
       
    
def generateNominalBackground(modelName="mymodel",
                    outputFolder="mymodel",
                    histFile=None,
                    prefix="cos_theta",
                    signalSetDict={},
                    backgroundSetDict={},
                    yieldSysDict={},
                    shapeSysDict={},
                    corrList=[],
                    binning=1,
                    ranges=[-1.0,1.0],
                    dicePoisson=True,
                    mcUncertainty=True):
                    
    if histFile==None:
        logging.error("no input histfile specified during model generation")
        sys.exit(-1)
    
    file=open(os.path.join(outputFolder,modelName+".cfg"), "w")
    
    sysDistributions=MultiDistribution("sysDist")
    for key in backgroundSetDict.keys():
        name = "sys_"+key
        mean = yieldSysDict[key]["mean"]
        unc = 0.000000001
        sysDistributions.addParameter(name,mean,unc)
    
    file.write(sysDistributions.toConfigString())
    
    model=Model(modelName)
    if mcUncertainty:
        model=Model(modelName, {"bb_uncertainties":"true"})

    #yield_lumi=Distribution("beta_LUMI", "gauss", {"mean": "1.0", "width":"0.022", "range":"(\"-inf\",\"inf\")"})
    #file.write(yield_lumi.toConfigString())
    totalSetDict={}
    totalSetDict.update(backgroundSetDict)
    
    obs=Observable(prefix, binning, ranges)
    for histSet in totalSetDict.keys():
        for histName in totalSetDict[histSet]:
            if not checkHistogramExistence(histFile,histName,debug=True):
                continue
            comp=ObservableComponent(histName)
            coeff=CoefficientMultiplyFunction()
            coeff.addDistribution(sysDistributions,"sys_"+histSet)
            comp.setCoefficientFunction(coeff)
 
            hist=RootHistogram(histName+"-NOMINAL",{"use_errors":"true"})
            hist.setFileName(histFile)
            hist.setHistoName(histName)
            file.write(hist.toConfigString())
            comp.setNominalHistogram(hist)
            
            obs.addComponent(comp)
           
        
    model.addObservable(obs)
    file.write(model.toConfigString())
    _writeFile(file,outputFolder,modelName,dicePoisson=False,mcUncertainty=False,experiments=1)
    file.close()
    
'''    
def generateModelData(modelName="mymodel",
                    outputFolder="mymodel",
                    histFile=None,
                    prefix="cos_theta",
                    signalSetDict={},
                    backgroundSetDict={},
                    yieldSysDict={},
                    shapeSysDict={},
                    corrList=[],
                    binning=1,
                    ranges=[-1.0,1.0],
                    dicePoisson=True,
                    mcUncertainty=True):
                    
    if histFile==None:
        logging.error("no input histfile specified during model generation")
        sys.exit(-1)
    
    file=open(os.path.join(outputFolder,modelName+".cfg"), "w")
    
    sysDistributions=MultiDistribution("sysDist")
    for key in yieldSysDict.keys():
        name = "sys_"+key
        mean = yieldSysDict[key]["mean"]
        unc = yieldSysDict[key]["unc"]
        sysDistributions.addParameter(name,mean,unc)
    for key in shapeSysDict.keys():
        name ="sys_"+key
        mean =shapeSysDict[key]["mean"]
        unc=shapeSysDict[key]["unc"]
        sysDistributions.addParameter(name,mean,unc)
    for corr in corrList:
        name1="sys_"+corr["name"][0]
        name2="sys_"+corr["name"][1]
        rho=corr["rho"]
        sysDistributions.setCorrelation(name1,name2,rho)
    
    file.write(sysDistributions.toConfigString())
    
    
    model=Model(modelName)
    if mcUncertainty:
        model=Model(modelName, {"bb_uncertainties":"true"})

    #yield_lumi=Distribution("beta_LUMI", "gauss", {"mean": "1.0", "width":"0.022", "range":"(\"-inf\",\"inf\")"})
    #file.write(yield_lumi.toConfigString())
    totalSetDict={}
    totalSetDict.update(signalSetDict)
    totalSetDict.update(backgroundSetDict)
    
    obs=Observable(prefix, binning, ranges)
    for histSet in totalSetDict.keys():
        for histName in totalSetDict[histSet]:
            if not checkHistogramExistence(histFile,histName,debug=True):
                continue
            comp=ObservableComponent(histName)
            coeff=CoefficientMultiplyFunction()
            coeff.addDistribution(sysDistributions,"sys_"+histSet)
            comp.setCoefficientFunction(coeff)
 
            hist=RootHistogram(histName+"-NOMINAL",{"use_errors":"true"})
            hist.setFileName(histFile)
            hist.setHistoName(histName)
            file.write(hist.toConfigString())
            comp.setNominalHistogram(hist)
            
            for sysName in shapeSysDict.keys():
                if not checkHistogramExistence(histFile,histName+"__"+sysName+"__up"):
                    continue
                if not checkHistogramExistence(histFile,histName+"__"+sysName+"__down"):
                    continue
                histUP=RootHistogram(histName+"-"+sysName+"-UP",{"use_errors":"true"})
                histUP.setFileName(histFile)
                histUP.setHistoName(histName+"__"+sysName+"__up")
                
                histDOWN=RootHistogram(histName+"-"+sysName+"-DOWN",{"use_errors":"true"})
                histDOWN.setFileName(histFile)
                histDOWN.setHistoName(histName+"__"+sysName+"__down")
                comp.addUncertaintyHistograms(histUP, histDOWN, sysDistributions,"sys_"+sysName)
                file.write(histUP.toConfigString())
                file.write(histDOWN.toConfigString())
            file.write("\n")
            
            obs.addComponent(comp)
           
        
    model.addObservable(obs)
    file.write(model.toConfigString())
    _writeFile(file,outputFolder,modelName,dicePoisson=dicePoisson,mcUncertainty=mcUncertainty)
    file.close()
'''             
                    
                    
def _writeFile(file,outputFolder,modelName,dicePoisson=True,mcUncertainty=True,experiments=10000): 

    file.write("\n")
    file.write("\n")
    
    file.write('pd = {\n')
    file.write('    type = "pseudodata_writer";\n')
    file.write('    name = "pd";\n')
    #file.write('    observables = ("obs_cosTheta","obs_cosThetaBG");\n')
    file.write('    write-data = true;\n')
    file.write('};\n')
    
    file.write('main={\n')
    '''
    file.write('    data_source={\n')
    file.write('        type="histo_source";\n')
    file.write('        name="data";\n')
    file.write('        obs_cosTheta="@hist_data-TopQuarkEventView_mass_btaggedTop";\n')
    file.write('    };\n')
    '''
    file.write('    data_source={\n')
    file.write('    type="model_source";\n')
    file.write('    model="@model_'+modelName+'";\n')
    file.write('    name="source";\n')
    if dicePoisson:
        file.write('    dice_poisson=true;\n')
    else:
        file.write('    dice_poisson=false;\n')
    if mcUncertainty:    
        file.write('    dice_template_uncertainties = true;\n')
    else:
        file.write('    dice_template_uncertainties = false;\n')
    file.write('    rnd_gen={\n')
    file.write('         seed=126;//default of-1 means: use current time.\n')
    file.write('      };\n')
    file.write('    };\n')
    
    
    
    file.write('    n-events='+str(experiments)+';\n')
    file.write('    model="@model_'+modelName+'";\n')
    file.write('    output_database={\n')
    file.write('        type="rootfile_database";\n')
    file.write('        filename="'+os.path.join(outputFolder,modelName+'.root')+'";\n')
    file.write('    };\n')
    file.write('    producers=("@pd"\n')
    file.write('    );\n')
    file.write('};\n')
    
    file.write('options = {\n')
    file.write('           plugin_files = ("$THETA_DIR/lib/root.so", "$THETA_DIR/lib/core-plugins.so");\n')
    file.write('};\n')

    
