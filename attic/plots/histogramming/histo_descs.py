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
    ("C", "C", [nbins, 0, 1]),
    ("met_50_150", "met", [nbins, 50, 150]),
    ("eta_lj", "eta_lj", [nbins, -4.5, 4.5]),
    ("n_jets", "n_jets", [3, 2, 4]),
    ("n_tags", "n_tags", [3, 0, 2]),
    ("abs_eta_lj", "abs(eta_lj)", [nbins, 0, 4.5]),
    ("abs_eta_lj_2_5", "abs(eta_lj)", [nbins, 2.5, 4.5]),
    ("abs_eta_lj_4", "abs(eta_lj)", [nbins, 4, 4.5]),
    ("top_mass", "top_mass", [nbins, 80, 400]),
    ("bj_pt", "pt_bj", [nbins, 0, 300]),
    ("bj_mass", "mass_bj", [nbins, 0, 300]),
    ("top_mass_sr", "top_mass", [nbins, 130, 220]),
    #("eta_lj", "eta_lj", [40, -5, 5]),
]

#Lepton channels need to be separated out
hdescs['mu'] = [
    ("bdt_discr", Cuts.mva_vars['mu'], [nbins, -1, 1]),
    ("bdt_discr_zoom_loose", Cuts.mva_vars['mu'], [nbins, Cuts.mva_wps['bdt']['mu']['loose'], 1]),
    ("lep_iso", 'mu_iso', [nbins, 0, 0.5]),
    ("lep_pt", 'mu_pt', [nbins, 0, 200]),
    ("mtw", "mt_mu", [nbins, 0, 300]),
    ("mtw_50_150", "mt_mu", [nbins, 50, 150]),
]
hdescs['ele'] = [
    ("bdt_discr", Cuts.mva_vars['ele'], [nbins, -1, 1]),
    ("bdt_discr_zoom_loose", Cuts.mva_vars['ele'], [nbins, Cuts.mva_wps['bdt']['ele']['loose'], 1]),
    ("lep_iso", 'el_iso', [nbins, 0, 0.5]),
    ("lep_pt", 'el_pt', [nbins, 0, 200]),
    ("mtw", "mt_el", [nbins, 0, 300]),
    ("mtw_50_150", "mt_el", [nbins, 50, 150]),
]

#MC-only variables
hdescs['mc'] = [
    ("true_cos_theta", "true_cos_theta", [nbins, -1, 1]),
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
