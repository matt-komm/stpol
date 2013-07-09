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

    #This symlink is present in the repo for *.hep.kbfi.ee, if running on other machines, you must make it yourself by doing
    #ln -s /path/to/step3/out $STPOL_DIR/step3_latest
    #isolated files are by default in $STPOL_DIR/step3_latest/mu/iso/nominal/*.root
    datadirs["iso"] = "/".join((os.environ["STPOL_DIR"], "step3_latest", "mu" ,"iso", "nominal"))
    #Use the anti-isolated data for QCD $STPOL_DIR/step3_latest/mu/antiiso/nominal/SingleMu.root
    datadirs["antiiso"] = "/".join((os.environ["STPOL_DIR"], "step3_latest", "mu" ,"antiiso", "nominal"))

    #Load all the samples in the isolated directory
    samples = Sample.fromDirectory(datadirs["iso"], out_type="dict")
    samples["SingleMu_aiso"] = Sample.fromFile(datadirs["antiiso"] + "/SingleMu.root")

    hists_mc = dict()
    hist_data = None

    #Define the variable, cut, weight and lumi
    var = "cos_theta"
    cut_name = "2j1t"
    cut_str = str(Cuts.n_jets(2)*Cuts.n_tags(1)*Cuts.lepton_veto*Cuts.one_muon*Cuts.mt_mu*Cuts.top_mass_sig*Cuts.eta_lj)
    weight_str = "1.0"
    lumi = 20000 #FIXME: take from the step2 output filelists/step2/latest/iso/nominal/luminosity.txt

    #nbins, min, max
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

    #Combine the subsamples to physical processes
    merged_hists = merge_hists(hists_mc, merge_cmds).values()

    #Some printout
    for h in merged_hists + [hist_data]:
        print h.GetName(), h.GetTitle(), h.Integral()

    canv = ROOT.TCanvas()

    stacks_d = OrderedDict()
    stacks_d["mc"] = merged_hists
    stacks_d["data"] = [hist_data]
    stacks = plot_hists_stacked(canv, stacks_d)
    canv.Draw()

    #Create the dir if it doesn't exits
    try:
        os.mkdir("muon_out")
    except OSError:
        pass
    canv.SaveAs("muon_out/test.pdf")
