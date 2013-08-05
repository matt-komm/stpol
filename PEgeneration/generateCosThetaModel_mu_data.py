from ModelClasses import *
from optparse import OptionParser
import math

if __name__=="__main__":
    parser=OptionParser()
    parser.add_option("-i", "--input", dest="file", help="input signal sample")
    parser.add_option("-o", "--output", dest="output", help="output root file")
    
    (options, args)=parser.parse_args()

    histograminputfile="/home/fynu/mkomm/mu_cos_theta_mva_0_09/data.root"
    modelfilename="data_muon.cfg"
    outputfilename="data_muon.root"
    
    binning=14
    range=[-1.0,1.0]
   
    
    
    signalNameList={
        "cos_theta__DATA": {"yield":1.00,"unc":0.000000001}
    }
   
    backgroundNameList={

    }
    ntupleNameList={}
    ntupleNameList.update(signalNameList)
    ntupleNameList.update(backgroundNameList)
    
                           
    
    
    shapeSystematicDict={}
    
    
    file=open(modelfilename, "w")

    for shapeSystematic in shapeSystematicDict.values():
        file.write(shapeSystematic.toConfigString())
        
    yields=MultiDistribution("beta_yields")
    for ntuple in ntupleNameList:
        yields.addParameter("beta_"+ntuple,ntupleNameList[ntuple]["yield"],ntupleNameList[ntuple]["unc"])
    #yields.setCorrelation("beta_cos_theta__wzjets","beta_cos_theta__top",-0.925)
    
    file.write(yields.toConfigString())
    
    model=Model("cosTheta")#, {"bb_uncertainties":"true"})
    
    
    
    #yield_lumi=Distribution("beta_LUMI", "gauss", {"mean": "1.0", "width":"0.022", "range":"(\"-inf\",\"inf\")"})
    #file.write(yield_lumi.toConfigString())
    
    
    obs=Observable("cosTheta", binning, range)
    for ntuple in ntupleNameList.keys():
        comp=ObservableComponent("comp_"+ntuple)
        coeff=CoefficientMultiplyFunction()
        
        '''
        betaDist=Distribution("beta_"+ntuple, "log_normal", {"mu":str(ntupleNameList[ntuple]["yield"]), "sigma":str(ntupleNameList[ntuple]["unc"])})
        file.write(betaDist.toConfigString())
        coeff.addDistribution(betaDist)
        '''
        coeff.addDistribution(yields,"beta_"+ntuple)
        
        #coeff.addDistribution(yield_lumi)
        
        
        comp.setCoefficientFunction(coeff)
        hist=RootHistogram(ntuple+"-NOMINAL")
        hist.setFileName(histograminputfile)
        hist.setHistoName(ntuple)
        file.write(hist.toConfigString())
        comp.setNominalHistogram(hist)
        
        
        obs.addComponent(comp)
    model.addObservable(obs)
    
    file.write(model.toConfigString())


    file.write("\n")
    file.write("\n")
    
    file.write('pd = {\n')
    file.write('    type = "pseudodata_writer";\n')
    file.write('    name = "pd";\n')
    file.write('    observables = ("obs_cosTheta");\n')
    file.write('    write-data = true;\n')
    file.write('};\n')
    
    
    '''
    file.write("myminuit = {\n")
    file.write("type = \"root_minuit\";\n")
    file.write("};\n")
    file.write("mle = {\n")
    file.write("    type = \"mle\";\n")
    file.write("    name = \"mle\";\n")
    file.write("    //use minuit as minimizer and source of errors:\n")
    file.write("    minimizer = \"@myminuit\";\n")
    file.write("    write_covariance = true; //optional, default is false\n")
    file.write("    write_ks_ts = true; //optional, default is false\n")
    file.write("    //write out result for both parameters:\n")
    file.write("    parameters = ("+model.getParameterNames()+");\n");
    file.write("};\n")
    '''
    '''
    file.write("hist_data-TopQuarkEventView_mass_btaggedTop = {\n")
    file.write("    type = \"root_histogram_from_ntuple\";\n")
    file.write("    use_errors = true;\n")
    file.write("    binning = "+str(binning)+";\n")
    file.write("    filename = \"/user/komm/428_Summer_v10/data_mvaout.root\";\n")
    file.write("    range = ("+str(range[0])+","+str(range[1])+");\n")
    file.write("    cutstr = \"event_weight*pu_weight*((trig_HLT_IsoMu17_v5 == 1.) || (trig_HLT_IsoMu17_v6 == 1.) || (trig_HLT_IsoMu17_v8 == 1.) || (trig_HLT_IsoMu17_v9 == 1.) || (trig_HLT_IsoMu17_v10 == 1.) || (trig_HLT_IsoMu17_v11 == 1.))*(TopQuarkEventView_mt_wboson_beforePz>40.0)\";\n")
    file.write("    ntuplename = \"Data\";\n")
    file.write("    projectstr = \"TopQuarkEventView_mass_btaggedTop\";\n")
    file.write("    zerobin_fillfactor = 0.0001;\n")
    file.write("};\n")
    '''
    
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
    file.write('    model="@model_cosTheta";\n')
    file.write('    name="source";\n')
    file.write('    dice_poisson=false;\n')
    file.write('    rnd_gen={\n')
    file.write('         seed=126;//default of-1 means: use current time.\n')
    file.write('      };\n')
    file.write('    };\n')
    
    
    
    file.write('    n-events=1;\n')
    file.write('    model="@model_cosTheta";\n')
    file.write('    output_database={\n')
    file.write('        type="rootfile_database";\n')
    file.write('        filename="'+outputfilename+'";\n')
    file.write('    };\n')
    file.write('    producers=("@pd"\n')
    file.write('    );\n')
    file.write('};\n')
    
    file.write('options = {\n')
    file.write('           plugin_files = ("$THETA_DIR/lib/root.so", "$THETA_DIR/lib/core-plugins.so");\n')
    file.write('};\n')
    file.close()
