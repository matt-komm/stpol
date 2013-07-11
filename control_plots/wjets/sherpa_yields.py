import ROOT
from plots.common.sample import Sample, load_samples
from plots.common.sample_style import Styling
from plots.common.utils import merge_cmds, merge_hists, mkdir_p, get_stack_total_hist
from plots.common.odict import OrderedDict
from plots.common.stack_plot import plot_hists_stacked
from plots.common.cuts import Cuts
from plots.common.cross_sections import xs as cross_sections
from plots.common.legend import legend
from plots.common.tdrstyle import tdrstyle

import os
import re

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

def plot(canv, name, hists_merged, **kwargs):
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

    stacks = plot_hists_stacked(canv, hists, **kwargs)
    stacks["data"].GetXaxis().SetLabelOffset(999.)
    stacks["data"].GetXaxis().SetTitleOffset(999.)
    r = plot_data_mc_ratio(
        canv,
        get_stack_total_hist(stacks["data"]),
        get_stack_total_hist(stacks["mc"])
    )
    
    r[1].GetXaxis().SetTitle(x_title)
    canv.cd()
    leg = legend(hists["data"] + hists["mc"], pos="top-left", styles=["p", "f"], **kwargs)

    return r, stacks, leg

if __name__=="__main__":
    tdrstyle()
    
    samples = load_samples(os.environ["STPOL_DIR"])
    hists = draw_data_mc(
        "cos_theta", [20, -1, 1],
        str(Cuts.final(2,0)),
        "pu_weight*muon_IDWeight*muon_TriggerWeight*muon_IsoWeight*b_weight_nominal", 19739, samples
    )
    
    out_dir = os.environ["STPOL_DIR"] + "/out/plots/wjets"
    mkdir_p(out_dir)
    
    hjoined = dict(filter_hists(hists, "mc/iso/(.*)"), **filter_hists(hists, "data/iso/(SingleMu)"))
    merges = dict()
    merges["default"] = merge_cmds.copy()
    merges["sherpa"] = merge_cmds.copy()
    merges["sherpa"]["WJets"] = ["WJets_sherpa_nominal"]
    hists_merged1 = merge_hists(hjoined, merges["default"])
    hists_merged2 = merge_hists(hjoined, merges["sherpa"])

    kwargs = {"x_label": "cos #theta", "nudge_x": -0.05}
    #A = plot("madgraph (exclusive) 2J0T", hists_merged1, **kwargs)
    canv = ROOT.TCanvas("c1", "sherpa (inclusive) 2J0T")
    x = plot(canv, "sherpa (inclusive) 2J0T", hists_merged2, **kwargs)
    canv.SaveAs(out_dir + "/sherpa_2J0T.png")

    canv = ROOT.TCanvas("c2", "madgraph (exclusive) 2J0T")
    x = plot(canv, "madgraph (exclusive) 2J0T", hists_merged1, **kwargs)
    canv.SaveAs(out_dir + "/madgraph_2J0T.png")
    
    
