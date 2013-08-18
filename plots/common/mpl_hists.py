from plots.common.mpl_tdrstyle import plt
from plots.common.hist_plots import hist_err
from rootpy.plotting import Hist

def draw_hists(hists, **kwargs):
    fig = plt.figure(
        figsize=(10,10)
    )
    ax = plt.axes()
    ax.grid(which="both")
    legitems = []
    if isinstance(hists, dict):
        hlist = hists.items()
    elif isinstance(hists, list):
        hlist = [(h.GetTitle(), h) for h in hists]
    
    for hn, h in hlist:
        h = h.Clone()
        #h.Scale(1.0/h.Integral())
        hi = hist_err(ax, h, **kwargs)
        legitems.append(hn)
    
    leg = ax.legend(legitems)
    return ax