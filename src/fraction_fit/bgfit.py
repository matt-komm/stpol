
from glob import glob
import tempfile, shutil, os
import ROOT
import ConfigParser
Config = ConfigParser.ConfigParser(allow_no_value=True)
Config.read(sys.argv[2])

infiles = Config.get("input", "filenames").split(" ")
try:
    prefixes = Config.get("input", "prefixes", []).split(" ")
except ConfigParser.NoOptionError:
    prefixes = []
if len(prefixes)!=len(infiles):
    prefixes = [""]*len(infiles)
outfile = Config.get("output", "filename")

import os
import os.path
dn = os.path.dirname(outfile)
if not os.path.exists(dn):
    os.makedirs(dn)
if not os.path.exists(outfile):
    os.makedirs(outfile)

print("outfile=", outfile)
print("infiles=", infiles)

signal = 'tchan' #name of signal process/histogram

syst = Config.get("systematics", "systematic", "nominal")
direction = Config.get("systematics", "direction", "none")
print "syst=", syst, "dir=", direction

def hfilter(hname):
    if "DEBUG" in hname:
        return False
    spl = hname.split("__")
    #print spl


#    #keep W+jets heavy-light splitting
#    if len(spl)==3 and spl[1] == "wjets":
#        return True

    ##remove combined W+jets
    #if len(spl)==2 and spl[1] == "wjets":
    #    print "remove combined W+jets", spl
    #    return False

    #remove systematic
    if len(spl)!=2:
        #print "remove systematic", spl
        return False


    #remove unmerged data
    if "data_" in hname:
        #print "remove data_", spl
        return False

    #remove systematic
    if '__up' in hname or '__down' in hname:
        #print "remove systematic", spl
        return False

    return True

sr = Config.get("fit", "range", "all")
#def htransform(h):
#    return Histogram(h.get_xmin(), 0.6, h.get_values()[0:24], uncertainties=h.get_uncertainties()[0:24], name=h.get_name())
if sr == "all":
    print "selecting full range"
    def htransform(h):
        return h
elif sr == "sub":
    mx = float(Config.get("fit", "max"))
    mn = float(Config.get("fit", "min"))
    n1 = int(Config.get("fit", "firstbin"))
    n2 = int(Config.get("fit", "lastbin"))
    print "selecting subrange", mn, mx, n1, n2
    def htransform(h):
        return Histogram(mn, mx, h.get_values()[n1:n2], uncertainties=h.get_uncertainties()[n1:n2], name=h.get_name())
def nameconv(n):
    n = n.replace("wjets__heavy", "wjets_heavy")
    n = n.replace("wjets__light", "wjets_light")
    return n

all_hists = []

def get_model(infile, pref):

    (fd, filename) = tempfile.mkstemp()
    filename += "_fit_templates.root"
    #print "temp file", filename
    tf0 = ROOT.TFile.Open(infile, "READ")
    tf = ROOT.TFile.Open(filename, "RECREATE")
    tf.Cd("")

    toskip = []
    kns = [k.GetName() for k in tf0.GetListOfKeys()]

    for k in tf0.GetListOfKeys():
        sys.stdout.flush()
        kn = str(k.GetName())

        if "DEBUG" in kn:
            continue
        #if not hfilter(kn):
        #    continue

        if kn in toskip or "%s__%s__%s"%(kn, syst, direction) in kns:
            continue

        #template is the same systematic scenario we have specified
        #rename the systematic to the nominal
        if (syst != "nominal") and ("%s__%s" % (syst, direction) in kn):
            _kn = "__".join(kn.split("__")[0:2])
            print "renaming", kn, "to", _kn
            toskip.append(_kn)
        else:
            #keep the nominal name
            _kn = kn

        _kn = pref + _kn

        #template passes the histogram filter
        if hfilter(_kn):
            #and is not already present in the output file
            if not tf.Get(_kn):
                x = tf0.Get(kn).Clone(_kn)
                print "cloned", kn, "to", _kn, x.Integral()
                x.SetDirectory(tf)
                x.Write()
            else:
                x = tf.Get(_kn)
                x.Sumw2()
                x1 = x.Integral()
                x.Add(tf0.Get(kn))
                x2 = x.Integral()
                print "added", kn, "to", _kn, x1, x2
                raise Exception("Probably this is an error")
                x.SetDirectory(tf)
                x.Write("", ROOT.TObject.kOverwrite)

    hists = {}
    for h in tf.GetListOfKeys():
        if not hfilter(h.GetName()):
            continue
        hi = h.ReadObj()
        hists[hi.GetName().split("__")[1]] = hi
        print "hist", hi.GetName(), hi.Integral()

    k1 = "ttjets" if "ttjets" in hists.keys() else "other"
    hists["wzjets"].SetMarkerSize(0)
    hists["tchan"].SetMarkerSize(0)
    hists[k1].SetMarkerSize(0)

    hists["wzjets"].SetFillStyle(1001)
    hists["tchan"].SetFillStyle(1001)
    hists[k1].SetFillStyle(1001)

    hists["DATA"].SetLineColor(ROOT.kBlack)
    hists["DATA"].SetMarkerStyle(ROOT.kDot)
    hists["tchan"].SetLineColor(ROOT.kRed)
    hists["wzjets"].SetLineColor(ROOT.kGreen)
    hists[k1].SetLineColor(ROOT.kOrange)
    if "qcd" in hists.keys():
        hists["qcd"].SetLineColor(ROOT.kGray)

    #hists["DATA"].SetFillColor(ROOT.kBlack)
    hists["tchan"].SetFillColor(ROOT.kRed)
    hists["wzjets"].SetFillColor(ROOT.kGreen)
    hists[k1].SetFillColor(ROOT.kOrange)
    if "qcd" in hists.keys():
        hists["qcd"].SetLineColor(ROOT.kGray)
        hists["qcd"].SetFillColor(ROOT.kGray)

    canv = ROOT.TCanvas()
    hists["DATA"].GetXaxis().SetTitle(hists["DATA"].GetName().split("__")[0])
    hists["DATA"].DrawNormalized("E1")
    hists["tchan"].DrawNormalized("E1 SAME")
    hists["wzjets"].DrawNormalized("E1 SAME")
    hists[k1].DrawNormalized("E1 SAME")
    if "qcd" in hists.keys():
        hists["qcd"].DrawNormalized("E1 SAME")
    canv.Print(outfile + "/" + hists["DATA"].GetName() + "_shapes.pdf")

    canv = ROOT.TCanvas()
    hs = ROOT.THStack("stack", "stack")
    if "qcd" in hists.keys():
        hs.Add(hists["qcd"])
    hs.Add(hists["wzjets"])
    hs.Add(hists[k1])
    hs.Add(hists["tchan"])
    hs.Draw("BAR HIST")
    hs.Draw("BAR HIST")
    hists["DATA"].Draw("E1 SAME")
    canv.Print(outfile + "/" + hists["DATA"].GetName() + "_unscaled.pdf")
    tf.Close()

    all_hists.append(filename)

    model = build_model_from_rootfile(
        filename,

        #This enables the Barlow-Beeston procedure
        # http://www.pp.rhul.ac.uk/~cowan/stat/mcml.pdf
        # http://atlas.physics.arizona.edu/~kjohns/teaching/phys586/s06/barlow.pdf
        include_mc_uncertainties = True,
        histogram_filter = hfilter,
        transform_histo = htransform,
        root_hname_to_convention = nameconv,
    )
    #os.remove(filename)
    model.fill_histogram_zerobins()
    model.set_signal_processes(signal)

    for o in model.get_observables():
        for p in model.get_processes(o):
            if p == signal:
                continue
            try:
                add_normal_unc(model,
                    p,
                    mean=float(Config.get("priors", "%s_mean"%p)),
                    unc=float(Config.get("priors", "%s_sigma"%p))
                )
            except:
                print "fixing process ", o, p
    add_normal_unc(model,
        "beta_signal",
        mean=float(Config.get("priors", "signal_mean")),
        unc=float(Config.get("priors", "signal_sigma"))
    )

    return model

def add_normal_unc(model, par, mean=1.0, unc=1.0):
    model.distribution.set_distribution(
        par, 'gauss', mean = mean,
        width=unc, range=[0.0, float("inf")]
    )
    for o in model.get_observables():
        for p in model.get_processes(o):
            print("p=",p)
            if par == p or (par == "beta_signal" and p == "tchan"):
                print "adding parameters for", o, p
                model.get_coeff(o,p).add_factor('id', parameter=par)

def build_model(infiles):
    model = None
    for (inf, pref) in zip(infiles, prefixes):
        print "loading model from ",inf
        m = get_model(inf, pref)
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
options.set("minimizer","strategy","robust")
#options.set("minimizer","strategy","minuit_vanilla")
options.set("global", "debug", "true")

#print "options=", options
dist = "gauss:1.0,0.01"
result = mle(model,
    input = 'data', n=1, with_covariance=True, options=options, chi2=True, ks=True,
#    signal_prior="flat:[0,1.01]"
    signal_prior=dist
)
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
outpars = copy.copy(pars)

for p in ["qcd"]:
    outpars.append("qcd")
    if p not in values.keys():
        values[p] = 1.0
    if p not in errors.keys():
        errors[p] = 0.0

for fn in all_hists:

    tf = ROOT.TFile(fn)

    hists = {}
    for h in tf.GetListOfKeys():
        if not hfilter(h.GetName()):
            continue
        hi = h.ReadObj()
        hists[hi.GetName().split("__")[1]] = hi
        print "hist", hi.GetName(), hi.Integral()
    hn = hists["DATA"].GetName()
    canv = ROOT.TCanvas()

    k1 = "ttjets" if "ttjets" in hists.keys() else "other"
    hists["DATA"].SetMarkerStyle(ROOT.kDot)

    hists["DATA"].SetLineColor(ROOT.kBlack)
    hists["tchan"].SetLineColor(ROOT.kRed)
    hists["wzjets"].SetLineColor(ROOT.kGreen)
    hists[k1].SetLineColor(ROOT.kOrange)
    if "qcd" in hists.keys():
        hists["qcd"].SetLineColor(ROOT.kGray)

    #hists["DATA"].SetFillColor(ROOT.kBlack)
    hists["tchan"].SetFillColor(ROOT.kRed)
    hists["wzjets"].SetFillColor(ROOT.kGreen)
    hists[k1].SetFillColor(ROOT.kOrange)
    if "qcd" in hists.keys():
        hists["qcd"].SetFillColor(ROOT.kGray)

    hs = ROOT.THStack("stack", "stack")

    if "qcd" in hists.keys():
        hists["qcd"].Scale(values["qcd"])
    hists[k1].Scale(values[k1])
    hists["wzjets"].Scale(values["wzjets"])
    hists["tchan"].Scale(values["beta_signal"])

    if "qcd" in hists.keys():
        hs.Add(hists["qcd"])
    hs.Add(hists["wzjets"])
    hs.Add(hists[k1])
    hs.Add(hists["tchan"])
    hs.Draw("BAR HIST")
    hists["DATA"].Draw("E1 SAME")
    canv.Print(outfile + "/" + hn + "_scaled.pdf")

print("pars:", pars)
print("outpars:", outpars)
n = len(outpars)

cov = result[signal]['__cov'][0]

corr = numpy.zeros((n, n), dtype=numpy.float32)


print("writing covariance file")
covfi = ROOT.TFile(outfile+"_cov.root", "RECREATE")
covmat = ROOT.TH2D("covariance", "covariance", n, 0, n - 1, n, 0, n - 1)
covmat.SetDirectory(covfi)
for i in range(n):
    covmat.GetXaxis().SetBinLabel(i+1, outpars[i])
    for j in range(n):
        covmat.GetYaxis().SetBinLabel(j+1, outpars[j])
        try:
            ci = pars.index(outpars[i])
            cj = pars.index(outpars[j])
            corr[i][j] = cov[ci][cj] / (errors[outpars[i]] * errors[outpars[j]])
            covmat.SetBinContent(i + 1, j + 1, cov[ci][cj])
        except Exception as err:
            corr[i][j] = 0#1.0 / (errors[outpars[i]] * errors[outpars[j]])
            covmat.SetBinContent(i + 1, j + 1, 1.0)

        covmat.SetBinError(i, j, 0.0)
covfi.Write()
covfi.Close()

out = {
    "names": [p for p in outpars],
    "means": [values[p] for p in outpars],
    "errors": [errors[p] for p in outpars],
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
    print("%s %f %f" % (p, values[p], errors[p]))
    of2.write("%s %f %f\n" % (p, values[p], errors[p]))
of2.close()

print("all done!")
