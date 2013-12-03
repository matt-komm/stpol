import sys, imp
from glob import glob

indir = sys.argv[2]
signal = 'tchan'

def is_nominal(hname):
    if '__up' in hname or '__down' in hname:
        return False
    return True
    
def get_model(infile):
    model = build_model_from_rootfile(
        infile,
        include_mc_uncertainties = True, histogram_filter = is_nominal
    )
    model.fill_histogram_zerobins()
    model.set_signal_processes(signal)

    add_normal_unc(model, "wzjets", mean=1.5, unc=1.0)
    add_normal_unc(model, "ttjets", unc=0.5)
    add_normal_unc(model, "qcd", unc=0.2)
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

def build_model(indir):
    model = None
    infiles = glob("%s/*.root" % indir)
    for inf in infiles:
        print "loading model from ",inf
        m = get_model(inf)
        if model is None:
            model = m
        else:
            model.combine(m)
    return model

model = build_model(indir)

print "processes:", sorted(model.processes)
print "observables:", sorted(model.get_observables())
print "parameters(signal):", sorted(model.get_parameters(["tchan"]))
nbins = sum([model.get_range_nbins(o)[2] for o in model.get_observables()])
model_summary(model)

options = Options()
options.set("minimizer","strategy","robust")
#options.set("minimizer","strategy","newton_vanilla")
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

#print values
#pred = evaluate_prediction(model, values, include_signal = True)
#print pred
# import pandas
# dfs = []

# for obs in pred.keys():
#     print obs
#     for subcomponent in pred[obs].keys():
#         hist = pred[obs][subcomponent]
#         print "  ", subcomponent, pred[obs][subcomponent].get_value_sum()
#         bins, uncs, edges = numpy.array(hist.get_values()), numpy.array(hist.get_uncertainties()), numpy.array(range(1, hist.get_nbins()+1))
#         print bins.size, uncs.size, edges.size
#         df = pandas.DataFrame(numpy.array([bins, uncs, edges]).T, columns=["bins", "errs", "edges"])
#         dfs += [df]

pars = sorted(model.get_parameters([signal]))
n = len(pars)

cov = result[signal]['__cov'][0]

# # write out covariance matrix
# import ROOT
# ROOT.gStyle.SetOptStat(0)

# fcov = ROOT.TFile("corr.root","RECREATE")
# canvas = ROOT.TCanvas("c1","Correlation")
# h = ROOT.TH2D("correlation","Correlation",n,0,n,n,0,n)

# for i in range(n):
#     h.GetXaxis().SetBinLabel(i+1,pars[i]);
#     h.GetYaxis().SetBinLabel(i+1,pars[i]);

corr = numpy.zeros((n, n), dtype=numpy.float32)
for i in range(n):
    for j in range(n):
        corr[i][j] = cov[i][j] / (errors[pars[i]] * errors[pars[j]])
        if i==j:
            print("diag corr = ", corr[i][j])

# h.Draw("COLZ TEXT")
# canvas.Print("plots/corr.png")
# canvas.Print("plots/corr.pdf")
# h.Write()
# fcov.Close()

# write_histograms_to_rootfile(pred, "out.root")
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
of = open("out.txt", "w")
of.write(json.dumps(out) + "\n")
of.close()
