from plots.common.mpl_tdrstyle import plt
from rootpy.plotting import Hist

def draw_hists(hists, **kwargs):
    fig = plt.figure(
        figsize=(10,10)
    )
    ax = plt.axes()

    axes_style(ax)
    if isinstance(hists, dict):
        hlist = hists.items()
    elif isinstance(hists, list):
        hlist = [(h.GetTitle(), h) for h in hists]
    
    for hn, h in hlist:

        #In case of latex name, escape the underscores
        if not hn.startswith "$":
            hn = hn.replace("_", " ")
            
        h = h.Clone()
        hi = hist_err(ax, h, label=hn, **kwargs)

    leg = ax.legend()
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

def ratio_subplots():
    gs = plt.GridSpec(2, 1,
        width_ratios=[1],
        height_ratios=[4,1]
    )
    ax1 = plt.subplot(gs[0])
    ax2 = plt.subplot(gs[1])
    return ax1, ax2

def axes_style(ax):
    ax.grid(True, which='both')
    ax.tick_params(axis='both', which='major', labelsize=16)