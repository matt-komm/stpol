import datetime
from theta_auto import *
#from Fit import Fit
#from Variable import *
#from plot_fit import plot_fit2
from ROOT import TH1D, TFile
#from chi2_values import *

sys.path.append("/".join([os.environ["STPOL_DIR"], "qcd_estimation"]))
from analyze_fit import *
from results_tables import make_results_tables_old
from fit_components import *
from plot_fit import plot_fit2

init_val = 1.2
step = 0.0001

def get_model(infile, components, i=0):
    # Read in and build the model automatically from the histograms in the root file. 
    # This model will contain all shape uncertainties given according to the templates
    # which also includes rate changes according to the alternate shapes.
    # For more info about this model and naming conventuion, see documentation
    # of build_model_from_rootfile.
    print infile
    model = build_model_from_rootfile(infile, include_mc_uncertainties = True)

    # If the prediction histogram is zero, but data is non-zero, teh negative log-likelihood
    # is infinity which causes problems for some methods. Therefore, we set all histogram
    # bin entries to a small, but positive value:
    model.fill_histogram_zerobins()

    # define what the signal processes are. All other processes are assumed to make up the 
    # 'background-only' model.
    model.set_signal_processes('QCD')

    # Add some lognormal rate uncertainties. The first parameter is the name of the
    # uncertainty (which will also be the name of the nuisance parameter), the second
    # is the 'effect' as a fraction, the third one is the process name. The fourth parameter
    # is optional and denotes the channel. The default '*' means that the uncertainty applies
    # to all channels in the same way.
    # Note that you can use the same name for a systematic here as for a shape
    # systematic. In this case, the same parameter will be used; shape and rate changes 
    # will be 100% correlated.
    print "Trying fit with uncertainty",init_val+i*step
    print components
    for comp in components:
        print comp, component_uncertainties[comp]
        model.add_lognormal_uncertainty('%s_rate' % comp, math.log(component_uncertainties[comp]+i*step), comp)
    return model

def get_options():
    options = Options()
    options.set("minimizer","strategy","newton_vanilla")
    #options.set("minimizer","strategy","tminuit")
    #options.set("minimizer","strategy","fast")
    #options.set("minimizer","mcmc_iterations","10000000")
    #options.set("minimizer","always_mcmc","true")
    #options.set("minimizer","strategy","robust")
    #nuisance_constraint="shape:free;rate:free"
    options.set("global", "debug", "true")
    return options

def fit_qcd(identifier, components, extra = {}):
    indir = "templates/"
    outdir = "fits/"
    results_file = open('theta_results.txt', 'a')
    #results_file.write("#FITTING: "+str(datetime.now())+"\n")
   
    infile = "templates/%s.root" % (identifier)
    print "infile", infile
    outfilename = "fits/fit__%s.root" % (identifier)
    #outfile = TFile(outfilename, "recreate")
    results_file.write("# "+identifier+"...")
    #fit.coeff = {}   
    
    for i in range(0,1000):
        try:
            model = get_model(infile, components, i) 
            options = get_options() 
            result = mle(model, "data", 1, ks=True, chi2=True, options=options)
            print result
            res_qcd = result["QCD"]["beta_signal"][0]
            res_nonqcd = {}
            priors = {}
            for comp in components:
                res_nonqcd[comp] = result["QCD"]["%s_rate" % comp][0]
                priors[comp] = math.log(component_uncertainties[comp]+i*step)
            #print model.distribution
            #print "_____"
            #print "res_"+identifier+".res="+str(result)
            #fit.result=result
            result_tex = analyze_fit(infile, res_qcd, res_nonqcd, priors, extra=extra)
            plot_fit2(infile, res_qcd, res_nonqcd, priors, extra=extra)
            #print result_tex
            values = {}
            values_minus = {}
            values_plus = {}
            qc = result["QCD"]
            beta_signal = 0
            for name, value in qc.items():
                if name not in ["__chi2", "__ks", "__nll"]:
                   val, var = value[0]
                   values[name] = val
                if name == "beta_signal":
                   beta_signal = val
            t = evaluate_prediction(model, values)
            #model_summary(model, create_plots=True, all_nominal_templates=False, shape_templates=True, lnmode='sym')
            """results_file.write(str(init_val+i*step)+"\n")
                         
            for channel in t:
                for process in t[channel]:
                   #print "channel",channel
                   line1 = "res_"+identifier+"."+process+"="+str(t[channel][process].get_value_sum())
                   line2 = "res_"+identifier+"."+process+"_uncert="+str(t[channel][process].get_value_sum_uncertainty())
                   
                   print line1
                   print line2
                   if process == "QCD":
                      qcd_yield = t[channel][process].get_value_sum()
                      uncert = t[channel][process].get_value_sum_uncertainty()
                      print "yield", qcd_yield, uncert
                   #use reflection here
                   #setattr(fit, process, t[channel][process].get_value_sum())
                   #setattr(fit, process+"_uncert", t[channel][process].get_value_sum_uncertainty())
                   results_file.write(line1+"\n")
                   results_file.write(line2+"\n")
                                 
                   #print channel+"_"+process+".vals="+str(t[channel][process].get_values())
                   #print channel+"_"+process+".uncerts="+str(t[channel][process].get_uncertainties())
                   #see add for toal uncert
            #setattr(fit, "chi2", result["qcd"]["__chi2"])
            line3 = "res_"+identifier+".res="+str(result)
            print line3
            results_file.write(line3+"\n")  
            results_file.write("\n")
            write_histograms_to_rootfile(t, outfilename) 
            """
            return result_tex
            # (qcd_yield, uncert)
        except IOError as e:
            print e.strerror
            exit()
        except RuntimeError as rt:
             print "error"
             print str(rt)



if __name__ == "__main__":
    components = fit_components_regular_reproc  

    fitvars = []
    fitvars.append("qcd_mva")
    fitvars.append("mtw")
    fitvars.append("met")
    #fitvars.append(Variable("qcd_mva", -1, 1, bins=20, shortName="qcd_mva", displayName="BDT"))
    #fitvars.append(Variable("met", 0, 200, bins=40, shortName="met", displayName="MET"))
    #fitvars.append(Variable("mtw", 0, 200, bins=20, shortName="mtw", displayName="MTW"))
    jtset  = ["2j1t", "2j0t", "3j1t", "3j2t"]
    #jtset  = ["2j1t"]
    channels = ["mu","ele"]
    #channels = ["mu"]
    #lumi = 19700
    results = {}    
    nonqcdresults = {}
    qcdfactors = {}
    nonqcdfactors = {}
    results_tex = {}
    for channel in channels:
        for jt in jtset:
            for var in fitvars:
                #if var == "mtw" and channel == "ele": continue
                for cuttype in ["reversecut", ]:#"nocut", "qcdcut"]:
                    for added in ["11Jan_deltaR"]:
                        print "\n"
                        print "AAA", channel, jt, var, cuttype, added
                        identifier = "%s__%s__%s__%s__%s" % (var, jt, channel, cuttype, added)
                        #fit = Fit()
                        result_tex = fit_qcd(identifier, components)
                        results_tex[channel+jt+var+cuttype] = result_tex
                        for isovar in ["up", "down"]:
                            print "\n"
                            print var, channel, jt, cuttype, added, "isovar=%s" %isovar
                            identifier = "%s__%s__%s__%s__%s__isovar_%s" % (var, jt, channel, cuttype, added, isovar)
                            result_tex = fit_qcd(identifier, components, extra = {"isovar": isovar})
                            results_tex[channel+jt+var+cuttype+"isovar"+isovar] = result_tex
                        #(cst, retval,  nonqcdval) = plot_fit2(channel, var, fit, fit, lumi, jt, cuttype+"_"+added)
                        #for varmc in [" ", "varMC_up", "varMC_down", "varMC_QCDMC"]:
                        """for varmc in ["varMC_QCDMC", "varMC_QCDMC2J0T"]:
                            print "\n"
                            print var, channel, jt, cuttype, added
                            identifier = "%s__%s__%s__%s__%s" % (var, jt, channel, cuttype, added)
                            if len(varmc) > 1:
                                identifier += "__"+varmc
                            #fit = Fit()
                            result_tex = fit_qcd(identifier, extra = varmc)
                            results_tex[channel+jt+var+cuttype+varmc] = result_tex"""
    print "\n\n\n\n\n"
    #make_results_tables_old(results_tex, channels, jtset, fitvars, ["reversecut", "nocut", ], ["isovar"])
    make_results_tables_old(results_tex, channels, jtset, ["mtw"], ["reversecut"])




"""
if __name__ == "__main__":
    fitvars = []
    fitvars.append(Variable("qcd_mva", -1, 1, bins=20, shortName="qcd_mva", displayName="BDT"))
    fitvars.append(Variable("met", 0, 200, bins=40, shortName="met", displayName="MET"))
    fitvars.append(Variable("mtw", 0, 200, bins=20, shortName="mtw", displayName="MTW"))
    jtset  = ["2j1t", "2j0t", "3j1t", "3j2t"]
    channels = ["mu","ele"]
    lumi = 19700
    results = {}    
    nonqcdresults = {}
    qcdfactors = {}
    nonqcdfactors = {}
    for channel in channels:
        results[channel] = {}
        nonqcdresults[channel] = {}
        for jt in jtset:
            results[channel][jt] = {}
            nonqcdresults[channel][jt] = {}
            for var in fitvars:
                results[channel][jt][var.name] = {}
                nonqcdresults[channel][jt][var.name] = {}
                if var.name == "mtw" and channel == "ele": continue
                for added in ["added_13_05", "added_13_05_isodown", "added_13_05_isoup"]:
                    results[channel][jt][var.name][added] = {}
                    nonqcdresults[channel][jt][var.name][added] = {}
                    for cuttype in ["nocut", "reversecut"]:
                        print "\n\n"
                        print var.name, channel, jt, cuttype, added
                        fit = Fit()
                        fit_qcd(channel, var, jt, fit, cuttype+"_"+added)
                        #print fit
                        #print "___"
                        #print fit.result
                        (cst, retval,  nonqcdval) = plot_fit2(channel, var, fit, fit, lumi, jt, cuttype+"_"+added)
                        chi2 = chi2s[channel][added][cuttype][var.name][jt] 
                        retval += " & %.2f" % chi2
                        results[channel][jt][var.name][added][cuttype] = retval
                        nonqcdresults[channel][jt][var.name][added][cuttype] = nonqcdval
                        qcdfactors[channel+jt+var.name+added+cuttype] = fit.result["qcd"]["beta_signal"][0][0]
                        nonqcdfactors[channel+jt+var.name+added+cuttype] = math.e**((fit.result["qcd"]["nonqcd_rate"][0][0])*fit.coeff["nonqcd"])
    
    for channel in channels:
        print 'scale_factors_spec["'+channel+'"] = {}'
        print 'nonqcd_scale_factors_spec["'+channel+'"] = {}'
        for jt in jtset:
            print 'scale_factors_spec["'+channel+'"]["'+jt+'"] = {}'
            print 'nonqcd_scale_factors_spec["'+channel+'"]["'+jt+'"] = {}'
            for var in fitvars:
                if var.name == "mtw" and channel == "ele": continue
                print 'scale_factors_spec["'+channel+'"]["'+jt+'"]["'+var.name+'"] = {}'
                print 'nonqcd_scale_factors_spec["'+channel+'"]["'+jt+'"]["'+var.name+'"] = {}'
                for added in ["added_13_05", "added_13_05_isodown", "added_13_05_isoup"]:
                    print 'scale_factors_spec["'+channel+'"]["'+jt+'"]["'+var.name+'"]["'+added+'"] = {}'
                    print 'nonqcd_scale_factors_spec["'+channel+'"]["'+jt+'"]["'+var.name+'"]["'+added+'"] = {}'
                    for cuttype in ["nocut", "reversecut"]:
                        print 'scale_factors_spec["'+channel+'"]["'+jt+'"]["'+var.name+'"]["'+added+'"]["'+cuttype+'"] = '+str(qcdfactors[channel+jt+var.name+added+cuttype])
                        print 'nonqcd_scale_factors_spec["'+channel+'"]["'+jt+'"]["'+var.name+'"]["'+added+'"]["'+cuttype+'"] = '+str(nonqcdfactors[channel+jt+var.name+added+cuttype])
                        
    
    for channel in channels:
        for jt in jtset:
            print "%s\t| %s \t | %10s \t | %16s \t | %s \t\t | %s \t\t | %s  \t | %s \t\t | %s " % ("Channel", "Region", "Variable", "Iso", "Cut", "QCD SF", "QCD Yield", "Non-QCD SF", "Chi2")
            for var in fitvars:
                if var.name == "mtw" and channel == "ele": continue
                for added in ["added_13_05", "added_13_05_isodown", "added_13_05_isoup"]:
                    for cuttype in ["nocut", "reversecut"]:
                        print "%s \t & %s \t & %10s \t & %16s \t & %s \t & %s" % (channel, jt, var.name, added, cuttype, results[channel][jt][var.name][added][cuttype])
    
    #report.write_html('htmlout')
"""
