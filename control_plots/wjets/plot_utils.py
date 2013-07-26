from plots.common.utils import *
from plots.common.stack_plot import *
from plots.common.hist_plots import *
from plots.common.legend import *
from plots.common.cuts import *
from plots.common.histogram import HistCollection, HistMetaData
import copy
from rootpy.extern.progressbar import *
from SingleTopPolarization.Analysis import sample_types
import re
import logging
logger = logging.getLogger("plot_utils")

costheta = {"var":"cos_theta", "varname":"cos #theta", "range":[20,-1,1]}
mtop = {"var":"top_mass", "varname":"M_{bl#nu}", "range":[20, 130, 220]}
mu_pt = {"var":"mu_pt", "varname":"p_{t,#mu}", "range":[20, 30, 220]}
lj_pt = {"var":"pt_lj", "varname":"p_{t,q}", "range":[20, 30, 150]}
bj_pt = {"var":"pt_bj", "varname":"p_{t,b}", "range":[20, 30, 150]}
eta_pos = {"var":"eta_lj", "varname":"#eta_{lq}", "range":[20, 2.5, 5.0]}
eta_neg = {"var":"eta_lj", "varname":"#eta_{lq}", "range":[20, -5.0, -2.5]}
aeta_lj = {"var":"abs(eta_lj)", "varname":"|#eta_{lq}|", "range":[20, 0, 5]}
aeta_lj_2_5 = {"var":"abs(eta_lj)", "varname":"|#eta_{lq}|", "range":[20, 2.5, 5]}


widgets = [Percentage(), ' ', Bar(marker=RotatingMarker()), ' ', ETA()]

def data_mc(var, cut_name, cut, weight, samples, out_dir, recreate, lumi, **kwargs):
    plot_name = "%s__%s" % (var, cut_name)
    plot_name = escape(plot_name)
    systematic = kwargs.get("systematic", "nominal")
    if recreate:
        hists = {}
        metadata = {}
        pbar = ProgressBar(widgets=["Plotting %s:" % plot_name] + widgets, maxval=sum([s.getEventCount() for s in samples])).start()
        nSamp = 1
        for sample in samples:
            hname = sample.name
            if sample.isMC:
                hname_ = sample.name
                hist = sample.drawHistogram(var, str(cut), weight=str(weight), **kwargs)
                hist.Scale(sample.lumiScaleFactor(lumi))
                hists[hname_] = hist
                metadata[hname_] = HistMetaData(
                    sample_name = sample.name,
                    process_name = sample.process_name,
                )
            else:
                hist = sample.drawHistogram(var, str(cut), **kwargs)
                hists[hname] = hist
                metadata[hname] = HistMetaData(
                    sample_name = sample.name,
                    process_name = sample.process_name,
                )
            pbar.update(nSamp)
            nSamp += sample.getEventCount()

        hist_coll = HistCollection(hists, metadata, plot_name)
        hist_coll.save(out_dir)
        logger.debug("saved hist collection %s" % (out_dir))
        pbar.finish()

    hist_coll = HistCollection.load(out_dir + "/%s.root" % plot_name)
    logger.debug("loaded hist collection %s" % (out_dir + "/%s.root" % plot_name))
    return hist_coll

def plot(canv, name, hists_merged, out_dir, desired_order=PhysicsProcess.desired_plot_order,  **kwargs):
    """
    Plots the data/mc stack with the ratio.
    """
    canv.cd()
    p1 = ROOT.TPad("p1", "p1", 0, 0.3, 1, 1)
    p1.Draw()
    p1.SetTicks(1, 1);
    p1.SetGrid();
    p1.SetFillStyle(0);
    p1.cd()
    kwargs["title"] = name + kwargs.get("title", "")
    hists = OrderedDict()
    hists["mc"] = [hists_merged[k] for k in desired_order if k!="data"]
    hists["data"] = [hists_merged["data"]]

    x_title = kwargs.pop("x_label", "")

    logger.debug("Drawing stack")
    stacks = plot_hists_stacked(p1, hists, **kwargs)
    stacks["mc"].GetXaxis().SetLabelOffset(999.)
    stacks["mc"].GetXaxis().SetTitleOffset(999.)

    logger.debug("Drawing ratio")

    tot_mc = get_stack_total_hist(stacks["mc"])
    tot_data = get_stack_total_hist(stacks["data"])
    tot_mc.SetMarkerSize(0)
    tot_mc.fillstyle = "/"
    #tot_mc.SetLineColor(ROOT.kBlue)
    tot_mc.SetFillColor(ROOT.kBlue)

    #Draw the MC statistical error
    tot_mc.Draw("E3 SAME")

    #Draw the systematic error (if present)
    tot_syst_error = kwargs.get("hist_tot_syst_error", None)
    if tot_syst_error:
        tot_syst_error.SetMarkerStyle(21)
        tot_syst_error.SetFillStyle(3005)
        tot_syst_error.SetMarkerColor(ROOT.kMagenta)
        tot_syst_error.SetFillColor(ROOT.kMagenta)
        tot_syst_error.SetLineColor(ROOT.kMagenta)
        tot_syst_error.Draw("LP SAME")

    r = plot_data_mc_ratio(
        canv,
        tot_data,
        tot_mc
    )

    chi2 = tot_data.Chi2Test(tot_mc, "UW CHI2/NDF NORM P")
    ks = tot_mc.KolmogorovTest(tot_data, "N D")
    stacks["mc"].SetTitle(stacks["mc"].GetTitle() + " #chi^{2}/#nu=%.2f" % (chi2))
    r[1].GetXaxis().SetTitle(x_title)
    canv.cd()

    logger.debug("Drawing legend")
    leg = legend(hists["data"] + hists["mc"], styles=["p", "f"], **kwargs)
    #canv.store = [leg, r, tot_mc, tot_data]

    canv.Update()
    canv.SaveAs(out_dir + "/%s.png" % name)
    canv.Close() #Must close canvas to prevent hang in ROOT upon GC
    logger.debug("Returning from plot()")
    return

def plot_hists_dict(hist_dict, doNorm=False, **kwargs):
    items = hist_dict.items()
    for hn, h in items:
        h.SetName(hn)
        h.SetTitle(hn)
    hists = [x[1] for x in items]
    names = [x[0] for x in items]
    if doNorm:
        map(norm, hists)
    ColorStyleGen.style_hists(hists)
    canv = plot_hists(hists, **kwargs)

    leg = legend(hists, styles=["f", "f"], **kwargs)
    canv.LEGEND = leg
    return canv