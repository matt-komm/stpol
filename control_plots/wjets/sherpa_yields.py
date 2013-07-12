import ROOT
from plots.common.sample import Sample, load_samples
from plots.common.sample_style import Styling
from plots.common.utils import merge_cmds, merge_hists, mkdir_p, get_stack_total_hist
from plots.common.odict import OrderedDict
from plots.common.stack_plot import plot_hists_stacked
from plots.common.cuts import Cuts, Cut
from plots.common.cross_sections import xs as cross_sections
from plots.common.legend import legend
from plots.common.tdrstyle import tdrstyle

import os
import re
import logging

def filter_hists(hists, pat):
    out = dict()
    for k,v in hists.items():
        m = re.match(pat, k)
        if not m:
            continue
        out[m.group(1)] = v
    return out

def plot_data_mc_ratio(canv, hist_data, hist_mc, height=0.3):
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

    hist_data.SetName("merged_data")
    hist_mc.SetName("merged_mc")
    hist_mc.Add(hist_data, -1.0)
    hist_mc.Divide(hist_data)

    hist_ratio = hist_mc

    hist_ratio.SetStats(False)
    hist_ratio.SetMarkerStyle(23)
    hist_ratio.SetTitle("ratio (exp.-meas.)/meas.")
    hist_ratio.SetTitleSize(0.08)
    hist_ratio.SetTitleOffset(-1)

    xAxis = hist_ratio.GetXaxis()
    yAxis = hist_ratio.GetYaxis()
    hist_ratio.SetMarkerStyle(20)
    yAxis.CenterTitle()

    xAxis.SetLabelSize(0.08)
    xAxis.SetTitleSize(0.15)
    xAxis.SetTitleOffset(0.5)
    yAxis.SetLabelSize(0.08)

    #xAxis.SetTickLength(xAxis->GetTickLength() * (1. - 2. * margin - bottomSpacing) / bottomSpacing);
    #xAxis.SetNdivisions(histStack.GetXaxis().GetNdivisions());
    yAxis.SetNdivisions(405)
    hist_ratio.Draw("p0e1")

    return p2, hist_ratio

def draw_data_mc(var, plot_range, cut_str, weight_str, lumi, samples):

    hists = dict()
    for name, sample in samples.items():
        if sample.isMC:
            sample_weight_str = weight_str
            #FIXME
            if "sherpa" in sample.name:
                sample_weight_str += "*gen_weight"

            hist = sample.drawHistogram(var, cut_str, weight=sample_weight_str, plot_range=plot_range)
            hist.normalize_lumi(lumi)

            Styling.mc_style(hist.hist, sample.name)
            hists["mc/iso/%s" % sample.name] = hist.hist
        elif name == "iso/SingleMu":
            hist_data = sample.drawHistogram(var, cut_str, weight="1.0", plot_range=plot_range).hist
            Styling.data_style(hist_data)
            hists["data/iso/%s" % sample.name] = hist_data

        elif name == "antiiso/SingleMu":
            hist_qcd = sample.drawHistogram(var, cut_str, weight="1.0", plot_range=plot_range).hist
            hists["data/antiiso/%s" % sample.name] = hist_qcd
    return hists

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
    r = plot_data_mc_ratio(
        canv,
        get_stack_total_hist(stacks["data"]),
        get_stack_total_hist(stacks["mc"])
    )

    r[1].GetXaxis().SetTitle(x_title)
    canv.cd()

    logging.debug("Drawing legend")
    leg = legend(hists["data"] + hists["mc"], styles=["p", "f"], **kwargs)

    canv.SaveAs(out_dir + "/%s.png" % name)
    canv.Close() #Must close canvas to prevent hang in ROOT upon GC
    #del canv, stacks, r
    logging.debug("Returning from plot()")
    return


def plot_sherpa_vs_madgraph(var, cut_name, cut_str, samples, out_dir, **kwargs):
    out_dir = out_dir + "/" + cut_name
    mkdir_p(out_dir)

    logging.info("Drawing histograms for variable=%s, cut=%s" % (var["var"], cut_name))
    hists = draw_data_mc(
        var["var"], var["range"],
        cut_str,
        "pu_weight*muon_IDWeight*muon_TriggerWeight*muon_IsoWeight*b_weight_nominal", 19739, samples
    )

    hjoined = dict(filter_hists(hists, "mc/iso/(.*)"), **filter_hists(hists, "data/iso/(SingleMu)"))
    merges = dict()
    merges["madgraph"] = merge_cmds.copy()
    merges["sherpa"] = merge_cmds.copy()
    merges["sherpa"]["WJets"] = ["WJets_sherpa_nominal"]
    hists_merged1 = merge_hists(hjoined, merges["madgraph"])
    hists_merged2 = merge_hists(hjoined, merges["sherpa"])

    kwargs = dict({"x_label": var["varname"]}, **kwargs)

    logging.info("Drawing sherpa plot")
    canv = ROOT.TCanvas("c1", "c1")
    suffix = "__%s__%s" % (var["var"], cut_name)
    plot(canv, "sherpa"+suffix, hists_merged2, out_dir, **kwargs)

    logging.info("Drawing madgraph plot")
    canv = ROOT.TCanvas("c2", "c2")
    plot(canv, "madgraph"+suffix, hists_merged1, out_dir, **kwargs)

    root_fname = out_dir + "/hists%s.root"%suffix
    logging.info("Saving to ROOT file: %s" % root_fname)

    ofi = ROOT.TFile(root_fname, "RECREATE")
    ofi.cd()
    madgraph_dir = ofi.mkdir("madgraph")
    sherpa_dir = ofi.mkdir("sherpa")

    sherpa_dir.cd()
    for n, h in hists_merged1.items():
        h.SetDirectory(sherpa_dir)
        h.SetName(n)
        #h.Write()
    madgraph_dir.cd()
    for n, h in hists_merged2.items():
        h.SetDirectory(madgraph_dir)
        h.SetName(n)
        #h.Write()
    ofi.Write()
    ofi.Close()

if __name__=="__main__":
    logging.basicConfig(level=logging.INFO)
    tdrstyle()
    ROOT.gStyle.SetOptTitle(True)


    samples = load_samples(os.environ["STPOL_DIR"])
   
    out_dir = os.environ["STPOL_DIR"] + "/out/plots/wjets"
    mkdir_p(out_dir)

    costheta = {"var":"cos_theta", "varname":"cos #theta", "range":[20,-1,1]}
    mtop = {"var":"top_mass", "varname":"M_{bl#nu}", "range":[20, 130, 220]}
    mu_pt = {"var":"mu_pt", "varname":"p_{t,#mu}", "range":[20, 30, 220]}
    lj_pt = {"var":"pt_lj", "varname":"p_{t,q}", "range":[20, 30, 150]}
    bj_pt = {"var":"pt_bj", "varname":"p_{t,b}", "range":[20, 30, 150]}
    eta_pos = {"var":"eta_lj", "varname":"#eta_{lq}", "range":[20, 2.5, 5.0]}
    eta_neg = {"var":"eta_lj", "varname":"#eta_{lq}", "range":[20, -5.0, -2.5]}

    plot_sherpa_vs_madgraph(mu_pt, "2J0T", str(Cuts.final(2,0)), samples, out_dir, legend_pos="top-right")
    plot_sherpa_vs_madgraph(mu_pt, "2J1T", str(Cuts.final(2,1)), samples, out_dir, legend_pos="top-right")

    plot_sherpa_vs_madgraph(lj_pt, "2J0T", str(Cuts.final(2,0)), samples, out_dir, legend_pos="top-right")
    plot_sherpa_vs_madgraph(lj_pt, "2J1T", str(Cuts.final(2,1)), samples, out_dir, legend_pos="top-right")

    plot_sherpa_vs_madgraph(bj_pt, "2J0T", str(Cuts.final(2,0)), samples, out_dir, legend_pos="top-right")
    plot_sherpa_vs_madgraph(bj_pt, "2J1T", str(Cuts.final(2,1)), samples, out_dir, legend_pos="top-right")

    plot_sherpa_vs_madgraph(costheta, "2J0T", str(Cuts.final(2,0)), samples, out_dir, legend_pos="top-right")
    plot_sherpa_vs_madgraph(costheta, "2J1T", str(Cuts.final(2,1)), samples, out_dir, legend_pos="top-right")

    plot_sherpa_vs_madgraph(mtop, "2J0T", str(Cuts.final(2,0)), samples, out_dir, legend_pos="top-right")
    plot_sherpa_vs_madgraph(mtop, "2J1T", str(Cuts.final(2,1)), samples, out_dir, legend_pos="top-right")

    plot_sherpa_vs_madgraph(eta_pos, "2J0T__eta_pos", str(Cuts.final(2,0)*Cut("eta_lj>0.0")), samples, out_dir, legend_pos="top-right")
    plot_sherpa_vs_madgraph(eta_pos, "2J1T__eta_pos", str(Cuts.final(2,1)*Cut("eta_lj>0.0")), samples, out_dir, legend_pos="top-right")

    plot_sherpa_vs_madgraph(eta_neg, "2J0T__eta_neg", str(Cuts.final(2,0)*Cut("eta_lj<0.0")), samples, out_dir, legend_pos="top-left")
    plot_sherpa_vs_madgraph(eta_neg, "2J1T__eta_neg", str(Cuts.final(2,1)*Cut("eta_lj<0.0")), samples, out_dir, legend_pos="top-left")