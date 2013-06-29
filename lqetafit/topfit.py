signal = 'tchan'

def add_normal_uncertainty(model, u_name, rel_uncertainty, procname, obsname='*'):
    found_match = False
    par_name = u_name
    if par_name not in model.distribution.get_parameters():
        model.distribution.set_distribution(par_name, 'gauss', mean = 1.0, width = rel_uncertainty, range = [0.0, float("inf")])
    else:
        raise RuntimeError, "parameter name already used"
    for o in model.get_observables():
        if obsname != '*' and o!=obsname: continue
        for p in model.get_processes(o):
            if procname != '*' and procname != p: continue
            model.get_coeff(o,p).add_factor('id', parameter = par_name)
            found_match = True
    if not found_match: raise RuntimeError, 'did not find obname, procname = %s, %s' % (obsname, procname)


def get_model():
    #model = build_model_from_rootfile('histos/lqeta.root', include_mc_uncertainties = False)
    # FIXME Using pseudo data
    model = build_model_from_rootfile('histos/pseudo_data.root', include_mc_uncertainties = False)
    model.fill_histogram_zerobins()
    model.set_signal_processes(signal)
    return model

model = get_model()

print sorted(model.processes)

# model uncertainties
#model.add_lognormal_uncertainty('lumi', math.log(1.022), '*')
#model.add_lognormal_uncertainty('ttbar', math.log(1.15), 'ttbar')
#model.add_lognormal_uncertainty('wjets', math.log(2.0), 'wjets')
#model.add_lognormal_uncertainty('wjets', math.log(1.3), 'wjets') # test
#model.add_lognormal_uncertainty('zjets', math.log(1.3), 'zjets')
#model.add_lognormal_uncertainty('QCD', math.log(1.03), 'QCD')

# gaussian uncertainties
#add_normal_uncertainty(model, 'qcd', 0.5, 'qcd')
add_normal_uncertainty(model, 'qcd', 0.1, 'qcd')
add_normal_uncertainty(model, 'top', 0.1, 'top')
#add_normal_uncertainty(model, 'wzjets', inf, 'wzjets')
add_normal_uncertainty(model, 'wzjets', 0.3, 'wzjets')

#
##add_normal_uncertainty(model, 'wjets_heavy', inf, 'wjets_heavy')
##add_normal_uncertainty(model, 'wjets_light', 0.3, 'wjets_light')
#add_normal_uncertainty(model, 'wjets_heavy', inf, 'wjets_light')
#add_normal_uncertainty(model, 'wjets_light', 0.5, 'wjets_light')
#add_normal_uncertainty(model, 'zjets', 0.3, 'zjets')

#print sorted(model.processes)

options = Options()
#options.set("minimizer","strategy","newton_vanilla")
#options.set("minimizer","strategy","tminuit")

# maximum likelihood estimate
# pseudo data
#result = mle(model, input = 'toys-asimov:1.0', n=1, with_covariance = True)
# data
result = mle(model, input = 'data', n=1, with_covariance = True, options=options)

fitresults = {}
for process in result[signal]:
    if '__' not in process:
        fitresults[process] = [result[signal][process][0][0], result[signal][process][0][1]]

# export sorted fit values
f = open('results.txt','w')
for key in sorted(fitresults.keys()):
        line = '%s %f %f\n' % (key, fitresults[key][0], fitresults[key][1])
        print line,
        f.write(line)
f.close()

# covariance matrix
pars = sorted(model.get_parameters(['tchan']))
n = len(pars)
#print pars

cov = result['tchan']['__cov'][0]
#print cov

# write out covariance matrix
import ROOT
ROOT.gStyle.SetOptStat(0)

fcov = ROOT.TFile("cov.root","RECREATE")
canvas = ROOT.TCanvas("c1","Covariance")
h = ROOT.TH2D("covariance","covariance",n,0,n,n,0,n)

for i in range(n):
    h.GetXaxis().SetBinLabel(i+1,pars[i]);
    h.GetYaxis().SetBinLabel(i+1,pars[i]);

for i in range(n):
    for j in range(n):
        h.SetBinContent(i+1,j+1,cov[i][j])

h.Draw("COLZ TEXT")
canvas.Print("cov.png")
canvas.Print("cov.pdf")
h.Write()
fcov.Close()

model_summary(model)
report.write_html('htmlout_fit')
