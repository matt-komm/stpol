import ROOT
from common.histogram import Histogram
from common.cross_sections import xs
from common.utils import get_sample_name
import numpy
from common.odict import OrderedDict as dict

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

if __name__=="__main__":
    from glob import glob
    from common.utils import get_sample_dict
    import os
    import sys

    samples_d = dict()
    samples_d["ttbar"] = ["TTJets_FullLept", "TTJets_SemiLept"]
    samples_d["wjets"] = ["W1Jets_exclusive", "W2Jets_exclusive", "W3Jets_exclusive", "W4Jets_exclusive"]
    samples_d["t-channel"] = ["T_t_ToLeptons", "Tbar_t_ToLeptons"]

    sample_name = sys.argv[1]
    out_dir = "b_eff_plots/"
    import os
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)
    axis = sys.argv[2]
    if axis == "x":
        xlab = "p_{T,q}"
    elif axis == "y":
        xlab = "|#eta_{q}|"
    else:
        raise ValueError("axis must be x or y: axis=%s" % axis)

    cutregions = glob("data/out_b_effs_bak/*/*")
    cutregions = filter(os.path.isdir, cutregions)
    cutregions_mu = sorted(filter(lambda x: "mu" in x, cutregions))
    cutregions_ele = sorted(filter(lambda x: "ele" in x, cutregions))
    cutregions = cutregions_mu + cutregions_ele
    print cutregions
    hists = dict()
    hists_2d = dict()
    for cut in cutregions:
        print cut
        samples = get_sample_dict(cut, samples_d)
        effs = {f: get_eff_merged(samples[sample_name], f, proj=axis) for f in ["b", "c", "l"]}
        effs_2d = {f: get_eff_merged(samples[sample_name], f, proj=None) for f in ["b", "c", "l"]}
        cutn = "/".join(cut.split("/")[-2:])
        print cutn
        hists[cutn] = effs
        hists_2d[cutn] = effs_2d
        for f, h in effs.items():
            h.SetTitle(cutn + " eff(%s)" % f)

    chis = []
    chiarr = numpy.zeros((len(hists.keys()), len(hists.keys())))
    i = 0
    for k1 in hists.keys():
        j = 0
        for k2 in hists.keys():
            effs1 = hists_2d[k1]
            effs2 = hists_2d[k2]
            chi = effs1["b"].Chi2Test(effs2["b"], "WW CHI2/NDF")
            chiarr[i,j] = chi
            j += 1
        i += 1

    pairs = [
        ("3J_nocut/mu", "3J_nocut/ele"),
        ("3J_nocut/mu", "3J_mtw/mu"),
        ("3J_nocut/mu", "3J_met/ele"),
        ("3J_nocut/mu", "3J_mtw_mtop/mu"),
        ("3J_mtw_mtop/mu", "3J_mtw_mtop_etalj/mu"),
    ]

    for a,b in pairs:
        i = hists.keys().index(a)
        j = hists.keys().index(b)
        print a,b, chiarr[i,j]

    from matplotlib import pyplot as plt
    im = plt.imshow(chiarr, interpolation="nearest", cmap="hot")
    plt.colorbar(im)
    plt.xticks(range(len(hists.keys())), hists.keys(), rotation=90)
    plt.yticks(range(len(hists.keys())), hists.keys())
    plt.savefig(out_dir + "b_effs_2d_chi2_%s.pdf" % (sample_name), dpi=500, bbox_inches='tight', pad_inches=0.5)

    from common.hist_plots import plot_hists
    from common.sample_style import ColorStyleGen
    from common.legend import legend
    from common.tdrstyle import tdrstyle
    tdrstyle()

    hnames = dict()
    hnames["mu"] = "nocut", "mtw", "mtw_mtop", "mtw_mtop_etalj"
    hnames["ele"] = "nocut", "met", "met_mtop", "met_mtop_etalj"

    for flavour in ["b", "c", "l"]:
        hi = hists["3J_nocut/mu"], hists["3J_nocut/ele"],  hists["3J_mtw/mu"], hists["3J_met/ele"]
        hi = map(lambda x: x[flavour], hi)
        ColorStyleGen.style_hists(hi)
        canv = plot_hists(hi, x_label=xlab, y_label="eff_{%s}" % flavour)
        leg = legend(hi, styles=(len(hi)*["f"]), pos="top-left")
        canv.SaveAs(out_dir + "/3J_mu_ele_nocut_mtw_proj_%s_eff_%s_sample_%s.pdf" % (axis, flavour, sample_name))

        hi = hists["3J_mtw/mu"], hists["3J_met/ele"],  hists["3J_mtw_mtop/mu"], hists["3J_met_mtop/ele"]
        hi = map(lambda x: x[flavour], hi)
        ColorStyleGen.style_hists(hi)
        canv = plot_hists(hi, x_label=xlab, y_label="eff_{%s}" % flavour)
        leg = legend(hi, styles=(len(hi)*["f"]), pos="top-left")
        canv.SaveAs(out_dir + "/3J_mu_ele_mtw_mtop_proj_%s_eff_%s_sample_%s.pdf" % (axis, flavour, sample_name))

    for nJets in [2,3]:
        for flavour in ["b", "c", "l"]:
            for lep in ["mu", "ele"]:
                bases = "%dJ_" % nJets

                hi = map(lambda x: x[flavour],
                    [hists[bases + hn + "/" + lep] for hn in hnames[lep]]
                )

                ColorStyleGen.style_hists(hi)
                canv = plot_hists(hi, x_label=xlab, y_label="eff_{%s}" % flavour)
                leg = legend(hi, styles=(len(hi)*["f"]), pos="top-left")

                plotname = out_dir + "/" + "effs_proj_%s_cut_comp_eff_%s_lep_%s_nJ_%d_sample_%s.pdf" % (axis, flavour, lep, nJets, sample_name)
                canv.SaveAs(plotname)

