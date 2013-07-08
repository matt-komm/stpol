import sys
import os
import copy
sys.path.append(os.environ["STPOL_DIR"])

import plots
import plots.common
from plots.common.odict import OrderedDict as dict
from plots.common.sample import Sample
from plots.common.cuts import Cuts, Cut
from plots.common.utils import merge_cmds, merge_hists, get_hist_int_err

lumi_total=19739
sample_dir = "data/out_step3_05_30_08_20"

samples = []
samples.append(Sample.fromFile(sample_dir + "/TTJets_MassiveBinDECAY.root"))
samples.append(Sample.fromFile(sample_dir + "/TTJets_FullLept.root"))
samples.append(Sample.fromFile(sample_dir + "/TTJets_SemiLept.root"))
samples.append(Sample.fromFile(sample_dir + "/T_t.root"))
samples.append(Sample.fromFile(sample_dir + "/Tbar_t.root"))
samples.append(Sample.fromFile(sample_dir + "/T_t_ToLeptons.root"))
samples.append(Sample.fromFile(sample_dir + "/Tbar_t_ToLeptons.root"))
#samples.append(Sample.fromFile(sample_dir + "/QCDMu.root"))
samples.append(Sample.fromFile(sample_dir + "/WJets_inclusive.root"))
samples.append(Sample.fromFile(sample_dir + "/W1Jets_exclusive.root"))
samples.append(Sample.fromFile(sample_dir + "/W2Jets_exclusive.root"))
samples.append(Sample.fromFile(sample_dir + "/W3Jets_exclusive.root"))
samples.append(Sample.fromFile(sample_dir + "/W4Jets_exclusive.root"))

samples_data = []
samples_data.append(Sample.fromFile(sample_dir + "/SingleMu.root"))

def mc_amount(cut, weight, lumi=lumi_total, ref=None):
    histsD = dict()
    for samp in samples:
        histsD[samp.name] = samp.drawHistogram("mu_pt", str(cut), dtype="float", weight=weight, plot_range=[100, 0, 100000000])

    for name, hist in histsD.items():
        hist.normalize_lumi(lumi)
    for name, hist in histsD.items():
        histsD[name] = hist.hist
    merge_cmd = dict()
    #merge_cmd["QCD (MC)"] = ["QCDMu"]
    merge_cmd["t-channel incl"] = ["T_t", "Tbar_t"]
    merge_cmd["t-channel excl"] = ["T_t_ToLeptons", "Tbar_t_ToLeptons"]
    merge_cmd["t#bar{t} incl"] = ["TTJets_MassiveBinDECAY"]
    merge_cmd["t#bar{t} excl"] = ["TTJets_FullLept", "TTJets_SemiLept"]
    merge_cmd["WJets incl"] = ["WJets_inclusive"]
    merge_cmd["WJets excl"] = ["W1Jets_exclusive", "W2Jets_exclusive", "W3Jets_exclusive", "W4Jets_exclusive"]
    merged_hists = merge_hists(histsD, merge_cmd)
    merged_hists["data"] = samples_data[0].drawHistogram("mu_pt", str(cut), dtype="float", weight="1.0", plot_range=[100,0,100000000]).hist

    normd = dict()
    for hn, h in merged_hists.items():
        normd[hn] = get_hist_int_err(h)
    return merged_hists, normd


if __name__=="__main__":
    cutsref = [
        ("final_2J0T", Cuts.mu*Cuts.final(2,0), "1.0"),
        ("final_2J0T_weighted", Cuts.mu*Cuts.final(2,0), "pu_weight*muon_IDWeight*muon_IsoWeight*muon_TriggerWeight*b_weight_nominal")
    ]

    for (name, cut, weight) in cutsref:
        hist, norms = mc_amount(cut, weight)
        print 80*"-"
        print name
        print "cut=",str(cut)
        print "weight=",str(weight)
        print "data | %d " % (norms["data"][0])
        print "t-channel incl | %d " % (norms["t-channel incl"][0])
        print "t-channel excl | %d " % (norms["t-channel excl"][0])
        print "Wjets incl | %d " % (norms["WJets incl"][0])
        print "Wjets excl | %d " % (norms["WJets excl"][0])
        print "ttbar incl | %d " % (norms["t#bar{t} incl"][0])
        print "ttbar excl | %d " % (norms["t#bar{t} excl"][0])
