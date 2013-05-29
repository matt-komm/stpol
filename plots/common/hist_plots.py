from sample_style import ColorStyleGen
import ROOT
from utils import get_max_bin

def plot_hists(hists, name="canv", **kwargs):
    canv = ROOT.TCanvas(name, name)
    draw_cmd = kwargs["draw_cmd"] if "draw_cmd" in kwargs.keys() else "E1"
#    title = kwargs["title"] if "title" in kwargs.keys() else "NOTITLE"
    line_width = kwargs["line_width"] if "line_width" in kwargs.keys() else 2
    x_label = kwargs.get("x_label", "XLABEL")
    y_label = kwargs.get("y_label", "events/bin")
    do_log_y = kwargs["do_log_y"] if "do_log_y" in kwargs.keys() else False
    min_bin = kwargs.get("min_bin", 0)
    max_bin_mult = kwargs.get("max_bin_mult", 1.5)
    styles = kwargs.get("styles", {})

    max_bin = get_max_bin([hist for hist in hists])

    first = False
    for hist in hists:
        hist.Draw(draw_cmd + (" SAME" if first else ""))
        first = True

#    hists[0].SetTitle(title)
    hists[0].SetStats(False)
    hists[0].SetMaximum(max_bin_mult*max_bin)
    hists[0].SetMinimum(min_bin)
    hists[0].GetXaxis().SetTitle(x_label)
    hists[0].GetYaxis().SetTitle(y_label)

    if do_log_y:
        canv.SetLogy()

    return canv
