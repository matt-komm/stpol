#!/bin/env python
import sys, os
import ROOT
from plots.common.cuts import Cuts
from plots.common.sample import Sample
from plots.common.utils import merge_cmds, merge_hists
from plots.common.cross_sections import lumis
from plots.common.cuts import Weights

lepton_channel = "ele"
lumi = lumis["343e0a9_Aug22"]["iso"][lepton_channel]

#step3 = "/hdfs/local/stpol/step3/Jul25"
step3 = "/hdfs/local/stpol/step3/37acf5_343e0a9_Aug22"

print "Starting " + lepton_channel + "-channel"
indir_mc = "/".join((step3, lepton_channel,"mc","iso","nominal","Jul15"))
samples_mc = Sample.fromDirectory(indir_mc)
    
indir_data = "/".join((step3, lepton_channel,"data","iso","Jul15"))
samples_data = Sample.fromDirectory(indir_data)

if lepton_channel == "mu":
    iso = "mu_iso"
    plot_range = [0.0,0.015,0.05,0.12]
    cut_lepton = Cuts.one_muon
    cut_hlt = Cuts.hlt_isomu
if lepton_channel == "ele":
    iso = "el_iso"
    plot_range = [0,0.015,0.05,0.1]
    cut_lepton = Cuts.one_electron
    cut_hlt = Cuts.hlt_isoele


cut_w = cut_hlt*cut_lepton*Cuts.n_jets(3)*Cuts.n_tags(2)*Cuts.lepton_veto*Cuts.deltaR(0.3)*Cuts.rms_lj*Cuts.metmt(lepton_channel)
cut_str = str(cut_w)
weight_str = str(Weights.total(lepton_channel)
                 * Weights.wjets_madgraph_shape_weight()
                 * Weights.wjets_madgraph_flat_weight())

print "Opening input data trees from: " + indir_data
hists_data = {}
data_sample_names = []

for name, sample in samples_data.items():
    if name[0:6] == "Single":
        print "Starting:", name
        hists_data[sample.name] = sample.drawHistogram(iso, cut_str, weight="1.0", binning=plot_range)
        data_sample_names.append(sample.name)

for it in range(len(data_sample_names)):
    if it == 0:
        hist_data = hists_data[data_sample_names[it]].Clone("hist_data") #add data trees together
    else:
        hist_data.add(hists_data[data_sample_names[it]])

print "Opening input MC trees from: " + indir_mc
hists_mc = {}

for name, sample in samples_mc.items():
    if name[0:6] != "Single":
        print "Starting:", name
        hist = sample.drawHistogram(iso, cut_str, weight=weight_str, binning=plot_range)
        hist.Scale(sample.lumiScaleFactor(lumi))
        hists_mc[sample.name] = hist
        
merged_hists = merge_hists(hists_mc, merge_cmds).values()
htot_mc = sum(merged_hists)

h_weight = hist_data.clone("h_weight_"+"lepton_channel")
for iBin in range(1, htot_mc.GetSize()-1):
    iso_weight = hist_data.GetBinContent(iBin)/htot_mc.GetBinContent(iBin)
    h_weight.SetBinContent(iBin,iso_weight)
    print "Lepton channel: " + lepton_channel 
    print "iso_weight = " + str(iso_weight) + ", bin nr " + str(iBin)


outdir = "weight_hists"
# Check if outdir exists
if not os.path.exists(outdir):
    os.makedirs(outdir)
        
outfilename = outdir + "/iso_weight_" + lepton_channel + ".root"
out = ROOT.TFile(outfilename,"RECREATE")
h_weight.Write()

out.Close()
