


from ModelClasses import *
from optparse import OptionParser
import math
import sys
import os
import logging
import ROOT


def checkHistogramExistence(fileName,histoName):
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
    return True
    
def generateModelPE(modelName="mymodel",
                    outputFolder="mymodel",
                    histFile=None,
                    histPrefix="cos_theta",
                    signalYieldList=[],
                    backgroundYieldList=[],
                    shapeSysList=[],
                    correlations=[],
                    binning=1,
                    ranges=[-1.0,1.0],
                    dicePoisson=True,
                    mcUncertainty=True):
                    
    if histFile==None:
        logging.error("no input histfile specified during model generation")
        sys.exit(-1)
    
    
    file=open(os.path.join(outputFolder,modelName+".cfg"), "w")
    ntupleNameList=[]
    ntupleNameList.extend(signalYieldList)
    ntupleNameList.extend(backgroundYieldList)
    
    sysDistributions=MultiDistribution("sysDist")
    for yieldSys in signalYieldList:
        name ="sys_"+yieldSys["name"]
        mean =yieldSys["mean"]
        unc=yieldSys["unc"]
        sysDistributions.addParameter(name,str(mean),unc)
    for yieldSys in backgroundYieldList:
        name ="sys_"+yieldSys["name"]
        mean =yieldSys["mean"]
        unc=yieldSys["unc"]
        sysDistributions.addParameter(name,str(mean),unc)
    for shapeSys in shapeSysList:
        name ="sys_"+shapeSys["name"]
        mean =shapeSys["mean"]
        unc=shapeSys["unc"]
        sysDistributions.addParameter(name,str(mean),unc)
    for corr in correlations:
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
    
    
    obs=Observable(histPrefix, binning, ranges)
    for ntuple in ntupleNameList:
        name=ntuple["name"]
        if not checkHistogramExistence(histFile,histPrefix+"__"+name):
            continue
        comp=ObservableComponent("comp_"+name)
        coeff=CoefficientMultiplyFunction()
        
        
        #betaDist=Distribution("beta_"+ntuple, "log_normal", {"mu":str(math.log(ntupleNameList[ntuple]["yield"])), "sigma":str(ntupleNameList[ntuple]["unc"])})
        #file.write(betaDist.toConfigString())
        #coeff.addDistribution(betaDist)
        
        coeff.addDistribution(sysDistributions,"sys_"+name)
        
        #coeff.addDistribution(yield_lumi)
        
        
        comp.setCoefficientFunction(coeff)
        hist=RootHistogram(name+"-NOMINAL",{"use_errors":"true"})
        hist.setFileName(histFile)
        hist.setHistoName(histPrefix+"__"+name)
        file.write(hist.toConfigString())
        comp.setNominalHistogram(hist)
        
        for shapeSystematic in shapeSysList:
            sysName=shapeSystematic["name"]
            if not checkHistogramExistence(histFile,histPrefix+"__"+name+"__"+sysName+"__up"):
                continue
            if not checkHistogramExistence(histFile,histPrefix+"__"+name+"__"+sysName+"__down"):
                continue
            histUP=RootHistogram(name+"-"+sysName+"-UP",{"use_errors":"true"})
            histUP.setFileName(histFile)
            histUP.setHistoName(histPrefix+"__"+name+"__"+sysName+"__up")
            histDOWN=RootHistogram(name+"-"+sysName+"-DOWN",{"use_errors":"true"})
            histDOWN.setFileName(histFile)
            histDOWN.setHistoName(histPrefix+"__"+name+"__"+sysName+"__down")
            comp.addUncertaintyHistograms(histUP, histDOWN, sysDistributions,"sys_"+sysName)
            file.write(histUP.toConfigString())
            file.write(histDOWN.toConfigString())
        file.write("\n")
        
        obs.addComponent(comp)
           
        
    model.addObservable(obs)
    file.write(model.toConfigString())
    _writeFile(file,outputFolder,modelName,dicePoisson=dicePoisson,mcUncertainty=mcUncertainty)
    file.close()
    
def generateNominalBackground(modelName="mymodel",
                    outputFolder="mymodel",
                    histFile=None,
                    histPrefix="cos_theta",
                    backgroundYieldList=[],
                    binning=1,
                    ranges=[-1.0,1.0]):
                    
    if histFile==None:
        logging.error("no input histfile specified during model generation")
        sys.exit(-1)
    
    
    file=open(os.path.join(outputFolder,modelName+".cfg"), "w")
    
    model=Model(modelName)
    
    obsBG=Observable(histPrefix, binning, ranges)
            
    for ntuple in backgroundYieldList:
        name=ntuple["name"]
        compBG=ObservableComponent("comp_"+name)
        coeffBG=CoefficientConstantFunction("beta_"+name,ntuple["mean"])
        compBG.setCoefficientFunction(coeffBG)
        histBG=RootHistogram(name,{"use_errors":"true"})
        histBG.setFileName(histFile)
        histBG.setHistoName(histPrefix+"__"+name)
        file.write(histBG.toConfigString())
        compBG.setNominalHistogram(histBG)
        obsBG.addComponent(compBG)
        
        
    model.addObservable(obsBG)
    file.write(model.toConfigString())
    _writeFile(file,outputFolder,modelName,dicePoisson=False,mcUncertainty=False,experiments=1)
    file.close()
    
    
def generateModelData(modelName="mymodel",
                    outputFolder="mymodel",
                    dataHist=None,
                    histPrefix="",
                    binning=1,
                    ranges=[-1.0,1.0]):
                    
                    
    if dataHist==None:
        logging.error("no input histfile specified during model generation")
        sys.exit(-1)
    
    
    file=open(os.path.join(outputFolder,modelName+".cfg"), "w")

    model=Model(modelName)
    
    
    obs=Observable(histPrefix, binning, ranges)
    
    histFile,histName=dataHist.rsplit(":",1)
    if not checkHistogramExistence(histFile,histName):
        logging.error("data histogram '"+histName+"' in file '"+histFile+"' not found")
        sys.exit(-1)
    comp=ObservableComponent("comp_data")
    coeff=CoefficientConstantFunction("beta-data")
    
    comp.setCoefficientFunction(coeff)
    hist=RootHistogram("data-NOMINAL",{"use_errors":"false"})
    hist.setFileName(histFile)
    hist.setHistoName(histName)
    file.write(hist.toConfigString())
    comp.setNominalHistogram(hist)
    
    file.write("\n")
    
    obs.addComponent(comp)
      
    model.addObservable(obs)
    file.write(model.toConfigString())
    _writeFile(file,outputFolder,modelName,dicePoisson=False,mcUncertainty=False,experiments=1)
    file.close() 
                    
                    
                    
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

    
