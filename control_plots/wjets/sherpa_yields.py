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
from plots.common.histogram import norm

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

import pdb

from plot_utils import *
LUMI_TOTAL = 19739

def get_merge_cmds(pref="weight__nominal/cut__all/"):
    cmds = plots.common.utils.merge_cmds.copy()
    for k, v in cmds.items():
        if k!="data":
            cmds[k] = map(lambda x: pref+x, v)
    return cmds

def plot_sherpa_vs_madgraph(var, cut_name, cut, samples, out_dir, recreate=False, **kwargs):
    hname = var["varname"]
    out_dir = out_dir + "/" + cut_name
    if recreate and os.path.exists(out_dir):
        logger.info("Output directory %s exists, removing" % out_dir)
        shutil.rmtree(out_dir)
    mkdir_p(out_dir)

    logger.info("Using output directory %s" % out_dir)


    logger.info("Using output directory %s" % out_dir)

    coll = data_mc(var["var"], cut_name, cut, Weights.total()*Weights.mu, samples, out_dir, recreate, LUMI_TOTAL, reweight_madgraph=True, flavour_split=True, plot_range=var["range"], **kwargs)

    logging.debug(str(coll.hists))
    for hn, hist in coll.hists.items():
        sample_name = coll.metadata[hn].sample_name
        process_name = coll.metadata[hn].process_name
        match = re.match(".*/cut__flavour__(W_[Hl][Hl])/.*", hn)
        if match:
            flavour_scenario = match.group(1)
        else:
            flavour_scenario = None

        try:
            if sample_types.is_mc(sample_name):
                Styling.mc_style(hist, process_name)
            else:
                Styling.data_style(hist)
        except KeyError as e:
            logger.warning("Couldn't style histogram %s" % hn)

        if flavour_scenario:
            logger.debug("Matched flavour split histogram %s, %s" % (hn, flavour_scenario))
            #Styling.mc_style(hist, process_name)
            if re.match("W_H[lH]", flavour_scenario):
                logger.debug("Changing colour of %s" % (hn))
                hist.SetFillColor(hist.GetFillColor()+1)
                hist.SetLineColor(hist.GetLineColor()+1)

    logger.debug("pre merge: %s" % str([ (hn, coll.hists[hn].GetLineColor()) for hn in coll.hists.keys() if "sherpa" in hn]))
    merges = dict()

    merge_cmds = get_merge_cmds()
    merge_cmds.pop("WJets")
    merges["madgraph/unweighted"] = merge_cmds.copy()
    merges["madgraph/weighted"] = merge_cmds.copy()
    merges["sherpa/unweighted"] = merge_cmds.copy()
    merges["sherpa/weighted"] = merge_cmds.copy()


    merges["sherpa/unweighted"]["WJets_hf"] = ["weight__nominal/cut__flavour__W_H[lH]/WJets_sherpa_nominal"]
    merges["sherpa/unweighted"]["WJets_lf"] = ["weight__nominal/cut__flavour__W_ll/WJets_sherpa_nominal"]
    merges["sherpa/weighted"]["WJets_hf"] = ["weight__sherpa_flavour/cut__flavour__W_H[lH]/WJets_sherpa_nominal"]
    merges["sherpa/weighted"]["WJets_lf"] = ["weight__sherpa_flavour/cut__flavour__W_ll/WJets_sherpa_nominal"]
    merges["madgraph/unweighted"]["WJets_hf"] = ["weight__nominal/cut__flavour__W_H[lH]/W[1-4]Jets_exclusive"]
    merges["madgraph/unweighted"]["WJets_lf"] = ["weight__nominal/cut__flavour__W_ll/W[1-4]Jets_exclusive"]
    merges["madgraph/weighted"]["WJets_hf"] = ["weight__reweight_madgraph/cut__flavour__W_H[lH]/W[1-4]Jets_exclusive"]
    merges["madgraph/weighted"]["WJets_lf"] = ["weight__reweight_madgraph/cut__flavour__W_ll/W[1-4]Jets_exclusive"]

    hmerged = dict()
    for k in merges.keys():
        hmerged[k] = merge_hists(copy.deepcopy(coll.hists), merges[k])

    logger.debug("post merge: %s" % str([ (hn, hmerged["sherpa/weighted"][hn].GetLineColor()) for hn in hmerged["sherpa/weighted"].keys()]))

    #w_mg_sh = 1.0416259307303726 #sherpa to madgraph ratio
    w_mg_sh = 1.0821535639376414
    hmerged["sherpa/weighted"]["WJets_hf"].Scale(w_mg_sh)
    hmerged["sherpa/weighted"]["WJets_lf"].Scale(w_mg_sh)

    logger.info("Drawing madgraph unweighted plot")
    canv = ROOT.TCanvas("c2", "c2")
    suffix = "__%s__%s" % (var["var"], cut_name)
    suffix = escape(suffix)
    plot(canv, "madgraph_unw"+suffix, hmerged["madgraph/unweighted"], out_dir, **kwargs)

    kwargs = dict({"x_label": var["varname"]}, **kwargs)

    for k, v in hmerged.items():
        logger.debug("Group %s" % k)
        for hn, h in v.items():
            logger.debug("Sample %s = %.2f" % (hn, h.Integral()))
        logger.info("%s data=%.2f" % (k, v["data"].Integral()))
        logger.info("%s MC=%.2f" % (k, sum([h.Integral() for k, h in v.items() if k!="data"])))

    hists_flavours_merged = dict()
    hists_flavours_merged["madgraph/weighted"] = merge_hists(hmerged["madgraph/weighted"], {"WJets": ["WJets_hf", "WJets_lf"]})
    hists_flavours_merged["madgraph/unweighted"] = merge_hists(hmerged["madgraph/unweighted"], {"WJets": ["WJets_hf", "WJets_lf"]})
    hists_flavours_merged["sherpa/unweighted"] = merge_hists(hmerged["sherpa/unweighted"], {"WJets": ["WJets_hf", "WJets_lf"]})
    hists_flavours_merged["sherpa/weighted"] = merge_hists(hmerged["sherpa/weighted"], {"WJets": ["WJets_hf", "WJets_lf"]})

    logger.info("Drawing sherpa weighted plot")
    canv = ROOT.TCanvas("c1", "c1")
    plot(canv, "sherpa_rew"+suffix, hmerged["sherpa/weighted"], out_dir, **kwargs)

    logger.info("Drawing sherpa unweighted plot")
    canv = ROOT.TCanvas("c1", "c1")
    plot(canv, "sherpa_unw"+suffix, hmerged["sherpa/unweighted"], out_dir, **kwargs)

    logger.info("Drawing madgraph plot")
    canv = ROOT.TCanvas("c2", "c2")
    plot(canv, "madgraph_rew"+suffix, hmerged["madgraph/weighted"], out_dir, **kwargs)

    total_madgraph = copy.deepcopy(hmerged["madgraph/unweighted"])
    merged_colls = dict()
    for k, v in hmerged.items():
        merged_colls[k] = HistCollection(copy.deepcopy(v), name=k)
    logger.info("Drawing sherpa vs. madgraph shape comparison plots")

    hists = [
        ("sherpa unw hf", hmerged["sherpa/unweighted"]["WJets_hf"]),
        ("sherpa rew hf", hmerged["sherpa/weighted"]["WJets_hf"]),
        ("madgraph unw hf", hmerged["madgraph/unweighted"]["WJets_hf"]),
        ("madgraph rew hf", hmerged["madgraph/weighted"]["WJets_hf"]),
    ]
    hists = copy.deepcopy(hists)
    for hn, h in hists:
        h.SetTitle(hn + " %.2f" % h.Integral())
        h.Scale(1.0/h.Integral())
    hists = [h[1] for h in hists]
    ColorStyleGen.style_hists(hists)
    canv = plot_hists(hists, x_label=var["varname"], do_chi2=True)
    leg = legend(hists, styles=["f", "f"], **kwargs)
    canv.SaveAs(out_dir + "/weighted_flavour_hf_%s.png" % hname)
    canv.Close()

    hists = [
        ("data", hmerged["madgraph/unweighted"]["data"]),
        ("sherpa", hists_flavours_merged["sherpa/unweighted"]["WJets"]),
        ("madgraph", hists_flavours_merged["madgraph/unweighted"]["WJets"]),
    ]
    hists = copy.deepcopy(hists)
    for hn, h in hists:
        h.SetTitle(hn + " %.2f" % h.Integral())
        h.Scale(1.0/h.Integral())
    hists = [h[1] for h in hists]
    ColorStyleGen.style_hists(hists)
    canv = plot_hists(hists, x_label=var["varname"], do_chi2=True)
    leg = legend(hists, styles=["f", "f"], **kwargs)
    canv.SaveAs(out_dir + "/unweighted_sherpa_mg_%s.png" % hname)
    canv.Close()

    hists = [
        ("data", hmerged["madgraph/unweighted"]["data"]),
        ("sherpa", hists_flavours_merged["sherpa/weighted"]["WJets"]),
        ("madgraph", hists_flavours_merged["madgraph/weighted"]["WJets"]),
    ]
    hists = copy.deepcopy(hists)
    for hn, h in hists:
        h.SetTitle(hn + " %.2f" % h.Integral())
        h.Scale(1.0/h.Integral())
    hists = [h[1] for h in hists]
    ColorStyleGen.style_hists(hists)
    canv = plot_hists(hists, x_label=var["varname"], do_chi2=True)
    leg = legend(hists, styles=["f", "f"], **kwargs)
    canv.SaveAs(out_dir + "/weighted_sherpa_mg_%s.png" % hname)
    canv.Close()

    hists = [
        ("sherpa unw lf", hmerged["sherpa/unweighted"]["WJets_lf"]),
        ("sherpa rew lf", hmerged["sherpa/weighted"]["WJets_lf"]),
        ("madgraph unw lf", hmerged["madgraph/unweighted"]["WJets_lf"]),
        ("madgraph rew lf", hmerged["madgraph/weighted"]["WJets_lf"]),
    ]
    hists = copy.deepcopy(hists)
    for hn, h in hists:
        h.SetTitle(hn + " %.2f" % h.Integral())
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
        ("sherpa unw", hists_flavours_merged["sherpa/unweighted"]["WJets"]),
        ("sherpa rew", hists_flavours_merged["sherpa/weighted"]["WJets"]),
    ]
    hists = copy.deepcopy(hists)
    for hn, h in hists:
        h.SetTitle(hn + " %.2f" % h.Integral())
        h.Scale(1.0/h.Integral())
    hists = [h[1] for h in hists]
    ColorStyleGen.style_hists(hists)
    canv = plot_hists(hists, x_label=var["varname"], do_chi2=True)
    leg = legend(hists, styles=["f", "f"], **kwargs)
    hists[0].SetTitle("")
    canv.Update()
    canv.SaveAs(out_dir + "/shapes_%s.png" % hname)
    canv.Close()

    # hists = [
    #     ("sherpa hf", hmerged["sherpa"]["WJets_hf"]),
    #     ("madgraph unw hf", hmerged["madgraph/unweighted"]["WJets_hf"]),
    #     ("madgraph rew hf", hmerged["madgraph/weighted"]["WJets_hf"]),
    # ]
    # hists = copy.deepcopy(hists)
    # for hn, h in hists:
    #     h.SetTitle(hn + " %.2f" % h.Integral())
    #     h.Scale(1.0/h.Integral())
    # hists = [h[1] for h in hists]
    # ColorStyleGen.style_hists(hists)
    # canv = plot_hists(hists, x_label=var["varname"], do_chi2=True)
    # leg = legend(hists, styles=["f", "f"], **kwargs)
    # hists[0].SetTitle("madgraph sherpa rew hf")
    # canv.SaveAs(out_dir + "/shapes_hf_%s.png" % hname)
    # canv.Close()

    return coll, merged_colls

def plot_ratios(cut_name, cut, samples, out_dir, recreate, flavour_scenario=flavour_scenarios[2]):
    out_dir += "/" + cut_name
    mkdir_p(out_dir)

    colls = dict()

    samples_WJets = filter(lambda x: sample_types.is_wjets(x.name), samples)

    for sc in flavour_scenario:
        logger.info("Drawing ratio with cut %s" % sc)
        cut_ = cut*getattr(Cuts, sc)
        colls[sc] = data_mc(costheta["var"], cut_name + "__" + sc, cut_, Weights.total()*Weights.mu, samples_WJets, out_dir, recreate, LUMI_TOTAL, plot_range=costheta["range"])

    logger.debug(colls[flavour_scenario[0]].hists["weight__nominal/cut__all/WJets_sherpa_nominal"].Integral())
    logger.debug(colls[flavour_scenario[1]].hists["weight__nominal/cut__all/WJets_sherpa_nominal"].Integral())
    coll = dict()
    for k, c in colls.items():
        for hn, h in c.hists.items():
            coll[hn + "/" + k] = h

    for k, h in coll.items():
        logger.debug("%s = %s" % (k, str([y for y in h.y()])))

    logger.debug(coll)
    #coll = HistCollection(coll, name=cut_name)

    merges = {}
    for sc in flavour_scenario:
        merges["madgraph/%s" % sc] = ["weight__nominal/cut__all/W[1-4]Jets_exclusive/%s" % sc]
        merges["sherpa/unweighted/%s" % sc] = ["weight__nominal/cut__all/WJets_sherpa_nominal/%s" % sc]
        merges["sherpa/weighted/%s" % sc] = ["weight__sherpa_flavour/cut__all/WJets_sherpa_nominal/%s" % sc]

    merged = merge_hists(coll, merges)
    for k, h in merged.items():
        logger.debug("%s = %s" % (k, str([y for y in h.y()])))
    hists_flavour = dict()
    hists_flavour["madgraph"] = ROOT.TH1F("madgraph", "madgraph", len(flavour_scenario), 0, len(flavour_scenario)-1)
    hists_flavour["sherpa/unweighted"] = ROOT.TH1F("sherpa_unw", "sherpa unweighted", len(flavour_scenario), 0, len(flavour_scenario)-1)
    hists_flavour["sherpa/weighted"] = ROOT.TH1F("sherpa_rew", "sherpa weighted", len(flavour_scenario), 0, len(flavour_scenario)-1)

    for i, sc in zip(range(1,len(flavour_scenario)+1), flavour_scenario):
        sh1_int, sh1_err = calc_int_err(merged["sherpa/unweighted/%s" % sc])
        sh2_int, sh2_err = calc_int_err(merged["sherpa/weighted/%s" % sc])
        mg_int, mg_err = calc_int_err(merged["madgraph/%s" % sc])
        logger.debug("%.2f %.2f" % (sh1_int, sh1_err))
        logger.debug("%.2f %.2f" % (sh2_int, sh2_err))
        logger.debug("%.2f %.2f" % (mg_int, mg_err))
        hists_flavour["madgraph"].SetBinContent(i, mg_int)
        hists_flavour["madgraph"].SetBinError(i, mg_err)
        hists_flavour["sherpa/unweighted"].SetBinContent(i, sh1_int)
        hists_flavour["sherpa/unweighted"].SetBinError(i, sh1_err)
        hists_flavour["sherpa/weighted"].SetBinContent(i, sh2_int)
        hists_flavour["sherpa/weighted"].SetBinError(i, sh2_err)

        hists_flavour["madgraph"].GetXaxis().SetBinLabel(i, sc)
        hists_flavour["sherpa/unweighted"].GetXaxis().SetBinLabel(i, sc)
        hists_flavour["sherpa/weighted"].GetXaxis().SetBinLabel(i, sc)

    hists_flavour["sherpa/weighted"].Sumw2()
    hists_flavour["sherpa/unweighted"].Sumw2()
    hists_flavour["madgraph"].Sumw2()

    hists_flavour["ratio/unweighted"] = hists_flavour["madgraph"].Clone("ratio_unw")
    hists_flavour["ratio/unweighted"].Divide(hists_flavour["sherpa/unweighted"])
    hists_flavour["ratio/weighted"] = hists_flavour["madgraph"].Clone("ratio_rew")
    hists_flavour["ratio/weighted"].Divide(hists_flavour["sherpa/weighted"])

    for i, sc in zip(range(1,len(flavour_scenario)+1), flavour_scenario):
        logger.info("weights[%s] = %.6f; //error=%.6f [%d]" % (sc, hists_flavour["ratio/unweighted"].GetBinContent(i), hists_flavour["ratio/unweighted"].GetBinError(i), i))

    flavour_ratio_coll = HistCollection(hists_flavour, name="hists__flavour_ratios")
    flavour_ratio_coll.save(out_dir)

    for sc in flavour_scenario:
        hists = [merged["madgraph/%s" % sc], merged["sherpa/unweighted/%s" % sc], merged["sherpa/weighted/%s" % sc]]
        for hist in hists:
            norm(hist)
            #hist.SetName(sc)
            #hist.SetTitle(sc)
        ColorStyleGen.style_hists(hists)
        canv = plot_hists(hists, x_label=costheta["varname"])
        leg = legend(hists, styles=["f", "f"], nudge_x=-0.2)
        chi2 = hists[0].Chi2Test(hists[1], "WW CHI2/NDF")
        hists[0].SetTitle("madgraph to sherpa comparison #chi^{2}/ndf=%.2f" % chi2)
        canv.Update()
        canv.SaveAs(out_dir + "/flavours__%s.png" % (sc))

    md_merged = dict()
    for sc in flavour_scenario:
        logger.info("Calculating ratio for %s" % sc)
        hi = merged["sherpa/unweighted/%s" % sc].Clone("ratio__%s" % sc)
        hi.Divide(merged["madgraph/%s" % sc])
        merged[hi.GetName()] = hi

    hc_merged = HistCollection(merged, md_merged, "hists__costheta_flavours_merged")
    hc_merged.save(out_dir)
    logger.info("Saved merged histogram collection")


if __name__=="__main__":
    logging.basicConfig(level=logging.INFO)
    tdrstyle()
    #logger.setLevel(logging.DEBUG)
    #logging.getLogger("utils").setLevel(logging.ERROR)
    #logging.getLogger("histogram").setLevel(logging.ERROR)
    #logging.getLogger("plot_utils").setLevel(logging.ERROR)
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

    # plot_ratios("2J0T", Cuts.final(2,0), samples, out_dir, args.recreate)
    # plot_ratios("2J1T", Cuts.final(2,1), samples, out_dir, args.recreate)
    plot_ratios("2J/ratios", Cuts.final_jet(2), samples.values(), out_dir, args.recreate)

    colls_in, colls_out = plot_sherpa_vs_madgraph(
        costheta, "2J",
        Cuts.mu*Cuts.final_jet(2),
        samples.values(), out_dir, recreate=args.recreate, legend_pos="top-left", nudge_x=-0.03, nudge_y=0, systematic="nominal"
    )
    hi_mg = colls_out["madgraph/weighted"].hists["WJets_hf"] + colls_out["madgraph/weighted"].hists["WJets_lf"]
    hi_sh = colls_out["sherpa/unweighted"].hists["WJets_hf"] + colls_out["sherpa/unweighted"].hists["WJets_lf"]
    hi_sh_w = colls_out["sherpa/weighted"].hists["WJets_hf"] + colls_out["sherpa/weighted"].hists["WJets_lf"]

    hf_mg = colls_out["madgraph/weighted"].hists["WJets_hf"].Integral() / hi_mg.Integral()
    lf_mg = colls_out["madgraph/weighted"].hists["WJets_lf"].Integral() / hi_mg.Integral()

    hf_sh = colls_out["sherpa/unweighted"].hists["WJets_hf"].Integral() / hi_sh.Integral()
    lf_sh = colls_out["sherpa/unweighted"].hists["WJets_lf"].Integral() / hi_sh.Integral()

    hf_sh_w = colls_out["sherpa/weighted"].hists["WJets_hf"].Integral() / hi_sh_w.Integral()
    lf_sh_w = colls_out["sherpa/weighted"].hists["WJets_lf"].Integral() / hi_sh_w.Integral()

    logger.info("mg = %s" % str(calc_int_err(hi_mg)))
    logger.info("sherpa unw = %s" % str(calc_int_err(hi_sh)))
    logger.info("sherpa rew = %s" % str(calc_int_err(hi_sh_w)))
    logger.info("madgraph fracs = %s" % str((hf_mg, lf_mg)))
    logger.info("sherpa fracs = %s" % str((hf_sh, lf_sh)))
    logger.info("sherpa weighted fracs = %s" % str((hf_sh_w, lf_sh_w)))
    # plot_sherpa_vs_madgraph(
    #     costheta, "2J",
    #     str(Cuts.mu*Cuts.final_jet(2)),
    #     samples, out_dir, recreate=args.recreate, legend_pos="top-left", nudge_x=-0.03, nudge_y=0, systematic="nominal"
    # )
    # plot_sherpa_vs_madgraph(
    #     costheta, "2J",
    #     str(Cuts.mu*Cuts.final_jet(2)),
    #     samples, out_dir, recreate=args.recreate, legend_pos="top-left", nudge_x=-0.03, nudge_y=0, systematic="nominal"
    # )

    # coll_in, coll_out = plot_sherpa_vs_madgraph(
    #     costheta, "2J0T",
    #     str(Cuts.mu*Cuts.final(2,0)),
    #     samples, out_dir, recreate=args.recreate, legend_pos="top-left", nudge_x=-0.03, nudge_y=0
    # )

    # def ratio(hists):
    #     tot_data = hists["data"].Integral()
    #     tot_mc_nonWlight = (
    #         sum([h.Integral() for k, h in hists.items() if k!="data" and k!= "WJets_lf"])
    #     )
    #     tot_mc_Wlight = hists["WJets_lf"].Integral()
    #     return tot_data, tot_mc_nonWlight, tot_mc_Wlight
    # A = ratio(coll_out["madgraph/unweighted"].hists)
    # print (A[0]-A[1])
    # print ratio(coll_out["madgraph/weighted"].hists)

    for syst in ["nominal", "wjets_up", "wjets_down"]:
        plot_sherpa_vs_madgraph(
            costheta, "2J/costheta/%s"%syst,
            Cuts.mu*Cuts.final_jet(2),
            samples.values(), out_dir, recreate=args.recreate, legend_pos="top-left", nudge_x=-0.03, nudge_y=0, systematic=syst
        )
        plot_sherpa_vs_madgraph(
            costheta, "2J0T/costheta/%s"%syst,
            Cuts.mu*Cuts.final(2,0),
            samples.values(), out_dir, recreate=args.recreate, legend_pos="top-left", nudge_x=-0.03, nudge_y=0, systematic=syst
        )
        plot_sherpa_vs_madgraph(
            costheta, "2J1T/costheta/%s"%syst,
            Cuts.mu*Cuts.final(2,1),
            samples.values(), out_dir, recreate=args.recreate, legend_pos="top-left", nudge_x=-0.03, nudge_y=0, systematic=syst
        )

        plot_sherpa_vs_madgraph(
            aeta_lj_2_5, "2J/aeta/%s"%syst,
            Cuts.mu*Cuts.final_jet(2),
            samples.values(), out_dir, recreate=args.recreate, legend_pos="top-left", nudge_x=-0.03, nudge_y=0, systematic=syst
        )
        plot_sherpa_vs_madgraph(
            aeta_lj_2_5, "2J0T/aeta/%s"%syst,
            Cuts.mu*Cuts.final(2,0),
            samples.values(), out_dir, recreate=args.recreate, legend_pos="top-left", nudge_x=-0.03, nudge_y=0, systematic=syst
        )
        plot_sherpa_vs_madgraph(
            aeta_lj_2_5, "2J1T/aeta/%s"%syst,
            Cuts.mu*Cuts.final(2,1),
            samples.values(), out_dir, recreate=args.recreate, legend_pos="top-left", nudge_x=-0.03, nudge_y=0, systematic=syst
        )
