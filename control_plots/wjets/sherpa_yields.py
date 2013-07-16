import ROOT
from plots.common.sample import Sample, load_samples, get_process_name
from plots.common.sample_style import Styling, ColorStyleGen
import plots.common.utils
from plots.common.utils import merge_hists, mkdir_p, get_stack_total_hist
from plots.common.odict import OrderedDict
from plots.common.stack_plot import plot_hists_stacked
from plots.common.cuts import Cuts, Cut, Weights, flavour_scenarios
from plots.common.cross_sections import xs as cross_sections
from plots.common.legend import legend
from plots.common.tdrstyle import tdrstyle
from plots.common.hist_plots import plot_hists, plot_data_mc_ratio
from SingleTopPolarization.Analysis import sample_types
import copy
import os
import re
import logging
logger = logging.getLogger("sherpa_yields")
import pickle
import math
import shutil
import rootpy
import rootpy.io
import rootpy.io.utils
from rootpy.io.file import File
import sys
from plots.common.histogram import HistCollection, HistMetaData
from plots.common.utils import escape, filter_hists
import rootpy
import rootpy.io
import rootpy.io.utils
from rootpy.io.file import File

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
def draw_data_mc(var, plot_range, cut_str, weight_str, lumi, samples, out_dir, collection_name=None):
    hists = dict()
    metadata = dict()
    for name, sample in samples.items():

        md = HistMetaData(
            sample_name=sample.name,
            sample_process_name=sample.process_name,
        )

        if sample.isMC:
            sample_weight_str = weight_str
            hn = "mc/iso/%s" % sample.name

            if sample_types.is_wjets(sample.name):
                logger.debug("Sample %s: enabling hf/lf separation" % (sample.name))

                hist_hf = sample.drawHistogram(var, cut_str+"&&(wjets_flavour_classification>=0 && wjets_flavour_classification<5)", weight=sample_weight_str, plot_range=plot_range)
                hist_lf = sample.drawHistogram(var, cut_str+"&&(wjets_flavour_classification>=5)", weight=sample_weight_str, plot_range=plot_range)
                metadata[hn + "_hf"] = md
                metadata[hn + "_lf"] = md
                hist_hf.hist.Scale(sample.lumiScaleFactor(lumi)) 
                hist_lf.hist.Scale(sample.lumiScaleFactor(lumi)) 
                hists[hn + "_hf"] = hist_hf.hist
                hists[hn + "_lf"] = hist_lf.hist

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
            collection_name=hname
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
        match = re.match("(.*)_([hl]f)", hn)
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
    merges["madgraph_unsplit"] = merge_cmds.copy()
    merge_cmds.pop("WJets")
    merges["madgraph"] = merge_cmds.copy()
    merges["sherpa"] = merge_cmds.copy()
    
    
    merges["sherpa"]["WJets_hf"] = ["WJets_sherpa_nominal_hf"]
    merges["sherpa"]["WJets_lf"] = ["WJets_sherpa_nominal_lf"]
    merges["madgraph"]["WJets_hf"] = ["W[0-9]Jets_exclusive_hf"]
    merges["madgraph"]["WJets_lf"] = ["W[0-9]Jets_exclusive_lf"]

    hmerged = {k:merge_hists(hjoined, merges[k]) for k in merges.keys()}

    reweigh_madgraph_hists(hmerged["madgraph"]["WJets_hf"], hmerged["madgraph"]["WJets_lf"])

    kwargs = dict({"x_label": var["varname"]}, **kwargs)

    for k, v in hmerged.items():
        logger.debug("Group %s" % k)
        for hn, h in v.items():
            logger.debug("Sample %s = %.2f" % (hn, h.Integral()))

    hists_flavours_merged = dict()
    hists_flavours_merged["madgraph"] = merge_hists(hmerged["madgraph"], {"WJets": ["WJets_hf", "WJets_lf"]})
    hists_flavours_merged["sherpa"] = merge_hists(hmerged["sherpa"], {"WJets": ["WJets_hf", "WJets_lf"]})

    logger.info("Drawing sherpa plot")
    canv = ROOT.TCanvas("c1", "c1")
    suffix = "__%s__%s" % (var["var"], cut_name)
    plot(canv, "sherpa"+suffix, hmerged["sherpa"], out_dir, **kwargs)

    logger.info("Drawing madgraph plot")
    canv = ROOT.TCanvas("c2", "c2")
    plot(canv, "madgraph"+suffix, hmerged["madgraph"], out_dir, **kwargs)

    total_madgraph = copy.deepcopy(hmerged["madgraph_unsplit"])
    logger.info("Drawing sherpa vs. madgraph shape comparison plots")

    histsnames = [
        ("data", hmerged["madgraph"]["data"]),
        ("madgraph", hists_flavours_merged["madgraph"]["WJets"]),
        ("sherpa unw", hists_flavours_merged["sherpa"]["WJets"]),
    ]
    hists = [h[1] for h in histsnames]
    ColorStyleGen.style_hists(hists)
    for hn, h in histsnames:
        h.Scale(1.0/h.Integral())
        h.SetTitle(hn)

    chi2_1 = hmerged["madgraph"]["data"].Chi2Test(hists_flavours_merged["madgraph"]["WJets"], "WW CHI2/NDF")
    chi2_2 = hmerged["madgraph"]["data"].Chi2Test(hists_flavours_merged["sherpa"]["WJets"], "WW CHI2/NDF")
    hists_flavours_merged["madgraph"]["WJets"].SetTitle(hists_flavours_merged["madgraph"]["WJets"].GetTitle() + " #chi^{2}/ndf = %.2f" % chi2_1)
    hists_flavours_merged["sherpa"]["WJets"].SetTitle(hists_flavours_merged["sherpa"]["WJets"].GetTitle() + " #chi^{2}/ndf = %.2f" % chi2_2)

    canv = plot_hists(hists, x_label=var["varname"])
    leg = legend(hists, styles=["f", "f"], **kwargs)
    hists[0].SetTitle("")
    canv.Update()
    canv.SaveAs(out_dir + "/shapes_%s.png" % hname)
    canv.Close()

    return total_madgraph

def plot_ratios(cut_name, cut, samples, out_dir, recreate):
    out_dir += "/" + cut_name
    if recreate:
        samples_WJets = filter(lambda x: sample_types.is_wjets(x.name), samples)
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

if __name__=="__main__":
    logging.basicConfig(level=logging.INFO)
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
    else:
        samples = {}

    out_dir = os.environ["STPOL_DIR"] + "/out/plots/wjets"
    if args.tag:
        out_dir += "/" + args.tag
    mkdir_p(out_dir)

    plot_ratios("2J", Cuts.final_jet(2), samples, out_dir, args.recreate)

    hists_2J0T = plot_sherpa_vs_madgraph(
        costheta, "2J0T",
        str(Cuts.mu*Cuts.final(2,0)),
        samples, out_dir, recreate=args.recreate, legend_pos="top-left", nudge_x=-0.03, nudge_y=0
    )
    sf_Wlight = hists_2J0T["data"].Integral() / hists_2J0T["WJets"].Integral()
    print "sf_Wlight = %.8f" % sf_Wlight
    print "err_sf_Wlight = %.8f" % abs((1-sf_Wlight))