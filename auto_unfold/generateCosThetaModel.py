


from ModelClasses import *
from optparse import OptionParser
import math
import sys
import logging

if __name__=="__main__":
    parser=OptionParser()
    (options, args)=parser.parse_args()
    
    histograminputfile="data.root"
    modelfilename="PE"
    outputfilename="PE.root"
    
    binning=14
    range=[-1.0,1.0]
    signalNameList={
        "cos_theta__tchan": {"yield":1.082186,"unc":0.066}
    }
    backgroundNameList={
        "cos_theta__wzjets": {"yield":1.511,"unc":0.187},
        "cos_theta__qcd": {"yield":0.782740,"unc":0.730},
        "cos_theta__top": {"yield":0.979,"unc":0.090}
    }
    shapeSystematicDict={"En":Distribution("delta_JES", "gauss", {"mean":"0.0", "width":"1.0", "range":"(\"-inf\",\"inf\")"}),
                        
                        "Res":Distribution("delta_JER", "gauss", {"mean":"0.0", "width":"1.0", "range":"(\"-inf\",\"inf\")"}),
                        
                        "UnclusteredEn":Distribution("delta_EN", "gauss", {"mean":"0.0", "width":"1.0", "range":"(\"-inf\",\"inf\")"}),
                        "btaggingBC":Distribution("delta_BCtagging", "gauss", {"mean":"0.0", "width":"1.0", "range":"(\"-inf\",\"inf\")"}),
                        "btaggingL":Distribution("delta_Ltagging", "gauss", {"mean":"0.0", "width":"1.0", "range":"(\"-inf\",\"inf\")"}),
                        "leptonID":Distribution("delta_leptonID", "gauss", {"mean":"0.0", "width":"1.0", "range":"(\"-inf\",\"inf\")"}),
                        "leptonIso":Distribution("delta_leptonIso", "gauss", {"mean":"0.0", "width":"1.0", "range":"(\"-inf\",\"inf\")"}),
                        "leptonTrigger":Distribution("delta_leptonTrigger", "gauss", {"mean":"0.0", "width":"1.0", "range":"(\"-inf\",\"inf\")"}),                                                
                        "wjets_flat":Distribution("delta_wjetFLAT", "gauss", {"mean":"0.0", "width":"1.0", "range":"(\"-inf\",\"inf\")"}),
                        "wjets_shape":Distribution("delta_wjetSHAPE", "gauss", {"mean":"0.0", "width":"1.0", "range":"(\"-inf\",\"inf\")"})         
    }
    
    generateModel(histograminputfile,modelfilename,outputfilename,signalNameList,backgroundNameList)

def generateModelPE(modelName="mymodel",
                    histFile=None,
                    histPrefix="cos_theta",
                    signalYieldList=[],
                    backgroundYieldList=[],
                    shapeSysList=[],
                    correlations=[],
                    binning=1,
                    ranges=[-1.0,1.0],
                    dicePoisson=False,
                    bbUncertainties=True):
                    
    if histFile==None:
        logging.error("no input histfile specified during model generation")
        sys.exit(-1)
    
    
    file=open(modelName+".cfg", "w")
    '''
    for shapeSystematic in shapeSysList:
        
        file.write(shapeSystematic.toConfigString())
    '''
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
    if bbUncertainties:
        model=Model(modelName, {"bb_uncertainties":"true"})
        
    
    
    
    #yield_lumi=Distribution("beta_LUMI", "gauss", {"mean": "1.0", "width":"0.022", "range":"(\"-inf\",\"inf\")"})
    #file.write(yield_lumi.toConfigString())
    
    
    obs=Observable(histPrefix, binning, ranges)
    obsBG=Observable(histPrefix+"BG", binning, ranges)
    for ntuple in ntupleNameList:
        name=ntuple["name"]
        comp=ObservableComponent("comp_"+name)
        coeff=CoefficientMultiplyFunction()
        
        
        #betaDist=Distribution("beta_"+ntuple, "log_normal", {"mu":str(math.log(ntupleNameList[ntuple]["yield"])), "sigma":str(ntupleNameList[ntuple]["unc"])})
        #file.write(betaDist.toConfigString())
        #coeff.addDistribution(betaDist)
        
        coeff.addDistribution(sysDistributions,"sys_"+name)
        
        #coeff.addDistribution(yield_lumi)
        
        
        comp.setCoefficientFunction(coeff)
        hist=RootHistogram(name+"-NOMINAL")
        hist.setFileName(histFile)
        hist.setHistoName(histPrefix+"__"+name)
        file.write(hist.toConfigString())
        comp.setNominalHistogram(hist)
        
        for shapeSystematic in shapeSysList:
            sysName=shapeSystematic["name"]
            if name=="qcd":
                continue
            histUP=RootHistogram(name+"-"+sysName+"-UP")
            histUP.setFileName(histFile)
            histUP.setHistoName(histPrefix+"__"+name+"__"+sysName+"__up")
            histDOWN=RootHistogram(name+"-"+sysName+"-DOWN")
            histDOWN.setFileName(histFile)
            histDOWN.setHistoName(histPrefix+"__"+name+"__"+sysName+"__down")
            comp.addUncertaintyHistograms(histUP, histDOWN, sysDistributions,"sys_"+sysName)
            file.write(histUP.toConfigString())
            file.write(histDOWN.toConfigString())
        file.write("\n")
        
        obs.addComponent(comp)
        
        
        
        
        
    for ntuple in backgroundYieldList:
        name=ntuple["name"]
        compBG=ObservableComponent("comp_"+name)
        coeffBG=CoefficientConstantFunction("betaBG_"+name,ntuple["mean"])
        compBG.setCoefficientFunction(coeffBG)
        histBG=RootHistogram(name+"-BG")
        histBG.setFileName(histFile)
        histBG.setHistoName(histPrefix+"__"+name)
        file.write(histBG.toConfigString())
        compBG.setNominalHistogram(histBG)
        obsBG.addComponent(compBG)
        
        
    model.addObservable(obs)
    model.addObservable(obsBG)
    file.write(model.toConfigString())
    

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
    file.write('    rnd_gen={\n')
    file.write('         seed=126;//default of-1 means: use current time.\n')
    file.write('      };\n')
    file.write('    };\n')
    
    
    
    file.write('    n-events=10000;\n')
    file.write('    model="@model_'+modelName+'";\n')
    file.write('    output_database={\n')
    file.write('        type="rootfile_database";\n')
    file.write('        filename="'+modelName+'.root";\n')
    file.write('    };\n')
    file.write('    producers=("@pd"\n')
    file.write('    );\n')
    file.write('};\n')
    
    file.write('options = {\n')
    file.write('           plugin_files = ("$THETA_DIR/lib/root.so", "$THETA_DIR/lib/core-plugins.so");\n')
    file.write('};\n')
    file.close()
    
