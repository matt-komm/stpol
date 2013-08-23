#!/usr/bin/env python
import rootpy
rootpy.log.basic_config_colorized()
from plots.common.sample import Sample
from plots.common.cuts import Cuts

lumi = 20000
def project(samp, cut):
    s = Sample.fromFile(samp)
    hi1 = s.drawHistogram(
        "cos_theta", str(
            cut
        ),
        binning=[20, -1, 1]
    ).Clone()
    hi = hi1.Clone()
    hi.Scale(s.lumiScaleFactor(lumi))
    hi.Integral()
    return hi1, hi

lep = "mu"
b = "/hdfs/local/stpol/step3/Jul26_MVA_multivar_v1/%s/mc/iso/nominal/Jul15/" % lep
wjets_sampls = [
    b + "W1Jets_exclusive.root",
    b + "W2Jets_exclusive.root",
    b + "W3Jets_exclusive.root",
    b + "W4Jets_exclusive.root"
]

baseline = Cuts.rms_lj * Cuts.lepton(lep) * Cuts.hlt(lep) * Cuts.metmt(lep) * Cuts.n_jets(2) * Cuts.n_tags(1)

wjets_cutbased = [project(s, baseline * Cuts.final(2,1)) for s in wjets_sampls]
wjets_mva = [project(s, baseline * Cuts.mva_wp(lep)) for s in wjets_sampls]

print "CB", str(Cuts.final(2,1))
print "MVA", str(Cuts.mva_wp(lep))
print sum([w[1].Integral() for w in wjets_cutbased]), sum([w[1].Integral() for w in wjets_mva])
