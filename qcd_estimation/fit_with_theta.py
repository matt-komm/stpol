import datetime
from theta_auto import *
from Fit import Fit

init_val = 1.2
init_val_wjets = 2.0
step = 0.0001

def get_model(infile, i=0):
    # Read in and build the model automatically from the histograms in the root file. 
    # This model will contain all shape uncertainties given according to the templates
    # which also includes rate changes according to the alternate shapes.
    # For more info about this model and naming conventuion, see documentation
    # of build_model_from_rootfile.
    model = build_model_from_rootfile(infile, include_mc_uncertainties = True)

    # If the prediction histogram is zero, but data is non-zero, teh negative log-likelihood
    # is infinity which causes problems for some methods. Therefore, we set all histogram
    # bin entries to a small, but positive value:
    model.fill_histogram_zerobins()

    # define what the signal processes are. All other processes are assumed to make up the 
    # 'background-only' model.
    model.set_signal_processes('qcd')

    # Add some lognormal rate uncertainties. The first parameter is the name of the
    # uncertainty (which will also be the name of the nuisance parameter), the second
    # is the 'effect' as a fraction, the third one is the process name. The fourth parameter
    # is optional and denotes the channel. The default '*' means that the uncertainty applies
    # to all channels in the same way.
    # Note that you can use the same name for a systematic here as for a shape
    # systematic. In this case, the same parameter will be used; shape and rate changes 
    # will be 100% correlated.
    print "Trying fit with uncertainty",init_val+i*step
    model.add_lognormal_uncertainty('nonqcd_rate', math.log(init_val+i*step), 'nonqcd')
    model.add_lognormal_uncertainty('wjets_rate', math.log(init_val_wjets+i*step), 'wjets')
    return model

def fit_qcd(variable, identifier, fit):
   indir = "templates/"
   outdir = "fits/"
   results_file = open('theta_results.txt', 'a')
   #results_file.write("#FITTING: "+str(datetime.now())+"\n")
   
   infile = indir+variable.shortName+"_templates_"+identifier+".root"
   outfile = outdir+variable.shortName+"_fit_"+identifier+".root"
   results_file.write("# "+identifier+"...")
   fit.coeff = {}   
   for i in range(0,1000):
      try:
         model = get_model(infile, i)  
         result = mle(model, "data", 1, ks=True, chi2=True)

         #print model.distribution
         #print "_____"
         #print "res_"+identifier+".res="+str(result)
         fit.result=result
        
         fit.coeff["wjets"] = math.log(init_val_wjets+i*step)
         fit.coeff["nonqcd"] = math.log(init_val+i*step)
         #print fit.result
         values = {}
         values_minus = {}
         values_plus = {}
         qc = result["qcd"]
         beta_signal = 0
         for name, value in qc.items():
            if name not in ["__chi2", "__ks", "__nll"]:
               val, var = value[0]
               values[name] = val
            if name == "beta_signal":
               beta_signal = val
               
         t = evaluate_prediction(model, values)
         results_file.write(str(init_val+i*step)+"\n")
                     
         for channel in t:
            for process in t[channel]:
               #print "channel",channel
               line1 = "res_"+identifier+"."+process+"="+str(t[channel][process].get_value_sum())
               line2 = "res_"+identifier+"."+process+"_uncert="+str(t[channel][process].get_value_sum_uncertainty())
               
               #print line1
               #print line2
               if process == "qcd":
                  qcd_yield = t[channel][process].get_value_sum()
                  uncert = t[channel][process].get_value_sum_uncertainty()
                  #print qcd_yield
               #use reflection here
               setattr(fit, process, t[channel][process].get_value_sum())
               setattr(fit, process+"_uncert", t[channel][process].get_value_sum_uncertainty())
               results_file.write(line1+"\n")
               results_file.write(line2+"\n")
                             
               #print channel+"_"+process+".vals="+str(t[channel][process].get_values())
               #print channel+"_"+process+".uncerts="+str(t[channel][process].get_uncertainties())
               #see add for toal uncert
         line3 = "res_"+identifier+".res="+str(result)
         results_file.write(line3+"\n")  
         results_file.write("\n")
         write_histograms_to_rootfile(t, outfile)         
         return (qcd_yield, uncert)
      except IOError as e:
         print e.strerror
         exit()
      except RuntimeError as rt:
         print "error"
         print str(rt)

      
