from rootpy.io import File
from plots.common.sample_style import Styling
from plots.common.stack_plot import plot_hists_stacked
from plots.common.legend import legend
from plots.common.odict import OrderedDict
from plots.common.tdrstyle import tdrstyle
from plots.common.hist_plots import plot_data_mc_ratio
from plots.common.utils import get_stack_total_hist
from plots.common.output import OutputFolder
from plots.common.metainfo import PlotMetaInfo
import ROOT
#from final_fit.final_fit import SIGNAL
SIGNAL = "tchan"

#Plot the fit before and after
def plot_fit(fit, infile, outfile, result):
    tdrstyle()

    spl = fit.filename.split("__")
    var = spl[1]    

    procstyles = OrderedDict()
    procstyles["tchan"] = "T_t"
    procstyles["wzjets"] = "WJets_inclusive"
    procstyles["top"] = "TTJets_FullLept"
    procstyles["qcd"] = "QCD"

    procnames = OrderedDict()
    procnames["wzjets"] = "W, Z"
    procnames["top"] = "t, #bar{t}"
    procnames["tchan"] = "signal (t-channel)"
    procnames["qcd"] = "QCD"

    hists_mc_pre = OrderedDict()
    hists_mc_post = OrderedDict()
    print "IN",infile
    print outfile
    fi1 = File(infile)
    fi2 = File(outfile)
    hist_data = fi1.Get(var+"__DATA")

    def loadhists(f):
        out = OrderedDict()
        for k in procnames.keys():
            out[k] = f.Get(var+"__" + k)
            out[k].SetTitle(procnames[k])
            Styling.mc_style(out[k], procstyles[k])
        return out
    hists_mc_pre = loadhists(fi1)
    hists_mc_post = loadhists(fi2)
    print hists_mc_pre, hists_mc_post
    Styling.data_style(hist_data)



    of = OutputFolder(subdir="plots/final_fit")
    def plot_data_mc(hists_mc, hist_data, name):
        canv = ROOT.TCanvas()
        p1 = ROOT.TPad("p1", "p1", 0, 0.3, 1, 1)
        p1.Draw()
        p1.SetTicks(1, 1);
        p1.SetGrid();
        p1.SetFillStyle(0);
        p1.cd()

        stacks_d = OrderedDict()
        print "MC",hists_mc
        print "VAL",hists_mc.values()
        stacks_d["mc"] = hists_mc.values()
        stacks_d["data"] = [hist_data]
        stacks = plot_hists_stacked(
            p1,
            stacks_d,
            x_label=var,
            y_label="",
            do_log_y=True
        )
        leg = legend([hist_data] + list(reversed(hists_mc.values())), styles=["p", "f"])
        print canv, hist_data
        print get_stack_total_hist(stacks["mc"])
        ratio_pad, hratio = plot_data_mc_ratio(canv, get_stack_total_hist(stacks["mc"]), hist_data)

        plot_info = PlotMetaInfo(
            name,
            "CUT",
            "WEIGHT",
            [infile],
            subdir=fit.name,
            comments=str(result[SIGNAL])
        )
        of.savePlot(canv, plot_info)
        canv.Close()
    plot_data_mc(hists_mc_post, hist_data, "post_fit")
    plot_data_mc(hists_mc_pre, hist_data, "pre_fit")
