from sample_style import ColorStyleGen
import ROOT
from utils import get_max_bin
import math
from plots.common.legend import legend
from plots.common.histogram import norm


def plot_hists(hists, name="canv", **kwargs):
    canv = ROOT.TCanvas(name, name)
    draw_cmd = kwargs["draw_cmd"] if "draw_cmd" in kwargs.keys() else "E1"
#    title = kwargs["title"] if "title" in kwargs.keys() else "NOTITLE"
    line_width = kwargs["line_width"] if "line_width" in kwargs.keys() else 2
    x_label = kwargs.get("x_label", "XLABEL")
    y_label = kwargs.get("y_label", "")
    do_log_y = kwargs["do_log_y"] if "do_log_y" in kwargs.keys() else False
    min_bin = kwargs.get("min_bin", 0)
    max_bin = kwargs.get("max_bin", None)
    max_bin_mult = kwargs.get("max_bin_mult", 1.5)
    styles = kwargs.get("styles", {})
    do_chi2 = kwargs.get("do_chi2", False)
    do_ks = kwargs.get("do_ks", False)

    max_bin_val = get_max_bin([hist for hist in hists])

    first = False
    for hist in hists:
        hist.Draw(draw_cmd + (" SAME" if first else ""))
        first = True

#    hists[0].SetTitle(title)
    hists[0].SetStats(False)
    if not max_bin:
        hists[0].SetMaximum(max_bin_mult*max_bin_val)
    else:
        hists[0].SetMaximum(max_bin)

    hists[0].SetMinimum(min_bin)
    hists[0].GetXaxis().SetTitle(x_label)
    hists[0].GetYaxis().SetTitle(y_label)

    if do_chi2:
        for h in hists[1:]:
            chi2 = hists[0].Chi2Test(h, "WW CHI2/NDF")
            h.SetTitle(h.GetTitle() + " #chi^{2}/ndf=%.2f" % chi2)

    if do_ks:
        for h in hists[1:]:
            ks = hists[0].KolmogorovTest(h, "")
            h.SetTitle(h.GetTitle() + " log p=%.1f" % math.log(ks))

    if do_log_y:
        canv.SetLogy()

    return canv

def plot_data_mc_ratio(canv, hist_data, hist_mc, height=0.3):
    """
    Puts the data/MC ratio plot on the TCanvas canv. A new TPad is created at the bottom with the specified height.
    canv - TCanvas
    hist_data  
    returns - (pad, histogram) where pad is the new TPad and histogram is the TH1F ratio histogram
    """
    canv.cd()
    p2 = ROOT.TPad("p2", "p2", 0, 0, 1, height)
    #p2.SetLeftMargin(height / p2.GetWNDC());
    #p2.SetRightMargin(height / p2.GetWNDC());
    p2.SetBottomMargin(height);
    #p2.SetTopMargin(height / 2.0);
    p2.SetTicks(1, 1);
    p2.SetGrid();
    p2.SetFillStyle(0);

    p2.Draw()
    p2.cd()

    hist_ratio = hist_mc.Clone()

    hist_ratio.SetName("ratio")
    hist_ratio.Add(hist_data, -1.0)
    hist_ratio.Divide(hist_data)

    hist_ratio.SetLineColor(ROOT.kBlack)
    hist_ratio.SetMarkerColor(ROOT.kBlack)

    hist_ratio.SetStats(False)
    hist_ratio.SetMarkerStyle(20)
    hist_ratio.SetMarkerSize(0.35)
    hist_ratio.SetMarkerColor(ROOT.kBlue)

    xAxis = hist_ratio.GetXaxis()
    yAxis = hist_ratio.GetYaxis()
    yAxis.CenterTitle()
    yAxis.SetTitle("(exp.-meas.)/meas.")
    yAxis.SetTitleOffset(0.5)
    yAxis.SetTitleSize(0.08)

    xAxis.SetLabelSize(0.08)
    xAxis.SetTitleSize(0.15)
    xAxis.SetTitleOffset(0.5)
    yAxis.SetLabelSize(0.08)

    #xAxis.SetTickLength(xAxis->GetTickLength() * (1. - 2. * margin - bottomSpacing) / bottomSpacing);
    #xAxis.SetNdivisions(histStack.GetXaxis().GetNdivisions());
    yAxis.SetNdivisions(405)

    hist_ratio.Draw("p0e1")

    hist_line = ROOT.TH1F("0line","0line",hist_mc.GetNbinsX(),hist_mc.GetBinLowEdge(1),hist_mc.GetBinLowEdge(hist_mc.GetNbinsX()+1))
    hist_line.Draw("lsame")

    return p2, hist_ratio, hist_line


def plot_hists_dict(hist_dict, setNames=True, **kwargs):
    """
    Draws the contents of a dictionary of hists.
    hist_dict - dict{str, Hist}: a collection of histograms to be drawn.
    setNames - bool: The keys of the dict will be used as titles in the legend. Styling will be done automatically.
    """
    items = hist_dict.items()
    for hn, h in items:
        h.SetName(hn)
        if setNames:
            h.SetTitle(hn)
    hists = [x[1] for x in items]
    names = [x[0] for x in items]
    ColorStyleGen.style_hists(hists)
    canv = plot_hists(hists, **kwargs)

    leg = legend(hists, styles=["f", "f"], **kwargs)
    canv.LEGEND = leg
    return canv
