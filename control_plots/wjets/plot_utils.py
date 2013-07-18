from plots.common.utils import *
from plots.common.histogram import *
from plots.common.stack_plot import *
from plots.common.hist_plots import *
from plots.common.legend import *
from plots.common.cuts import *
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
            weight_ = weight
            if sample.isMC:

                #Apply sherpa gen-level weight
                if "sherpa" in sample.name:
                    logger.debug("WJets sherpa sample, enabling sherpa weights")
                    weight_ *= Weights.sherpa_weight*Weights.sherpa_flavour_weight

                weight_strs = [("weight__nominal", str(weight_))]

                cut_strs = [("cut__all", str(cut))]
                if kwargs.get("flavour_split", False) and sample_types.is_wjets(sample.name):
                    cut_strs += [
                        ("cut__flavour__W_HH", str(cut*Cuts.W_HH)),
                        ("cut__flavour__W_Hl", str(cut*Cuts.W_Hl)),
                        ("cut__flavour__W_ll", str(cut*Cuts.W_ll)),
                    ]

                #Reweigh madgraph samples
                if kwargs.get("reweight_madgraph", False) and re.match("W[0-9]Jets_exclusive", sample.name):
                    sample.tree.AddFriend("trees/WJets_weights", sample.file_name)
                    logger.debug("WJets madgraph sample, enabling flavour weight")
                    avg_weight = sample.drawHistogram(
                        str(Weights.wjets_madgraph_shape_weight(systematic)),
                        str(cut), weight_str=str(weight_), plot_range=[100, 0, 2]
                    ).hist.GetMean()

                    logger.debug("average weight = %.2f" % avg_weight)
                    reweighted_sample_weight_str = str(weight_*Weights.wjets_madgraph_flat_weight(systematic) * Weights.wjets_madgraph_shape_weight(systematic) * Weight(str(1.0/avg_weight)))
                    logger.debug("weight=%s" % reweighted_sample_weight_str)
                    weight_strs += [("weight__reweight_madgraph", reweighted_sample_weight_str)]    

                for weight_name, weight_str in weight_strs:
                    for cut_name, cut_str in cut_strs:
                        logger.debug("Drawing with %s, %s" % (weight_str, cut_str))
                        hname_ = weight_name + "/" + cut_name + "/" + hname
                        hist = sample.drawHistogram(var, cut_str, weight_=weight_str, **kwargs)
                        hist.hist.Scale(sample.lumiScaleFactor(lumi))
                        hists[hname_] = hist.hist
                        metadata[hname_] = HistMetaData(
                            sample_name = sample.name,
                            process_name = sample.process_name,
                        )
            else:
                hist = sample.drawHistogram(var, str(cut), **kwargs)
                hists[hname] = hist.hist
                metadata[hname] = HistMetaData(
                    sample_name = sample.name,
                    process_name = sample.process_name,
                )
            pbar.update(nSamp)
            nSamp += sample.getEventCount()
            #metadata[sample.name] = HistMetaData()

        hist_coll = HistCollection(hists, metadata, plot_name)
        hist_coll.save(out_dir)
        logger.debug("saved hist collection %s" % (out_dir))
        pbar.finish()

    hist_coll = HistCollection.load(out_dir + "/%s.root" % plot_name)
    logger.debug("loaded hist collection %s" % (out_dir + "/%s.root" % plot_name))
    return hist_coll

    # merges = copy.deepcopy(merge_cmds)
    # merged = merge_hists(hists)
    # canv = ROOT.TCanvas()
    # plot(canv, plot_name, merged, out_dir)
    # canv.Update()
    # canv.SaveAs(out_dir + "/%s.png" % plot_name)

def plot(canv, name, hists_merged, out_dir, **kwargs):
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
    hists["mc"] = [v for (k,v) in hists_merged.items() if k!="data"]
    hists["data"] = [hists_merged["data"]]

    x_title = kwargs.pop("x_label", "")

    logger.debug("Drawing stack")
    stacks = plot_hists_stacked(p1, hists, **kwargs)
    stacks["mc"].GetXaxis().SetLabelOffset(999.)
    stacks["mc"].GetXaxis().SetTitleOffset(999.)

    logger.debug("Drawing ratio")

    tot_mc = get_stack_total_hist(stacks["mc"])
    tot_data = get_stack_total_hist(stacks["data"])
    r = plot_data_mc_ratio(
        canv,
        tot_data,
        tot_mc
    )

    chi2 = tot_data.Chi2Test(tot_mc, "UW CHI2/NDF NORM P")
    ks = tot_mc.KolmogorovTest(tot_data, "N D")
    stacks["mc"].SetTitle(stacks["mc"].GetTitle() + " #chi^{2}/N=%.2f ks=%.2E" % (chi2, ks))
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