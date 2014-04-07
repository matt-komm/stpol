import sys, imp
from glob import glob

infiles = sys.argv[3:]
outfile = sys.argv[2]
ident = 1

print("outfile=", outfile)
dn = os.path.dirname(outfile)
if not os.path.exists(dn):
    os.makedirs(dn)
print("infiles=", infiles)

signal = 'wjets_light' #name of signal process/histogram

def hfilter(hname):
    if '__up' in hname or '__down' in hname:
        return False

    spl = hname.split("__")

    if len(spl)==2 and spl[1]=="wjets":
        return False

    if "data" in hname:
        return False

    return True

def rename(hn):
    spl = hn.split("__")
    global ident
    spl[0] = str(ident) + "_" + spl[0]
    hn = "__".join(spl)
    hn = hn.replace("wjets__light", "wjets_light")
    hn = hn.replace("wjets__heavy", "wjets_heavy")
    print("renamed to %s"%hn)
    return hn

def get_model(infile):
    model = build_model_from_rootfile(
        infile,
        #This enables the Barlow-Beeston procedure
        # http://www.pp.rhul.ac.uk/~cowan/stat/mcml.pdf
        # http://atlas.physics.arizona.edu/~kjohns/teaching/phys586/s06/barlow.pdf
        include_mc_uncertainties = True,
        histogram_filter = hfilter,
        root_hname_to_convention=rename
    )
    global ident
    ident += 1
    model.fill_histogram_zerobins()
    model.set_signal_processes(signal)

    #add_normal_unc(model, "tchan", unc=0.5)
    #add_normal_unc(model, "wjets_heavy", mean=1.0, unc=3.0)
    #add_normal_unc(model, "ttjets", unc=0.5)
    #add_normal_unc(model, "qcd", unc=0.5)
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
print "parameters(signal):", sorted(model.get_parameters([signal]))
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

for p in sorted(model.processes):
    if p==signal:
        continue

    if p not in values.keys():
        values[p] = 1.0
    if p not in errors.keys():
        errors[p] = 0.0

pars = sorted(model.get_parameters([signal]))
n = len(pars)

cov = result[signal]['__cov'][0]

corr = numpy.zeros((n, n), dtype=numpy.float32)

print("writing covariance file")
covfi = ROOT.TFile(outfile+"_cov.root", "RECREATE")
covmat = ROOT.TH2D("covariance", "covariance", n, 0, n - 1, n, 0, n - 1)
covmat.SetDirectory(covfi)
for i in range(n):
   for j in range(n):
       corr[i][j] = cov[i][j] / (errors[pars[i]] * errors[pars[j]])
       covmat.SetBinContent(i, j, cov[i][j])
       covmat.SetBinError(i, j, 0.0)
       # if i==j:
       #     print("diag corr = ", corr[i][j])
covfi.Write()
covfi.Close()

#report.write_html('report')

out = {
    "names": [p for p in pars],
    "means": [values[p] for p in pars],
    "errors": [errors[p] for p in pars],
    "cov": cov.tolist(),
    "corr": corr.tolist(),
    "chi2": result[signal]["__chi2"],
    "nbins": nbins
}

print("writing json file")
import json
of = open(outfile+".json", "w")
of.write(json.dumps(out) + "\n")
of.close()

print("writing txt file")
of2 = open(outfile+".txt", "w")
for p in sorted(values.keys()):
    of2.write("%s %f %f\n" % (p, values[p], errors[p]))
of2.close()

print("all done!")
