import ROOT
from plots.common.sample import Sample, load_samples, get_process_name
from plots.common.sample_style import Styling, ColorStyleGen
import plots.common.utils
from plots.common.utils import merge_hists, mkdir_p, get_stack_total_hist
from plots.common.odict import OrderedDict
from plots.common.stack_plot import plot_hists_stacked
from plots.common.cuts import Cuts, Cut
from plots.common.cross_sections import xs as cross_sections
from plots.common.legend import legend
from plots.common.tdrstyle import tdrstyle
from plots.common.hist_plots import plot_hists, plot_data_mc_ratio

import copy
import os
import re
import logging
import pickle
import math

import rootpy
import rootpy.io
import rootpy.io.utils
from rootpy.io.file import File
import sys
from plots.common.histogram import HistCollection, HistMetaData
from plots.common.utils import escape, filter_hists

def draw_data_mc(var, plot_range, cut_str, weight_str, lumi, samples, out_dir, collection_name=None):
    import rootpy
    import rootpy.io
    import rootpy.io.utils
    from rootpy.io.file import File

    hists = dict()
    metadata = dict()
    for name, sample in samples.items():

        md = HistMetaData(
            sample_name=sample.name,
            sample_process_name=sample.process_name,
        )
        #metadata["iso/%s" % sample.name] = md

        if sample.isMC:
            sample_weight_str = weight_str
            hn = "mc/iso/%s" % sample.name
            #FIXME
            if "sherpa" in sample.name:
                logging.debug("Sample %s: enabling gen_weight" % (sample.name))
                sample_weight_str += "*gen_weight"

            if "sherpa_nominal_reweighted" in sample.name:
                logging.debug("Sample %s: enabling wjets_flavour_weight" % (sample.name))
                sample_weight_str += "*wjets_flavour_weight"

                hist_hf = sample.drawHistogram(var, cut_str+"&&(wjets_flavour_classification>0 && wjets_flavour_classification<5)", weight=sample_weight_str, plot_range=plot_range)
                hist_lf = sample.drawHistogram(var, cut_str+"&&(wjets_flavour_classification==0 || wjets_flavour_classification==5)", weight=sample_weight_str, plot_range=plot_range)
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

        metadata[hn] = md
        hists[hn] = hist

    if not collection_name:
        collection_name = "%s" % var
        collection_name = escape(collection_name)
    hc = HistCollection(hists, metadata, collection_name)
    hc.save(out_dir)

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

    logging.debug("Drawing stack")
    stacks = plot_hists_stacked(canv, hists, **kwargs)
    stacks["mc"].GetXaxis().SetLabelOffset(999.)
    stacks["mc"].GetXaxis().SetTitleOffset(999.)

    logging.debug("Drawing ratio")

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

    logging.debug("Drawing legend")
    leg = legend(hists["data"] + hists["mc"], styles=["p", "f"], **kwargs)

    canv.Update()
    canv.SaveAs(out_dir + "/%s.png" % name)
    canv.Close() #Must close canvas to prevent hang in ROOT upon GC
    logging.debug("Returning from plot()")
    return

def is_mc(path):
    return path.split("/")[0] == "mc"

def reweigh_sherpa_hists(h_heavy, h_light, syst="nominal"):

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
    mkdir_p(out_dir)
    
    logging.info("Using output directory %s" % out_dir)

    hname = escape(var["var"])
    if recreate:
        logging.info("Drawing histograms for variable=%s, cut=%s" % (var["var"], cut_name))
        hists = draw_data_mc(
            var["var"], var["range"],
            cut_str,
            "pu_weight*muon_IDWeight*muon_TriggerWeight*muon_IsoWeight*b_weight_nominal", 19739, samples, out_dir,
            collection_name=hname
        )

    hist_coll = HistCollection.load(out_dir + "/hists__%s.root" % hname)
    hist_coll.hists["mc/iso/WJets_sherpa_nominal_reweighted_hf"].SetFillColor(
        hist_coll.hists["mc/iso/WJets_sherpa_nominal_reweighted_hf"].GetFillColor()+1
        )
    hist_coll.hists["mc/iso/WJets_sherpa_nominal_reweighted_hf"].SetLineColor(
        hist_coll.hists["mc/iso/WJets_sherpa_nominal_reweighted_hf"].GetLineColor()+1
        )
    logging.debug("Loaded hists: %s" % str(hist_coll.hists))


    #Combine data and mc hists to one dict
    hjoined = dict(
        filter_hists(hist_coll.hists, "mc/iso/(.*)"), 
        **filter_hists(hist_coll.hists, "data/iso/(SingleMu)")
    )

    merges = dict()
    #merge_cmds.pop("WJets")
    #merge_cmds["WJets_hf"] = ["W1Jets_exclusive_hf", "W2Jets_exclusive_hf", "W3Jets_exclusive_hf", "W4Jets_exclusive_hf"]
    #merge_cmds["WJets_lf"] = ["W1Jets_exclusive_lf", "W2Jets_exclusive_lf", "W3Jets_exclusive_lf", "W4Jets_exclusive_lf"]
    
    merge_cmds = plots.common.utils.merge_cmds.copy()
    merges["madgraph"] = merge_cmds.copy()
    merges["sherpa"] = merge_cmds.copy()
    merge_cmds.pop("WJets")
    merges["sherpa_rew"] = merge_cmds.copy()
    
    merges["sherpa"]["WJets"] = ["WJets_sherpa_nominal"]
   #merges["sherpa"]["WJets_lf"] = ["WJets_sherpa_nominal_lf"]

    merges["sherpa_rew"]["WJets_hf"] = ["WJets_sherpa_nominal_reweighted_hf"]
    merges["sherpa_rew"]["WJets_lf"] = ["WJets_sherpa_nominal_reweighted_lf"]
    hmerged = {k:merge_hists(hjoined, merges[k]) for k in merges.keys()}


    reweigh_sherpa_hists(hmerged["sherpa_rew"]["WJets_hf"], hmerged["sherpa_rew"]["WJets_lf"])
    # #Measured in 2J
    # #tot_sherpa = 94423.38#hmerged["sherpa_rew"]["WJets"].Integral()
    # tot_sherpa = 92141.60 #After applying the flavour-based weighting
    # tot_madgraph = 90893.48#hmerged["madgraph"]["WJets"].Integral()
    # logging.info("Unweighted sherpa sample norm: %.2f" %  hmerged["sherpa"]["WJets"].Integral())
    # def tot_sherpa_rew(): return hmerged["sherpa_rew"]["WJets_hf"].Integral() + hmerged["sherpa_rew"]["WJets_lf"].Integral()
    # logging.info("Weighted sherpa sample norm: %.2f" %  tot_sherpa_rew())
    # hmerged["sherpa_rew"]["WJets_hf"].Scale(tot_madgraph / tot_sherpa)
    # hmerged["sherpa_rew"]["WJets_lf"].Scale(1.22)
    # logging.info("Scaled sherpa to madgraph: %.2f -> %.2f = %.2f" % (tot_sherpa, tot_madgraph, tot_sherpa_rew()))
    
    kwargs = dict({"x_label": var["varname"]}, **kwargs)

    for k, v in hmerged.items():
        logging.info("Group %s" % k)
        for hn, h in v.items():
            logging.info("Sample %s = %.2f" % (hn, h.Integral()))

    logging.info("Drawing sherpa plot")
    canv = ROOT.TCanvas("c1", "c1")
    suffix = "__%s__%s" % (var["var"], cut_name)
    plot(canv, "sherpa"+suffix, hmerged["sherpa"], out_dir, **kwargs)

    logging.info("Drawing madgraph plot")
    canv = ROOT.TCanvas("c2", "c2")
    plot(canv, "madgraph"+suffix, hmerged["madgraph"], out_dir, **kwargs)

    logging.info("Drawing sherpa reweighed plot")
    canv = ROOT.TCanvas("c3", "c3")
    plot(canv, "sherpa_rew"+suffix, hmerged["sherpa_rew"], out_dir, **kwargs)

    hmerged_unnorm = copy.deepcopy(hmerged)
    logging.info("Drawing sherpa vs. madgraph shape comparison plots")
    #canv = ROOT.TCanvas("c4", "c4")
    histsnames = [
        ("data", hmerged["madgraph"]["data"]),
        ("madgraph", hmerged["madgraph"]["WJets"]),
        ("sherpa unw", hmerged["sherpa"]["WJets"]),
        #("sherpa (rew) HF", hmerged["sherpa_rew"]["WJets_hf"]),
        #("sherpa (rew) LF", hmerged["sherpa_rew"]["WJets_lf"])
    ]
    hists = [h[1] for h in histsnames]
    ColorStyleGen.style_hists(hists)
    for hn, h in histsnames:
        h.Scale(1.0/h.Integral())
        h.SetTitle(hn)

    chi2_1 = hmerged["madgraph"]["data"].Chi2Test(hmerged["madgraph"]["WJets"], "WW CHI2/NDF")
    chi2_2 = hmerged["madgraph"]["data"].Chi2Test(hmerged["sherpa"]["WJets"], "WW CHI2/NDF")
    hmerged["madgraph"]["WJets"].SetTitle(hmerged["madgraph"]["WJets"].GetTitle() + " #chi^{2}/ndf = %.2f" % chi2_1)
    hmerged["sherpa"]["WJets"].SetTitle(hmerged["sherpa"]["WJets"].GetTitle() + " #chi^{2}/ndf = %.2f" % chi2_2)

    canv = plot_hists(hists, x_label=var["varname"])
    leg = legend(hists, styles=["f", "f"], **kwargs)
    #hists[0].SetTitle("mg_sherpa_shapes__%s" % (cut_name))
    hists[0].SetTitle("")
    canv.Update()
    canv.SaveAs(out_dir + "/shapes_%s.png" % hname)
    canv.Close()

    return hmerged_unnorm

if __name__=="__main__":
    logging.basicConfig(level=logging.INFO)
    tdrstyle()
    ROOT.gStyle.SetOptTitle(True)

    import argparse

    parser = argparse.ArgumentParser(description='Draw WJets sherpa plots')
    parser.add_argument('--recreate', dest='recreate', action='store_true')
    parser.add_argument('--tag', type=str, default=None)
    args = parser.parse_args()

    if args.recreate:
        samples = load_samples(os.environ["STPOL_DIR"])
    else:
        samples = None

    out_dir = os.environ["STPOL_DIR"] + "/out/plots/wjets"
    if args.tag:
        out_dir += "/" + args.tag
    mkdir_p(out_dir)

    costheta = {"var":"cos_theta", "varname":"cos #theta", "range":[20,-1,1]}
    mtop = {"var":"top_mass", "varname":"M_{bl#nu}", "range":[20, 130, 220]}
    mu_pt = {"var":"mu_pt", "varname":"p_{t,#mu}", "range":[20, 30, 220]}
    lj_pt = {"var":"pt_lj", "varname":"p_{t,q}", "range":[20, 30, 150]}
    bj_pt = {"var":"pt_bj", "varname":"p_{t,b}", "range":[20, 30, 150]}
    eta_pos = {"var":"eta_lj", "varname":"#eta_{lq}", "range":[20, 2.5, 5.0]}
    eta_neg = {"var":"eta_lj", "varname":"#eta_{lq}", "range":[20, -5.0, -2.5]}
    aeta_lj = {"var":"abs(eta_lj)", "varname":"|#eta_{lq}|", "range":[20, 0, 5]}
    aeta_lj_2_5 = {"var":"abs(eta_lj)", "varname":"|#eta_{lq}|", "range":[20, 2.5, 5]}

    hists_2J0T = plot_sherpa_vs_madgraph(
        costheta, "2J0T",
        str(Cuts.mu*Cuts.final(2,0)),
        samples, out_dir, recreate=args.recreate, legend_pos="top-left", nudge_x=-0.03, nudge_y=0
    )
    sf_Wlight = hists_2J0T["madgraph"]["data"].Integral() / hists_2J0T["madgraph"]["WJets"].Integral()
    print "sf_Wlight = %.8f" % sf_Wlight
    print "err_sf_Wlight = %.8f" % abs((1-sf_Wlight))
    # plot_sherpa_vs_madgraph(
    #     costheta, "2J",
    #     str(Cuts.mu*Cuts.rms_lj*Cuts.mt_mu*Cuts.n_jets(2)*Cuts.eta_lj*Cuts.top_mass_sig),
    #     samples, out_dir, recreate=args.recreate, legend_pos="top-left", nudge_x=-0.03, nudge_y=0.05
    # )

    # plot_sherpa_vs_madgraph(
    #     aeta_lj_2_5, "2J0T",
    #     str(Cuts.mu*Cuts.final(2,0)),
    #     samples, out_dir, recreate=args.recreate, legend_pos="top-right",
    # )
    # plot_sherpa_vs_madgraph(
    #     costheta, "2J1T",
    #     str(Cuts.mu*Cuts.final(2,1)),
    #     samples, out_dir, recreate=args.recreate, legend_pos="top-left", nudge_x=-0.03, nudge_y=0.05
    # )
    # plot_sherpa_vs_madgraph(
    #     aeta_lj_2_5, "2J1T",
    #     str(Cuts.mu*Cuts.final(2,1)),
    #     samples, out_dir, recreate=args.recreate, legend_pos="top-right",
    # )