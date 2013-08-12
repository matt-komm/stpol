import sys, os
import math
from fit import *
#from theta_auto import *
import logging
import ROOT
#from final_fit.fit_systematics import *
import argparse
from plot_fit import plot_fit

logging.basicConfig(level=logging.INFO)
"""
Script for final fit

The fit parameters are specified in fit.py
The default shape uncertainties are ["__En", "Res", "ttbar_scale", "ttbar_matching", "iso"]  - other do not change the shape.
The systematics which match in shape with the nominal should not be used for the fit as the fit might not converge. The are absorbed in the rate uncertainties.
Check with $STPOL_DIR/final_fit/compare_template_shapes.py when adding new systematics-
As a default, unconstrained prior rate uncertaintes are applied for signal and wzjets while "other" (top+qcd) gets a 20% gaussian uncertainty.
By default, the output file will also contain the correlation between ("wzjets", "other"). Others can be added as needed.
"""
SIGNAL = 'tchan'
def get_model(infile, fit):
    model = build_model_from_rootfile(infile, include_mc_uncertainties = True, histogram_filter = fit.histofilter, transform_histo = fit.transformHisto)
    model.fill_histogram_zerobins()
    model.set_signal_processes(SIGNAL)
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
    fit.write_results(fitresults, corrm, fit)
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
    write_histograms_to_rootfile(pred, outfile)
    #FIXME: Secgmentation faults for more than 2 fits...
    #plot_fit(fit, infile, outfile, result)

if __name__=="__main__":
    if "theta-auto.py" not in sys.argv[0]:
        raise Exception("Must run as `$STPOL_DIR/theta/utils2/theta-auto.py %s`" % (sys.argv[0]))
    try:
        sys.argv.pop(sys.argv.index("final_fit.py"))
    except ValueError:
        pass


    parser = argparse.ArgumentParser(description='Do the final fit')
    parser.add_argument('--channel', default=None, help="The lepton channel used for the fit")
    parser.add_argument('--path', default="./")
    parser.add_argument('--var', default=None, help="Variable to fit on")
    parser.add_argument('--infile', default=None, help="The input file")
    args = parser.parse_args()

    #If the input file is explicitly specified, just run a single fit on it
    if args.infile:
        fits = [Fit(args.infile.split(".root")[0])]

    #Otherwise do some logic based on the input arguments (channel, path, var)
    else:
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

