import ROOT
from common.histogram import Histogram
from common.cross_sections import xs
from common.utils import get_sample_name

def get_eff_norm(tfile, flavour, proj, rebin=50):
    ROOT.gROOT.cd()
    sample_name = tfile.GetPath().split("/")[-2].split(".")[0]
    sample_entries = tfile.Get("trees/count_hist").GetBinContent(1)
    hi_true = tfile.Get("b_eff_hists/true_%s" % flavour).Clone()
    hi_tagged = tfile.Get("b_eff_hists/true_%s_tagged" % flavour).Clone()
    hi_true.Sumw2()
    hi_tagged.Sumw2()

    if proj=="x":
        hi_true = hi_true.ProjectionX()
        hi_tagged = hi_tagged.ProjectionX()
    elif proj=="y":
        hi_true = hi_true.ProjectionY()
        hi_tagged = hi_tagged.ProjectionY()
#    hi_true = Histogram.make(hi_true, sample_name=sample_name, sample_entries_total=sample_entries)
#    hi_tagged = Histogram.make(hi_tagged, sample_name=sample_name, sample_entries_total=sample_entries)

#    hi_true.normalize_lumi(1.0)
#    hi_tagged.normalize_lumi(1.0)

#    return (hi_true.hist, hi_tagged.hist)
    return (hi_true, hi_tagged)

def get_eff_merged(samples, flavour, proj="x"):
    hists = [get_eff_norm(sample, flavour, proj) for sample in samples]

    xs_s = [xs[get_sample_name(sample)] for sample in samples]
    #print xs_s

    n_true = hists[0][0]
    n_tagged = hists[0][1]
    n_true.Scale(xs_s[0])
    n_tagged.Scale(xs_s[0])
    for (h_true, h_tagged), _xs in zip(hists[1:], xs_s[1:]):
        #print "int_true=%.2f, int_tagged=%.2f" % (n_true.Integral(), n_tagged.Integral())
        n_true.Add(h_true, _xs)
        n_tagged.Add(h_tagged, _xs)

    n_true.Scale(1.0/sum(xs_s))
    n_tagged.Scale(1.0/sum(xs_s))

    #print "int_true=%.2f, int_tagged=%.2f" % (n_true.Integral(), n_tagged.Integral())
    div = n_tagged.Clone("eff_%s" % flavour)
    div.Divide(n_true)
    #print "div=%.2f" % div.Integral()
    return div
