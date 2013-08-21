import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

from plots.common.cuts import Cuts
from tree import is_chan, is_mc


#Which distributions do you want to plot
hdescs = dict()
nbins = 60 #Use 60 since it has many divisors for rebinning
hdescs['all'] = [
    ("cos_theta", "cos_theta", [nbins, -1, 1]),
    ("met", "met", [nbins, 0, 300]),
    ("met_50_150", "met", [nbins, 50, 150]),
    ("abs_eta_lj", "abs(eta_lj)", [nbins, 2.5, 5]),
    ("abs_eta_lj_4", "abs(eta_lj)", [nbins, 4, 5]),
    ("top_mass", "top_mass", [nbins, 80, 400]),
    ("top_mass_sr", "top_mass", [nbins, 130, 220]),
    #("eta_lj", "eta_lj", [40, -5, 5]),
]

#Lepton channels need to be separated out
hdescs['mu'] = [
    (Cuts.mva_vars['mu'], Cuts.mva_vars['mu'], [60, -1, 1]),
    ("mtw", "mt_mu", [nbins, 0, 300]),
    ("mtw_50_150", "mt_mu", [nbins, 50, 150]),
]
hdescs['ele'] = [
    (Cuts.mva_vars['ele'], Cuts.mva_vars['ele'], [60, -1, 1]),
    ("mtw", "mt_el", [nbins, 0, 300]),
    ("mtw_50_150", "mt_el", [nbins, 50, 150]),
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

def create_plots(graph, plot_nodes, filter_funcs=[]):
    from weights import reweight, syst_weights
    from tree import HistNode    
    #Add all the nodes for the final plots with all the possible reweighting combinations
    final_plots = dict()
    for t, descs in hdescs.items():
        for name, func, binning in descs:
            skip = False
            for f in filter_funcs:
                if f(name):
                    logger.info("Not creating a plot for %s" % name)
                    skip=True
                    break
            if skip:
                continue
            hd = hdesc(name, func, binning)

            #Make only the required plots per channel
            lambdas = []
            if t in final_plot_lambdas.keys():
                lambdas.append(final_plot_lambdas[t])

            final_plots[name] = HistNode(
                hd,
                graph, name, plot_nodes, [], filter_funcs=lambdas
            )
            final_plots[name] = reweight(
                final_plots[name],
                syst_weights(graph)
            )
    return final_plots