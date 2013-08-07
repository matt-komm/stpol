import sys, os
from theta_auto import *
import math
import logging
import ROOT
#from final_fit.fit_systematics import *
from final_fit.fit import *
import argparse
from final_fit.plot_fit import plot_fit

logging.basicConfig(level=logging.INFO)

SIGNAL = 'tchan'


def get_model(infile, fit):
    model = build_model_from_rootfile(infile, include_mc_uncertainties = True, histogram_filter = fit.histofilter)    
    model.fill_histogram_zerobins()
    model.set_signal_processes(SIGNAL)
    return model


def get_options():
    options = Options()
    options.set("minimizer","strategy","newton_vanilla")
    #options.set("minimizer","strategy","tminuit")
    #options.set("minimizer","strategy","robust")
    #nuisance_constraint="shape:free;rate:free"
    options.set("global", "debug", "true")
    return options


def do_fit(fit, path):
    infile = path+"/"+fit.filename+".root"
    model = get_model(infile, fit)

    fit.add_uncertainties_to_model(model)
    
    options = get_options()
    result = mle(model, input = 'data', n=1, with_covariance = True, options=options)
    
    fitresults = {}
    values = {}

    for process in result[SIGNAL]:
        if '__' not in process:
            fitresults[process] = [result[SIGNAL][process][0][0], result[SIGNAL][process][0][1]]
            values[process] = fitresults[process][0]
    
    # covariance matrix
    pars = sorted(model.get_parameters([SIGNAL]))
    
    #print result[signal]
    cov = result[SIGNAL]['__cov'][0]
    
    (covm, corrm) = fit.makeCovMatrix(cov, pars)
    fit.write_results(fitresults, corrm)
    fit.plotMatrices(covm, corrm)

    #TODO fix
    #model_summary(model)
    #report.write_html('htmlout_fit')

    pred = evaluate_prediction(model, values, include_signal = True)
    try:
        os.makedirs("histos_fitted")
    except:
        pass
    try:
        os.makedirs("histos_fitted/"+fit.name)
    except:
        pass
        
    outfile = "histos_fitted/"+fit.name+"/fitted.root"
    spl = fit.filename.split("__")
    var = spl[1]
    write_histograms_to_rootfile(pred, outfile)
    #plot_fit(var, infile, outfile, result)

if __name__=="__main__":
    if "theta-auto.py" not in sys.argv[0]:
        raise Exception("Must run as `$STPOL_DIR/theta/utils2/theta-auto.py %s`" % (sys.argv[0]))
    try:
        sys.argv.pop(sys.argv.index("final_fit.py"))
    except ValueError:
        pass
    

    parser = argparse.ArgumentParser(description='Do the final fit')
    parser.add_argument('--channel', dest='channel', default=None, help="The lepton channel used for the fit")
    parser.add_argument('--path', dest='path', default="/hdfs/local/stpol/fit_histograms/07_08_2013/")
    parser.add_argument('--var', dest='var', default=None, help="Variable to fit on")
    #TODO    
    #parser.add_argument('--coupling', dest='coupling', choices=["powheg", "comphep", "anomWtb-0100", "anomWtb-unphys"], default="powheg", help="Coupling used for signal sample")
    #parser.add_argument('--asymmetry', dest='asymmetry', help="Asymmetry to reweight generated distribution to", default=None)
    args = parser.parse_args()
    
    if args.channel == None and args.var == None:
        fits = Fit.all_fits
    elif args.channel is not None and args.var is not None:
        fits = Fit.fits[args.channel].intersection(Fit.fits[args.var])
    elif args.channel is not None:
        fits = Fit.fits[args.channel]
    elif args.var is not None :
        fits = Fit.fits[args.var]

    for fit in fits:
            print "Fitting", fit.name
            do_fit(fit, args.path)
            print 
    
