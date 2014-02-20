import sys, imp
from glob import glob

infiles = sys.argv[3:]
outfile = sys.argv[2]
signal = 'tchan' #name of signal process/histogram

def is_nominal(hname):
    if '__up' in hname or '__down' in hname:
        return False
    return True

def get_model(infile):
    model = build_model_from_rootfile(
        infile,

        #This enables the Barlow-Beeston procedure
        # http://www.pp.rhul.ac.uk/~cowan/stat/mcml.pdf
        # http://atlas.physics.arizona.edu/~kjohns/teaching/phys586/s06/barlow.pdf
        include_mc_uncertainties = True,
        histogram_filter = is_nominal
    )
    model.fill_histogram_zerobins()
    model.set_signal_processes(signal)

    add_normal_unc(model, "wzjets", mean=1.0, unc=3.0)
    add_normal_unc(model, "ttjets", unc=0.5)
    #add_normal_unc(model, "qcd", unc=0.000001)
    return model

def add_normal_unc(model, par, mean=1.0, unc=1.0):
    model.distribution.set_distribution(
        par, 'gauss', mean = mean,
        width=unc, range=[0.0, float("inf")]
    )
    for o in model.get_observables():
        for p in model.get_processes(o):
            if par != p:
                continue
            print "adding parameters for", o, p
            model.get_coeff(o,p).add_factor('id', parameter=par)

def build_model(infiles):
    model = None
    #infiles = glob("%s/*.root*" % indir)
    for inf in infiles:
        print "loading model from ",inf
        m = get_model(inf)
        if model is None:
            model = m
        else:
            model.combine(m)
    if not model:
        raise Exception("no model was built from infiles=%s" % infiles)
    return model

model = build_model(infiles)

print "processes:", sorted(model.processes)
print "observables:", sorted(model.get_observables())
print "parameters(signal):", sorted(model.get_parameters(["tchan"]))
print "nbins=", [model.get_range_nbins(o)[2] for o in model.get_observables()]
nbins = sum([model.get_range_nbins(o)[2] for o in model.get_observables()])
model_summary(model)

options = Options()
#options.set("minimizer","strategy","robust")
options.set("minimizer","strategy","newton_vanilla")
options.set("global", "debug", "true")

#print "options=", options

result = mle(model, input = 'data', n=1, with_covariance = True, options=options, chi2=True, ks=True)
print "result=", result
fitresults = {}
values = {}
errors = {}
for process in result[signal]:
    if '__' not in process:
        fitresults[process] = result[signal][process][0]
        values[process] = fitresults[process][0]
        errors[process] = fitresults[process][1]

pars = sorted(model.get_parameters([signal]))
n = len(pars)

cov = result[signal]['__cov'][0]

corr = numpy.zeros((n, n), dtype=numpy.float32)
for i in range(n):
   for j in range(n):
       corr[i][j] = cov[i][j] / (errors[pars[i]] * errors[pars[j]])
       # if i==j:
       #     print("diag corr = ", corr[i][j])

report.write_html('report')

out = {
    "names": [p for p in pars],
    "means": [values[p] for p in pars],
    "errors": [errors[p] for p in pars],
    "cov": cov.tolist(),
    "corr": corr.tolist(),
    "chi2": result[signal]["__chi2"],
    "nbins": nbins
}

import json
of = open(outfile, "w")
of.write(json.dumps(out) + "\n")
of.close()
