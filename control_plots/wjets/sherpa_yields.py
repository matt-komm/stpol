import ROOT
ROOT.gROOT.SetBatch(True)
from plots.common.sample import Sample, load_samples, get_process_name
from plots.common.sample_style import Styling, ColorStyleGen
from plots.common.utils import merge_hists, mkdir_p, get_stack_total_hist
from plots.common.odict import OrderedDict
from plots.common.stack_plot import plot_hists_stacked
from plots.common.cuts import Cuts, Cut, Weights, flavour_scenarios
from plots.common.cross_sections import xs as cross_sections
from plots.common.legend import legend
from plots.common.tdrstyle import tdrstyle
from plots.common.hist_plots import plot_hists, plot_data_mc_ratio
from SingleTopPolarization.Analysis import sample_types
import plots.common.utils
import copy
import os
import re
import logging
logger = logging.getLogger("sherpa_yields")
import pickle
import math
import shutil
import sys
from plots.common.histogram import HistCollection, HistMetaData
from plots.common.utils import escape, filter_hists
import rootpy
import rootpy.io
from rootpy.io.file import File
import numpy

costheta = {"var":"cos_theta", "varname":"cos #theta", "range":[20,-1,1]}
mtop = {"var":"top_mass", "varname":"M_{bl#nu}", "range":[20, 130, 220]}
mu_pt = {"var":"mu_pt", "varname":"p_{t,#mu}", "range":[20, 30, 220]}
lj_pt = {"var":"pt_lj", "varname":"p_{t,q}", "range":[20, 30, 150]}
bj_pt = {"var":"pt_bj", "varname":"p_{t,b}", "range":[20, 30, 150]}
eta_pos = {"var":"eta_lj", "varname":"#eta_{lq}", "range":[20, 2.5, 5.0]}
eta_neg = {"var":"eta_lj", "varname":"#eta_{lq}", "range":[20, -5.0, -2.5]}
aeta_lj = {"var":"abs(eta_lj)", "varname":"|#eta_{lq}|", "range":[20, 0, 5]}
aeta_lj_2_5 = {"var":"abs(eta_lj)", "varname":"|#eta_{lq}|", "range":[20, 2.5, 5]}
LUMI_TOTAL = 19739

def draw_data_mc(var, plot_range, cut_str, weight_str, lumi, samples, out_dir, collection_name=None, systematic="nominal", reweigh=True):
    hists = dict()
    metadata = dict()
    for name, sample in samples.items():

        md = HistMetaData(
            sample_name=sample.name,
            sample_process_name=sample.process_name,
        )

        if sample.isMC:
            sample_weight_str = weight_str
            weight_strs = []
            weight_strs += [("unweighted", sample_weight_str)]

            if reweigh and re.match("W[0-9]Jets_exclusive", sample.name):
                sample.tree.AddFriend("trees/WJets_weights", sample.file_name)
                logger.debug("WJets madgraph sample, enabling flavour weight")
                avg_weight = sample.drawHistogram( str(Weights.wjets_madgraph_weight(systematic)), cut_str, weight_str=weight_str, plot_range=[100, 0, 2]).hist.GetMean()
                #avg_weight = 1.0
                md.average_weight = avg_weight
                logger.debug("average weight = %.2f" % avg_weight)
                reweighted_sample_weight_str = weight_str + "*" + str(Weights.wjets_madgraph_weight(systematic))# + "*" + (str(1.0/avg_weight))
                logger.debug("weight=%s" % reweighted_sample_weight_str)
                weight_strs += [("weighted", reweighted_sample_weight_str)]

            hn = "mc/iso/%s" % sample.name

            if sample_types.is_wjets(sample.name):
                logger.debug("Sample %s: enabling hf/lf separation" % (sample.name))

                for wn, w in weight_strs:
                    logger.info("Weight strategy %s, weights str=%s" % (wn, w))
                    suffix = "_%s" % wn
                    hist_hf = sample.drawHistogram(var, cut_str+"&&(wjets_flavour_classification>=0 && wjets_flavour_classification<4)", weight=w, plot_range=plot_range)
                    hist_lf = sample.drawHistogram(var, cut_str+"&&(wjets_flavour_classification>=4)", weight=w, plot_range=plot_range)
                    metadata[hn + "_hf" + suffix] = md
                    metadata[hn + "_lf" + suffix] = md
                    hist_hf.hist.Scale(sample.lumiScaleFactor(lumi))
                    hist_lf.hist.Scale(sample.lumiScaleFactor(lumi))
                    hists[hn + "_hf" + suffix] = hist_hf.hist
                    hists[hn + "_lf" + suffix] = hist_lf.hist

            hist = sample.drawHistogram(var, cut_str, weight=sample_weight_str, plot_range=plot_range)
            hist.hist.Scale(sample.lumiScaleFactor(lumi))
            hist = hist.hist
        elif name == "iso/SingleMu":
            hist = sample.drawHistogram(var, cut_str, weight="1.0", plot_range=plot_range).hist
            Styling.data_style(hist)
            hn = "data/iso/%s" % sample.name
        elif name == "antiiso/SingleMu":
            hist = sample.drawHistogram(var, cut_str, weight="1.0", plot_range=plot_range).hist
            hn = "data/antiiso/%s" % sample.name
        sys.stdout.write(".")
        sys.stdout.flush()
        metadata[hn] = md
        hists[hn] = hist

    if not collection_name:
        collection_name = "%s" % var
        collection_name = escape(collection_name)
    hc = HistCollection(hists, metadata, collection_name)
    hc.save(out_dir)
    sys.stdout.write("\n")
    logger.info("Saved histogram collection to %s/%s.root" % (out_dir, collection_name))

    return hc

def plot(canv, name, hists_merged, out_dir, **kwargs):
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
    stacks = plot_hists_stacked(canv, hists, **kwargs)
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

    chi2 = tot_data.Chi2Test(tot_mc, "UW CHI2/NDF")
    ks = tot_data.KolmogorovTest(tot_mc, "")
    stacks["mc"].SetTitle(stacks["mc"].GetTitle() + "__#chi^{2}/N=%.2f__ks=%.2E" % (chi2, ks))
    r[1].GetXaxis().SetTitle(x_title)
    canv.cd()

    logger.debug("Drawing legend")
    leg = legend(hists["data"] + hists["mc"], styles=["p", "f"], **kwargs)

    canv.Update()
    canv.SaveAs(out_dir + "/%s.png" % name)
    canv.Close() #Must close canvas to prevent hang in ROOT upon GC
    logger.debug("Returning from plot()")
    return

def reweigh_madgraph_hists(h_heavy, h_light, syst="nominal"):

    #Determined from 2J0T data/madgraph
    sf_Wlight = 1.21990650
    err_sf_Wlight = 1.0-1.21990650

    if syst=="nominal":
        h_light.Scale(sf_Wlight)
        h_heavy.Scale(1.0)
    elif syst=="WJets_up":
        h_light.Scale(sf_Wlight + err_sf_Wlight)
        h_heavy.Scale(2.0)
    elif syst=="WJets_down":
        h_light.Scale(sf_Wlight - err_sf_Wlight)
        h_heavy.Scale(0.5)
    else:
        return ValueError("syst must be nominal, WJets_up, WJets_down: syst=%" % syst)

def plot_sherpa_vs_madgraph(var, cut_name, cut_str, samples, out_dir, recreate=False, **kwargs):
    out_dir = out_dir + "/" + cut_name
    if recreate and os.path.exists(out_dir):
        logger.info("Output directory %s exists, removing" % out_dir)
        shutil.rmtree(out_dir)
    mkdir_p(out_dir)

    logger.info("Using output directory %s" % out_dir)

    hname = escape(var["var"])
    if recreate:
        logger.info("Drawing histograms for variable=%s, cut=%s" % (var["var"], cut_name))
        hists = draw_data_mc(
            var["var"], var["range"],
            cut_str,
            "pu_weight*muon_IDWeight*muon_TriggerWeight*muon_IsoWeight*b_weight_nominal", LUMI_TOTAL, samples, out_dir,
            collection_name=hname,
            systematic=kwargs.get("systematic", "nominal")
        )


    try:
        hist_coll = HistCollection.load(out_dir + "/%s.root" % hname)
    except rootpy.ROOTError as e:
        logging.error("Couldn't open the histogram collection: %s. Try running with --recreate" % str(e))
        sys.exit(1)

    for hn, hist in hist_coll.hists.items():
        hn = hn.split("/")[-1]
        try:
            if sample_types.is_mc(hn):
                Styling.mc_style(hist, hn)
            else:
                Styling.data_style(hist)
        except KeyError as e:
            logger.warning("Couldn't style histogram %s" % hn)
        match = re.match("(.*)_([hl]f)_.*", hn)
        if match:
            logger.debug("Matched flavour split histogram %s" % hn)
            Styling.mc_style(hist, match.group(1))
            if match.group(2)=="hf":
                hist.SetFillColor(hist.GetFillColor()+1)

    logger.debug("Loaded hists: %s" % str(hist_coll.hists))

    #Combine data and mc hists to one dict
    hjoined = dict(
        filter_hists(hist_coll.hists, "mc/iso/(.*)"),
        **filter_hists(hist_coll.hists, "data/iso/(SingleMu)")
    )

    merges = dict()

    merge_cmds = plots.common.utils.merge_cmds.copy()
    merge_cmds.pop("WJets")
    merges["madgraph/unweighted"] = merge_cmds.copy()
    merges["madgraph/weighted"] = merge_cmds.copy()
    merges["sherpa"] = merge_cmds.copy()


    merges["sherpa"]["WJets_hf"] = ["WJets_sherpa_nominal_hf_unweighted"]
    merges["sherpa"]["WJets_lf"] = ["WJets_sherpa_nominal_lf_unweighted"]
    merges["madgraph/unweighted"]["WJets_hf"] = ["W[0-9]Jets_exclusive_hf_unweighted"]
    merges["madgraph/unweighted"]["WJets_lf"] = ["W[0-9]Jets_exclusive_lf_unweighted"]
    merges["madgraph/weighted"]["WJets_hf"] = ["W[0-9]Jets_exclusive_hf_weighted"]
    merges["madgraph/weighted"]["WJets_lf"] = ["W[0-9]Jets_exclusive_lf_weighted"]

    hmerged = dict()
    for k in merges.keys():
        hmerged[k] = merge_hists(hjoined, merges[k])

    logger.info("Drawing madgraph unweighted plot")
    canv = ROOT.TCanvas("c2", "c2")
    suffix = "__%s__%s" % (var["var"], cut_name)
    suffix = escape(suffix)

    plot(canv, "madgraph_unweighted"+suffix, hmerged["madgraph/unweighted"], out_dir, **kwargs)

    #reweigh_madgraph_hists(hmerged["madgraph"]["WJets_hf"], hmerged["madgraph"]["WJets_lf"])

    kwargs = dict({"x_label": var["varname"]}, **kwargs)

    for k, v in hmerged.items():
        logger.debug("Group %s" % k)
        for hn, h in v.items():
            logger.debug("Sample %s = %.2f" % (hn, h.Integral()))
        logger.debug("data=%.2f" % v["data"].Integral())
        logger.debug("MC=%.2f" % sum([h.Integral() for k, h in v.items() if k!="data"]))

    hists_flavours_merged = dict()
    hists_flavours_merged["madgraph/weighted"] = merge_hists(hmerged["madgraph/weighted"], {"WJets": ["WJets_hf", "WJets_lf"]})
    hists_flavours_merged["madgraph/unweighted"] = merge_hists(hmerged["madgraph/unweighted"], {"WJets": ["WJets_hf", "WJets_lf"]})
    hists_flavours_merged["sherpa"] = merge_hists(hmerged["sherpa"], {"WJets": ["WJets_hf", "WJets_lf"]})

    logger.info("Drawing sherpa plot")
    canv = ROOT.TCanvas("c1", "c1")
    plot(canv, "sherpa"+suffix, hmerged["sherpa"], out_dir, **kwargs)

    logger.info("Drawing madgraph plot")
    canv = ROOT.TCanvas("c2", "c2")
    plot(canv, "madgraph"+suffix, hmerged["madgraph/weighted"], out_dir, **kwargs)

    total_madgraph = copy.deepcopy(hmerged["madgraph/unweighted"])
    logger.info("Drawing sherpa vs. madgraph shape comparison plots")

    hists = [
        ("data", hmerged["madgraph/unweighted"]["data"]),
        ("madgraph unw", hists_flavours_merged["madgraph/unweighted"]["WJets"]),
        ("madgraph rew", hists_flavours_merged["madgraph/weighted"]["WJets"]),
    ]
    hists = copy.deepcopy(hists)
    for hn, h in hists:
        h.SetTitle(hn)
        h.Scale(1.0/h.Integral())
    hists = [h[1] for h in hists]
    ColorStyleGen.style_hists(hists)
    canv = plot_hists(hists, x_label=var["varname"], do_chi2=True)
    leg = legend(hists, styles=["f", "f"], **kwargs)
    canv.SaveAs(out_dir + "/weighted_%s.png" % hname)
    canv.Close()

    hists = [
        ("madgraph unw hf", hmerged["madgraph/unweighted"]["WJets_hf"]),
        ("madgraph rew hf", hmerged["madgraph/weighted"]["WJets_hf"]),
    ]
    hists = copy.deepcopy(hists)
    for hn, h in hists:
        h.SetTitle(hn)
        h.Scale(1.0/h.Integral())
    hists = [h[1] for h in hists]
    ColorStyleGen.style_hists(hists)
    canv = plot_hists(hists, x_label=var["varname"], do_chi2=True)
    leg = legend(hists, styles=["f", "f"], **kwargs)
    canv.SaveAs(out_dir + "/weighted_flavour_hf_%s.png" % hname)
    canv.Close()

    hists = [
        ("madgraph unw lf", hmerged["madgraph/unweighted"]["WJets_lf"]),
        ("madgraph rew lf", hmerged["madgraph/weighted"]["WJets_lf"]),
    ]
    hists = copy.deepcopy(hists)
    for hn, h in hists:
        h.SetTitle(hn)
        h.Scale(1.0/h.Integral())
    hists = [h[1] for h in hists]
    ColorStyleGen.style_hists(hists)
    canv = plot_hists(hists, x_label=var["varname"], do_chi2=True)
    leg = legend(hists, styles=["f", "f"], **kwargs)
    canv.SaveAs(out_dir + "/weighted_flavour_lf_%s.png" % hname)
    canv.Close()

    hists = [
        ("data", hmerged["madgraph/unweighted"]["data"]),
        ("madgraph unw", hists_flavours_merged["madgraph/unweighted"]["WJets"]),
        ("madgraph rew", hists_flavours_merged["madgraph/weighted"]["WJets"]),
        ("sherpa unw", hists_flavours_merged["sherpa"]["WJets"]),
    ]
    hists = copy.deepcopy(hists)
    for hn, h in hists:
        h.Scale(1.0/h.Integral())
        h.SetTitle(hn)
    hists = [h[1] for h in hists]
    ColorStyleGen.style_hists(hists)

    canv = plot_hists(hists, x_label=var["varname"], do_chi2=True)
    leg = legend(hists, styles=["f", "f"], **kwargs)
    hists[0].SetTitle("")
    canv.Update()
    canv.SaveAs(out_dir + "/shapes_%s.png" % hname)
    canv.Close()

    hists = [
        ("sherpa hf", hmerged["sherpa"]["WJets_hf"]),
        ("madgraph unw hf", hmerged["madgraph/unweighted"]["WJets_hf"]),
        ("madgraph rew hf", hmerged["madgraph/weighted"]["WJets_hf"]),
    ]
    hists = copy.deepcopy(hists)
    for hn, h in hists:
        h.SetTitle(hn)
        h.Scale(1.0/h.Integral())
    hists = [h[1] for h in hists]
    ColorStyleGen.style_hists(hists)
    canv = plot_hists(hists, x_label=var["varname"], do_chi2=True)
    leg = legend(hists, styles=["f", "f"], **kwargs)
    hists[0].SetTitle("madgraph sherpa rew hf")
    canv.SaveAs(out_dir + "/shapes_hf_%s.png" % hname)
    canv.Close()

    return total_madgraph, hist_coll

def plot_ratios(cut_name, cut, samples, out_dir, recreate):
    out_dir += "/" + cut_name
    mkdir_p(out_dir)
    if recreate:
        samples_WJets = filter(lambda x: sample_types.is_wjets(x.name), samples.values())
        logger.debug("Using samples %s" % str(samples_WJets))

        hists = {}
        metadata = {}
        for sample in samples_WJets:
            logger.debug("Drawing histogram from %s" % sample.name)
            for sc in flavour_scenarios:
                logger.debug("Flavor scenario %s" % sc)
                hist = sample.drawHistogram(costheta["var"], str(cut*Cuts.Wflavour(sc)), weight=str(Weights.total()), plot_range=costheta["range"]).hist
                hist.Scale(sample.lumiScaleFactor(LUMI_TOTAL))
                hname = "%s__%s" % (sample.name, sc)

                hist.SetName(hname)
                hists[hname] = hist
                hist.SetTitle(sc)

                metadata[hname] = HistMetaData(sample_name=sample.name, flavour_scenario=sc)
        coll = HistCollection(hists, metadata, "hists__costheta_flavour_ratios")
        coll.save(out_dir)
    else:
        coll = HistCollection.load(out_dir + "/hists__costheta_flavour_ratios.root")

    hists = coll.hists.values()

    merges = {}
    for sc in flavour_scenarios:
        merges["WJets/madgraph/%s" % sc] = ["W.*Jets_exclusive__%s" % sc]
        merges["WJets/sherpa/%s" % sc] = ["WJets_sherpa_nominal__%s" % sc]

    merged = merge_hists(coll.hists, merges)

    for sc in flavour_scenarios:
        hists = [merged["WJets/madgraph/%s" % sc], merged["WJets/sherpa/%s" % sc]]
        for hist in hists:
            hist.Scale(1.0/hist.Integral())
            #hist.SetName(sc)
            #hist.SetTitle(sc)
        ColorStyleGen.style_hists(hists)
        canv = plot_hists(hists, x_label=costheta["varname"])
        leg = legend(hists, styles=["f", "f"], nudge_x=-0.2)
        chi2 = hists[0].Chi2Test(hists[1], "WW CHI2/NDF")
        hists[0].SetTitle("madgraph sherpa comparison #chi^{2}/ndf=%.2f" % chi2)
        canv.Update()
        canv.SaveAs(out_dir + "/flavours__%s.png" % sc)

    md_merged = dict()
    for hn, h in merged.items():
        md_merged[hn] = HistMetaData(sample_names = merges[hn])
    hc_merged = HistCollection(merged, md_merged, "hists__costheta_flavours_merged")
    hc_merged.save(out_dir)
    logger.info("Saved merged histogram collection")

if __name__=="__main__":
    logging.basicConfig(level=logging.ERROR)
    tdrstyle()
    logger.setLevel(level=logging.DEBUG)
    logging.getLogger("utils").setLevel(logging.DEBUG)
    ROOT.gStyle.SetOptTitle(True)

    import argparse

    parser = argparse.ArgumentParser(description='Draw WJets sherpa plots')
    parser.add_argument('--recreate', dest='recreate', action='store_true')
    parser.add_argument('--tag', type=str, default="test")
    args = parser.parse_args()

    if args.recreate:
        samples = load_samples(os.environ["STPOL_DIR"])
        for s in samples.values():
            if sample_types.is_wjets(s.name):
                s.tree.AddFriend("trees/WJets_weights", s.tfile)

    else:
        samples = {}

    out_dir = os.environ["STPOL_DIR"] + "/out/plots/wjets"
    if args.tag:
        out_dir += "/" + args.tag
    mkdir_p(out_dir)

    #plot_ratios("2J", Cuts.final_jet(2), samples, out_dir, args.recreate)

    hists_2J0T, coll1 = plot_sherpa_vs_madgraph(
        costheta, "2J0T",
        str(Cuts.mu*Cuts.final(2,0)),
        samples, out_dir, recreate=args.recreate, legend_pos="top-left", nudge_x=-0.03, nudge_y=0
    )

    sf_Wlight = hists_2J0T["data"].Integral() / (
        sum([h.Integral() for k, h in hists_2J0T.items() if k!="data"])
    )
    del coll1

    for syst in ["nominal", "wjets_up", "wjets_down"]:
        plot_sherpa_vs_madgraph(
            costheta, "2J0T",
            str(Cuts.mu*Cuts.final(2,0)),
            samples, out_dir, recreate=args.recreate, legend_pos="top-left", nudge_x=-0.03, nudge_y=0, systematic=syst
        )
        plot_sherpa_vs_madgraph(
            costheta, "2J1T",
            str(Cuts.mu*Cuts.final(2,1)),
            samples, out_dir, recreate=args.recreate, legend_pos="top-left", nudge_x=-0.03, nudge_y=0, systematic=syst
        )
