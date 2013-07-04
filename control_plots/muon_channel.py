#!/usr/bin/env python
#run as ./muon_channel.py -b to skip visual output
import sys
import os

##Need to add parent dir to python path to import plots
#try:
#    sys.path.append(os.environ["STPOL_DIR"] )
#except KeyError:
#    print "Could not find the STPOL_DIR environment variable, dod you run `source setenv.sh` in the code base directory?"
#    sys.exit(1)

import ROOT
import plots
from plots.common.stack_plot import plot_hists_stacked
from plots.common.odict import OrderedDict
from plots.common.sample import Sample
from plots.common.cuts import Cuts
from plots.common.sample_style import Styling
import plots.common.pretty_names as pretty_names
from plots.common.utils import merge_cmds, merge_hists
import random

if __name__=="__main__":
    #import plots.common.tdrstyle as tdrstyle
    #tdrstyle.tdrstyle()

    datadirs = dict()
    datadirs["iso"] = "/".join((os.environ["STPOL_DIR"], "step3_latest", "mu" ,"iso", "nominal"))
    datadirs["antiiso"] = "/".join((os.environ["STPOL_DIR"], "step3_latest", "mu" ,"antiiso", "nominal"))

    samples = Sample.fromDirectory(datadirs["iso"], out_type="dict")
    samples["SingleMu_aiso"] = Sample.fromFile(datadirs["antiiso"] + "/SingleMu.root")
    
    hists_mc = dict()
    hist_data = None
    var = "cos_theta"
    cut_name = "2j1t"
    cut_str = str(Cuts.n_jets(2)*Cuts.n_tags(1)*Cuts.lepton_veto*Cuts.one_muon*Cuts.mt_mu*Cuts.top_mass_sig*Cuts.eta_lj)
    weight_str = "1.0"
    lumi = 20000
    plot_range= [20, -1, 1]
    
    for name, sample in samples.items():
        if sample.isMC:
            hist = sample.drawHistogram(var, cut_str, weight=weight_str, plot_range=plot_range)
            hist.normalize_lumi(lumi)
            hists_mc[sample.name] = hist.hist
            Styling.mc_style(hists_mc[sample.name], sample.name)
        elif name == "SingleMu":
            hist_data = sample.drawHistogram(var, cut_str, weight="1.0", plot_range=plot_range).hist
            Styling.data_style(hist_data)

        elif name == "SingleMu_aiso":
            hist_qcd = sample.drawHistogram(var, cut_str, weight="1.0", plot_range=plot_range).hist
            #hist_qcd.
            pass

    merged_hists = merge_hists(hists_mc, merge_cmds).values()
    for h in merged_hists + [hist_data]:
        print h.GetName(), h.GetTitle(), h.Integral()

    canv = ROOT.TCanvas()

    stacks_d = OrderedDict()
    stacks_d["mc"] = merged_hists
    stacks_d["data"] = [hist_data]
    stacks = plot_hists_stacked(canv, stacks_d)
    canv.Draw()

    try:
        os.mkdir("muon_out")
    except OSError:
        pass
    canv.SaveAs("muon_out/test.pdf")
