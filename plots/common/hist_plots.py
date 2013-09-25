from sample_style import ColorStyleGen
import ROOT
from utils import get_max_bin
import math
from plots.common.legend import legend
from plots.common.histogram import norm
import logging
logger = logging.getLogger("hist_plots")
logger.setLevel(logging.WARNING)

from plots.common.mpl_hists import hist_err, ipy_show_canv

def plot_hists(hists, **kwargs):
    """
    Draws a list of histograms side-by-side on a new canvas.

    Args:
        hists - a list of Hist instances to draw

    Keywords:
        name: the name of the canvas to create.
        draw_cmd: the ROOT draw command. Can be a single command
            (use the same for all) or a list with the length of hists
        x_label: a string with the title for the x axis.
        y_label: ditto for the y axis.
        do_log_y: a boolean to specify if the y axis should be logarithmic.
        min_bin: a numerical value for the lower range of the y axis.
        max_bin: ditto for the upper range. Overrides the max_bin_mult variable.
        max_bin_mult: a multiplier for the y axis, applied on the maximal bin
            height.
        do_chi2: a boolean to specify whether to do the Chi2 test between
            the first and subsequent histograms.
        do_ks: ditto for the KS test.

    Returns:
        a handle to the new canvas.
    Raises:
        ValueError: when the number of draw commands did not equal the number
            of hists
    """

    canv = kwargs.get("canvas", ROOT.TCanvas())
    canv.cd()
    draw_cmd = kwargs["draw_cmd"] if "draw_cmd" in kwargs.keys() else "E1"
    x_label = kwargs.get("x_label", "XLABEL")
    y_label = kwargs.get("y_label", "")
    do_log_y = kwargs["do_log_y"] if "do_log_y" in kwargs.keys() else False
    min_bin = kwargs.get("min_bin", 0)
    max_bin = kwargs.get("max_bin", None)
    max_bin_mult = kwargs.get("max_bin_mult", 1.5)
    do_chi2 = kwargs.get("do_chi2", False)
    do_ks = kwargs.get("do_ks", False)

    max_bin_val = get_max_bin([hist for hist in hists])

    if isinstance(draw_cmd, basestring):
        draw_cmd = [draw_cmd]*len(hists)
    if len(draw_cmd) != len(hists):
        raise ValueError("Must have the same number of draw commands as hists: %s vs %s" % (str(draw_cmd), str(hists)))
    first = False
    for dc, hist in zip(draw_cmd, hists):
        hist.Draw(dc + (" SAME" if first else ""))
        first = True

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
            h.SetTitle(h.GetTitle() + " #chi^{2}/ndf=%.1f" % chi2)

    if do_ks:
        for h in hists[1:]:
            ks = hists[0].KolmogorovTest(h, "")
            h.SetTitle(h.GetTitle() + " log p=%.1f" % math.log(ks))

    if do_log_y:
        canv.SetLogy()

    return canv

def subpad(canv, low=0.3):
    """
    Makes a new subpad on a TCanvas in the upper region.

    Args:
        canv: the parent canvas or pad instance.
        low: a floating point fraction for the area to cut off in the lower part.

    Returns:
        a handle to the new TPad.
    """
    #Make a separate pad for the stack plot
    canv.cd()
    p1 = ROOT.TPad("p1", "p1", 0, low, 1, 1)
    p1.Draw()
    p1.SetTicks(1, 1);
    p1.SetGrid();
    p1.SetFillStyle(0);
    p1.cd()
    return p1

def plot_data_mc_ratio(canv, hist_data, hist_mc, **kwargs):
    """
    Puts the data/MC ratio plot on the TCanvas canv. A new TPad is created at
    the bottom with the specified height.

    Args:
        canv: a TCanvas instance on which to draw the ratio plot. A subpad will
            be created on this canvas.
        hist_data: A Hist instance with the data.
        hist_mc: A Hist instance with the MC.

    Keywords:
        height: the floating value fraction of the height of the new pad
        syst_hists: a 2-tuple (syst_up, syst_down) with Hist instances to
            draw as the systematic error band.
        min_max: a 2-tuple specifying the (low, up) with the minimum
            and maximum of the y axis of the ratio plot

    Returns:
        A tuple with (pad, histogram) where pad is the new TPad and histogram is
        the TH1F ratio histogram that were created.

    Raises:
        ValueError: when the format of the supplied systematic histograms was
            not a 2-tuple.
    """
    canv.cd()

    height = kwargs.get("height", 0.3)
    syst_hists = kwargs.get("syst_hists", None)
    min_max = kwargs.get("min_max", 2.0)
    syst_fill = kwargs.get("syst_fill", 0)

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
    hdata_orig = hist_data.Clone()

    # (MC-data) / data
    hist_ratio.SetName("ratio")
    hist_ratio.Add(hist_data, -1.0)
    hist_ratio.Divide(hist_data)

    #If the measured data was 0, then set the bin error to the maximal value
    #and content to 0
    for i in range(hist_ratio.nbins()):
        if hist_data[i] == 0:
            hist_ratio.SetBinError(i+1,
                min_max if isinstance(min_max, float) else 2.0
            )
            hist_ratio.SetBinContent(i+1, 0)


    hist_ratio.SetLineColor(ROOT.kBlack)

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

    #Draw the ratio histogram with default (statistical error bars) to get the correct axis
    #This histogram will not be visible in the end
    hist_ratio.Draw("p0e1")

    if isinstance(min_max, float):
        _minmax = min_max*max(map(lambda x: abs(x),
                [hist_ratio.GetMinimum(), hist_ratio.GetMaximum()]
            )
        )
        hist_ratio.SetMinimum(-_minmax)
        hist_ratio.SetMaximum(_minmax)
    else:
        hist_ratio.SetMinimum(min(min_max))
        hist_ratio.SetMaximum(max(min_max))
    #logger.debug(list(hist_ratio.y()))

    hist_line = ROOT.TH1F("0line","0line",hist_mc.GetNbinsX(),hist_mc.GetBinLowEdge(1),hist_mc.GetBinLowEdge(hist_mc.GetNbinsX()+1))
    hist_line.Draw("lsame")
    canv.hist_line = hist_line

    #Calculate the down/up variation ratios
    if syst_hists:
        logger.info("Drawing systematic histograms")
        syst_ratio_hists = []
        if len(syst_hists) != 2:
            raise Exception("Must specify the systematic histograms as a 2-tuple (down, up), got %s" % str(syst_hists))
        for h in list(syst_hists):
            hr = h.Clone()
            hr.Add(hdata_orig, -1)
            hr.Divide(hdata_orig)
            #Draw them as gray lines
            hr.Draw("same hist")
            logger.debug("systematic ratio = %s" % str(list(hr.y())))
            syst_ratio_hists.append(hr)

        canv.syst_ratio_hists = syst_ratio_hists
        # canv.ratio_graph = ratio_graph

    return p2, hist_ratio


def plot_hists_dict(hist_dict, setNames=True, **kwargs):
    """
    Draws the contents of a dictionary of hists. Styling will be done
    automatically. Any additional kwargs are passed to the plot_hists and legend
    methods.

    Args:
        hist_dict: a str, Hist dictionary of the histograms to be drawn.

    Keywords:
        setNames: a bool to specify whether the keys of the dict will be used as
            titles in the legend.

    Returns: a handle to the new canvas
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

if __name__=="__main__":
    logger.setLevel(logging.DEBUG)
    ROOT.gROOT.SetBatch(True)
    ROOT.TH1F.SetDefaultSumw2()
    from plots.common.tdrstyle import tdrstyle
    tdrstyle()
    from rootpy.plotting import Hist
    import numpy.random as nr

    hdata = Hist(20, -1, 1, name="mc")
    hmc = Hist(20, -1, 1, name="data")

    for i in range(10000):
        hdata.Fill(nr.normal(0, 1))
    for i in range(100000):
        hmc.Fill(nr.normal(0.05, 1))
    hmc.Scale(1.05 * hdata.Integral()/ hmc.Integral())

    c = ROOT.TCanvas("c1")

    p1 = subpad(c)

    from plots.common.sample_style import Styling
    Styling.mc_style(hmc, "T_t")
    Styling.data_style(hdata)
    hmc.Draw("hist")
    hdata.Draw("e1 same")

    hsyst_up = hmc.Clone()
    hsyst_up.Scale(1.02)

    #FIXME: do random smearing
    for i in range(1, hsyst_up.nbins()):
        pass
    hsyst_down = hmc.Clone()
    hsyst_down.Scale(0.98)

    p2, hist_ratio = plot_data_mc_ratio(c, hmc, hdata, syst_hists=(hsyst_up, hsyst_down))
    #c.Update()
    #c.Show()
    c.SaveAs("hist_plots_test1.png")
