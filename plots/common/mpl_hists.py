from plots.common.mpl_tdrstyle import plt
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

def hist_err(axes, hist, yerr=None, **kwargs):
    """
    Plots a Histogram on matplotlib Axes in familiar ROOT style with errorbars.

    Args:
        axes: a matplotlib axes instance
        hist: a Hist instance
    Returns:
        The errorbar plot.
    """

    if not yerr:
        yerr = [list(hist.yerrh()), list(hist.yerrl())]
    return axes.errorbar(
        list(hist.x()),
        list(hist.y()),
        yerr=yerr,
        drawstyle='steps-mid', **kwargs
    )

def ipy_show_canv(c):
    from IPython.core.display import Image

    fn = "temp.png"
    c.SaveAs(fn) 
    return Image(filename=fn) 