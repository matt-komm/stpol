from plots.common.cuts import Cuts
from SingleTopPolarization.Analysis.tree import is_chan, is_mc
#Which distributions do you want to plot
hdescs = dict()
nbins = 60 #Use 60 since it has many divisors for rebinning
hdescs['all'] = [
    ("cos_theta", "cos_theta", [nbins, -1, 1]),
    ("abs_eta_lj", "abs(eta_lj)", [nbins, 2.5, 5]),
    ("abs_eta_lj_4", "abs(eta_lj)", [nbins, 4, 5]),
    ("top_mass", "top_mass", [nbins, 80, 400]),
    ("top_mass_sr", "top_mass", [nbins, 130, 220]),
    #("eta_lj", "eta_lj", [40, -5, 5]),
]

#Lepton channels need to be separated out
hdescs['mu'] = [
    (Cuts.mva_vars['mu'], Cuts.mva_vars['mu'], [60, -1, 1]),
]
hdescs['ele'] = [
    (Cuts.mva_vars['ele'], Cuts.mva_vars['ele'], [60, -1, 1]),
]

#MC-only variables
hdescs['mc'] = [
    ("true_cos_theta", "true_cos_theta", [60, -1, 1]),
]

#define a LUT for type <-> filtering function
final_plot_lambdas = {
    'mu': lambda x: is_chan(x, 'mu'),
    'ele': lambda x: is_chan(x, 'ele'),
    'mc': lambda x: is_mc(x)
}

def hdesc(name, func, binning):
    hdesc = {
        "name": name,
        "var": func,
        "binning": binning
    }
    return hdesc