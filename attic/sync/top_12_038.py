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

lumi_total=12210
sample_dir = "data/out_step3_05_30_08_20"

samples = []
samples.append(Sample.fromFile(sample_dir + "/TTJets_MassiveBinDECAY.root"))
samples.append(Sample.fromFile(sample_dir + "/TTJets_FullLept.root"))
samples.append(Sample.fromFile(sample_dir + "/TTJets_SemiLept.root"))
samples.append(Sample.fromFile(sample_dir + "/T_t.root"))
samples.append(Sample.fromFile(sample_dir + "/Tbar_t.root"))
samples.append(Sample.fromFile(sample_dir + "/T_t_ToLeptons.root"))
samples.append(Sample.fromFile(sample_dir + "/Tbar_t_ToLeptons.root"))
samples.append(Sample.fromFile(sample_dir + "/QCDMu.root"))
samples.append(Sample.fromFile(sample_dir + "/WJets_inclusive.root"))
samples.append(Sample.fromFile(sample_dir + "/W1Jets_exclusive.root"))
samples.append(Sample.fromFile(sample_dir + "/W2Jets_exclusive.root"))
samples.append(Sample.fromFile(sample_dir + "/W3Jets_exclusive.root"))
samples.append(Sample.fromFile(sample_dir + "/W4Jets_exclusive.root"))

def mc_amount(cut, weight, lumi=12210, ref=None):
    histsD = dict()
    for samp in samples:
        histsD[samp.name] = samp.drawHistogram("mu_pt", str(cut), dtype="float", weight=weight, plot_range=[100, 0, 100000000])
        histsD[samp.name].Scale(samp.lumiScaleFactor(lumi))
        
    merge_cmd = dict()
    merge_cmd["t-channel incl"] = ["T_t", "Tbar_t"]
    merge_cmd["t-channel excl"] = ["T_t_ToLeptons", "Tbar_t_ToLeptons"]
    merge_cmd["t#bar{t} excl"] = ["TTJets_FullLept", "TTJets_SemiLept"]
    merge_cmd["QCD (MC)"] = ["QCDMu"]
    merge_cmd["t#bar{t} incl"] = ["TTJets_MassiveBinDECAY"]
    merge_cmd["WJets incl"] = ["WJets_inclusive"]
    merge_cmd["WJets excl"] = ["W1Jets_exclusive", "W2Jets_exclusive", "W3Jets_exclusive", "W4Jets_exclusive"]
    merged_hists = merge_hists(histsD, merge_cmd)

    normd = dict()
    for hn, h in merged_hists.items():
        normd[hn] = get_hist_int_err(h)
    return merged_hists, normd


if __name__=="__main__":
    #cut = Cuts.mu * Cuts.n_jets(2) * Cuts.mt_mu * Cuts.top_mass_sig * Cuts.eta_lj * Cuts.n_tags(1)
    cut = Cuts.mu * Cuts.final(2,1)

    cutsref = [
        ("1mu", Cuts.mu, (5879691, 268238, 50236)),
        ("2J", Cuts.mu*Cuts.n_jets(2), (972069, 75674, 22387)),
        ("met", Cuts.mu*Cuts.n_jets(2)*Cut("met>45"), (404707, 46185, 11052)),
        ("0T", Cuts.mu*Cuts.n_jets(2)*Cut("met>45")*Cuts.n_tags(0), (-1, -1, -1)),
        ("rmslj_0T", Cuts.mu*Cuts.n_jets(2)*Cut("met>45")*Cuts.n_tags(0)*Cuts.rms_lj, (-1, -1, -1)),
        ("1T", Cuts.mu*Cuts.n_jets(2)*Cut("met>45")*Cuts.n_tags(1), (6197, 17505, 4173)),
        ("rmslj_1T", Cuts.mu*Cuts.n_jets(2)*Cut("met>45")*Cuts.n_tags(1)*Cuts.rms_lj, (5095, 14197, 3664)),
    ]

    for (name, cut, (refW, refTT, refT)) in cutsref:
        #hist, norms = mc_amount(cut, "pu_weight*muon_IDWeight*muon_IsoWeight")
        hist, norms = mc_amount(cut, "1.0")
        print 80*"-"
        print name
        print "t-channel | %d | %d | %d " % (norms["t-channel incl"][0], norms["t-channel excl"][0], refT)
        print "Wjets | %d | %d | %d " % (norms["WJets incl"][0], norms["WJets excl"][0], refW)
        print "ttbar | %d | %d | %d " % (norms["t#bar{t} incl"][0], norms["t#bar{t} excl"][0], refTT)
