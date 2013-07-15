import ROOT
from plots.common.sample import Sample, load_samples, get_process_name
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
import pickle

import rootpy
import rootpy.io
import rootpy.io.utils
from rootpy.io.file import File
import sys

class HistMetaData:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
def filter_hists(indict, pat):
    """
    Returns the values of the dictionary whose keys match the pattern. The return type is a dictionary, whose keys are the first group of the pattern.
    filter_hists({"asd/mystuff":1}, ".*/(mystuff)") will return {"mystuff":1}
    indict - a dictionary
    pat - a regex pattern that has at least 1 parenthesized group
    """
    out = dict()
    for k,v in indict.items():
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

def draw_data_mc(var, plot_range, cut_str, weight_str, lumi, samples, histo_input_file):
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
        metadata["iso/%s" % sample.name] = md

        if sample.isMC:
            sample_weight_str = weight_str
            #FIXME
            if "sherpa" in sample.name:
                logging.debug("Sample %s: enabling gen_weight" % (sample.name))
                sample_weight_str += "*gen_weight"
            if "sherpa_nominal_reweighted" in sample.name:
                logging.debug("Sample %s: enabling wjets_flavour_weight" % (sample.name))
                sample_weight_str += "*wjets_flavour_weight"


            hist = sample.drawHistogram(var, cut_str, weight=sample_weight_str, plot_range=plot_range)
            hist.hist.Scale(sample.lumiScaleFactor(lumi)) 
            hn = "mc/iso/%s" % sample.name
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

    outdir ="/".join(histo_input_file.split("/")[:-1])
    mkdir_p(outdir)
    fi = File(histo_input_file, "RECREATE")
    for hn, h in hists.items():
        dirn = "/".join(hn.split("/")[:-1])
        fi.cd()
        try:
            d = fi.Get(dirn)
        except rootpy.io.DoesNotExist:
            d = rootpy.io.utils.mkdir(dirn, recurse=True)
        d.cd()
        h.SetName(hn.split("/")[-1])
        h.SetDirectory(d)

        md = metadata[hn]
        mdpath = outdir + "/" + hn.replace("/", "__") + ".pickle"
        pickle.dump(md, open(mdpath, "w"))
    fi.Write()
    fi.Close()

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

    tot_mc = get_stack_total_hist(stacks["mc"])
    tot_data = get_stack_total_hist(stacks["data"])
    r = plot_data_mc_ratio(
        canv,
        tot_data,
        tot_mc
    )

    chi2 = tot_data.Chi2Test(tot_mc, "UW CHI2/NDF")
    stacks["mc"].SetTitle(str(chi2))
    r[1].GetXaxis().SetTitle(x_title)
    canv.cd()

    logging.debug("Drawing legend")
    leg = legend(hists["data"] + hists["mc"], styles=["p", "f"], **kwargs)

    canv.SaveAs(out_dir + "/%s.png" % name)
    canv.Close() #Must close canvas to prevent hang in ROOT upon GC
    #del canv, stacks, r
    logging.debug("Returning from plot()")
    return

def is_mc(path):
    return path.split("/")[0] == "mc"

def plot_sherpa_vs_madgraph(var, cut_name, cut_str, samples, out_dir, histo_input_file=None, recreate=False, **kwargs):
    out_dir = out_dir + "/" + cut_name
    mkdir_p(out_dir)

    if recreate:
        logging.info("Drawing histograms for variable=%s, cut=%s" % (var["var"], cut_name))
        hists = draw_data_mc(
            var["var"], var["range"],
            cut_str,
            "pu_weight*muon_IDWeight*muon_TriggerWeight*muon_IsoWeight*b_weight_nominal", 19739, samples, histo_input_file
        )

    logging.info("Loading histograms from file %s" % histo_input_file)
    fi = File(histo_input_file)
    hists = {}
    for path, dirs, hnames in fi.walk():
        if len(hnames)>0:
            for hn in hnames:
                logging.debug("Getting %s" % (path + "/"  + hn))
                hname = path + "/" + hn
                hists[hname] = fi.Get(hname)
                md = pickle.load(open(cutname + "/" + hname.replace("/", "__") + ".pickle"))
                hists[hname] = md.hist_title
                process_name = md.sample_process_name
                if is_mc(hname):
                    Styling.mc_style(hists[hname], process_name)
                else:
                    Styling.data_style(hists[hname])

    hjoined = dict(filter_hists(hists, "mc/iso/(.*)"), **filter_hists(hists, "data/iso/(SingleMu)"))
    merges = dict()
    merges["madgraph"] = merge_cmds.copy()
    merges["sherpa"] = merge_cmds.copy()
    merges["sherpa_rew"] = merge_cmds.copy()
    merges["sherpa"]["WJets"] = ["WJets_sherpa_nominal"]
    merges["sherpa_rew"]["WJets"] = ["WJets_sherpa_nominal_reweighted"]
    hmerged = {k:merge_hists(hjoined, merges[k]) for k in merges.keys()}


    tot_sherpa = hmerged["sherpa_rew"]["WJets"].Integral()
    tot_madgraph = hmerged["madgraph"]["WJets"].Integral()

    logging.info("Unweighted sherpa sample norm: %.2f" %  hmerged["sherpa"]["WJets"].Integral())
    logging.info("Weighted sherpa sample norm: %.2f" %  hmerged["sherpa_rew"]["WJets"].Integral())
    hmerged["sherpa_rew"]["WJets"].Scale(tot_madgraph / tot_sherpa)
    logging.info("Scaled sherpa to madgraph: %.2f -> %.2f = %.2f" % (tot_sherpa, tot_madgraph, hmerged["sherpa_rew"]["WJets"].Integral()))
    kwargs = dict({"x_label": var["varname"]}, **kwargs)

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

    root_fname = out_dir + "/hists%s.root"%suffix
    logging.info("Saving to ROOT file: %s" % root_fname)

    ofi = ROOT.TFile(root_fname, "RECREATE")
    ofi.cd()

    for k, hists in hmerged.items():
        ofdir = ofi.mkdir(k)
        ofdir.cd()
        for name, hist in hists.items():
            hist.SetName(name)
            hist.SetDirectory(ofdir)
    ofi.Write()
    ofi.Close()

if __name__=="__main__":
    logging.basicConfig(level=logging.INFO)
    tdrstyle()
    ROOT.gStyle.SetOptTitle(True)

    import argparse

    parser = argparse.ArgumentParser(description='Draw WJets sherpa plots')
    parser.add_argument('--recreate', dest='recreate', action='store_true')
    args = parser.parse_args()

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

    # plot_sherpa_vs_madgraph(mu_pt, "2J0T", str(Cuts.final(2,0)), samples, out_dir, legend_pos="top-right")
    # plot_sherpa_vs_madgraph(mu_pt, "2J1T", str(Cuts.final(2,1)), samples, out_dir, legend_pos="top-right")

    # plot_sherpa_vs_madgraph(lj_pt, "2J0T", str(Cuts.final(2,0)), samples, out_dir, legend_pos="top-right")
    # plot_sherpa_vs_madgraph(lj_pt, "2J1T", str(Cuts.final(2,1)), samples, out_dir, legend_pos="top-right")

    # plot_sherpa_vs_madgraph(bj_pt, "2J0T", str(Cuts.final(2,0)), samples, out_dir, legend_pos="top-right")
    # plot_sherpa_vs_madgraph(bj_pt, "2J1T", str(Cuts.final(2,1)), samples, out_dir, legend_pos="top-right")

    # plot_sherpa_vs_madgraph(costheta, "2J0T", str(Cuts.final(2,0)), samples, out_dir, legend_pos="top-right")
    plot_sherpa_vs_madgraph(costheta, "2J1T", str(Cuts.final(2,1)), samples, out_dir, histo_input_file="2J1T/costheta.root", recreate=args.recreate, legend_pos="top-right")

    plot_sherpa_vs_madgraph(mtop, "2J0T", str(Cuts.final(2,0)), samples, out_dir, histo_input_file="2J0T/mtop.root", recreate=args.recreate, legend_pos="top-right")
    # plot_sherpa_vs_madgraph(mtop, "2J1T", str(Cuts.final(2,1)), samples, out_dir, histo_input_file="2J1T/mtop.root", recreate=args.recreate, legend_pos="top-right")
    # plot_sherpa_vs_madgraph(mtop, "2J1T", str(Cuts.final(2,1)), samples, out_dir, legend_pos="top-right")

    # plot_sherpa_vs_madgraph(eta_pos, "2J0T__eta_pos", str(Cuts.final(2,0)*Cut("eta_lj>0.0")), samples, out_dir, legend_pos="top-right")
    # plot_sherpa_vs_madgraph(eta_pos, "2J1T__eta_pos", str(Cuts.final(2,1)*Cut("eta_lj>0.0")), samples, out_dir, legend_pos="top-right")

    # plot_sherpa_vs_madgraph(eta_neg, "2J0T__eta_neg", str(Cuts.final(2,0)*Cut("eta_lj<0.0")), samples, out_dir, legend_pos="top-left")
    # plot_sherpa_vs_madgraph(eta_neg, "2J1T__eta_neg", str(Cuts.final(2,1)*Cut("eta_lj<0.0")), samples, out_dir, legend_pos="top-left")