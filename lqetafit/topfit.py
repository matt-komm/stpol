signal = 'tchan'

def histofilter(s):
    #if '__plus' in s or '__minus' in s:
    if '__up' in s or '__down' in s:
        return False
    return True

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
    model = build_model_from_rootfile('../final_fit/histos/mu__mva_BDT_with_top_mass_eta_lj_C_mu_pt_mt_mu_met_mass_bj_pt_bj_mass_lj__no_metphi.root', include_mc_uncertainties = True, histogram_filter = histofilter)
    #model = build_model_from_rootfile('histos/no_metphi/mu__mva_BDT_with_top_mass_eta_lj_C_mu_pt_mt_mu_met_mass_bj_pt_bj_mass_lj__comphep.root', include_mc_uncertainties = False, histogram_filter = histofilter)
    #model = build_model_from_rootfile('histos/no_metphi/ele__mva_BDT_with_top_mass_C_eta_lj_el_pt_mt_el_pt_bj_mass_bj_met_mass_lj.root', include_mc_uncertainties = False, histogram_filter = histofilter)
    #model = build_model_from_rootfile('histos/no_metphi/ele__mva_BDT_with_top_mass_C_eta_lj_el_pt_mt_el_pt_bj_mass_bj_met_mass_lj__comphep.root', include_mc_uncertainties = False, histogram_filter = histofilter)
    model.fill_histogram_zerobins()
    model.set_signal_processes(signal)
    return model

model = get_model()

print sorted(model.processes)

# model uncertainties
execfile('uncertainties.py')

options = Options()
options.set("minimizer","strategy","newton_vanilla")
#options.set("minimizer","strategy","tminuit")

# maximum likelihood estimate
# FIXME pseudo data
#result = mle(model, input = 'toys-asimov:1.0', n=1, with_covariance = True, options=options)
# data
result = mle(model, input = 'data', n=1, with_covariance = True, options=options)

fitresults = {}
for process in result[signal]:
    if '__' not in process:
        fitresults[process] = [result[signal][process][0][0], result[signal][process][0][1]]

# export sorted fit values
f = open('results/nominal.txt','w')
for key in sorted(fitresults.keys()):
        line = '%s %f %f\n' % (key, fitresults[key][0], fitresults[key][1])
        print line,
        f.write(line)
f.close()

# covariance matrix
pars = sorted(model.get_parameters([signal]))
n = len(pars)
#print pars

cov = result[signal]['__cov'][0]

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
canvas.Print("plots/cov.png")
canvas.Print("plots/cov.pdf")
h.Write()
fcov.Close()

model_summary(model)
report.write_html('htmlout_fit')
