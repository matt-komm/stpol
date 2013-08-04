import sys, os
from theta_auto import *
import logging
logging.basicConfig(level=logging.INFO)
signal = 'tchan'
infile = 'histos/mu_mva_BDT/lqeta.root'
outfile = 'histos_fitted.root'
import math

def histofilter(s):
    if '__up' in s or '__down' in s:
        if 'top__Res' in s and 'ele_mva' in infile:
            return False
        if 'ttbar_matching' in s or '__En' in s or 'Res' in s or 'ttbar_scale' in s:#
            return True
        return False
    return True

def add_normal_uncertainty(model, u_name, rel_uncertainty, procname, obsname='*'):
    found_match = False
    par_name = u_name
    if par_name not in model.distribution.get_parameters():
        model.distribution.set_distribution(par_name, 'gauss', mean = 1.0, width = rel_uncertainty, range = [0.0, float("inf")])
    else:
        raise RuntimeError, "parameter name already used"
    for o in model.get_observables():
        if obsname != '*' and o!=obsname: continue
        for p in model.get_processes(o):
            if procname != '*' and procname != p: continue
            model.get_coeff(o,p).add_factor('id', parameter = par_name)
            found_match = True
    if not found_match: raise RuntimeError, 'did not find obname, procname = %s, %s' % (obsname, procname)


def get_model():
    model = build_model_from_rootfile(infile, include_mc_uncertainties = True, histogram_filter = histofilter)    
    model.fill_histogram_zerobins()
    model.set_signal_processes(signal)
    return model

if __name__=="__main__":
    if "theta-auto.py" not in sys.argv[0]:
        raise Exception("Must run as `$STPOL_DIR/theta/utils2/theta-auto.py %s`" % (sys.argv[0]))

    model = get_model()

    print sorted(model.processes)

    # model uncertainties
    execfile('uncertainties.py')

    options = Options()
    options.set("minimizer","strategy","newton_vanilla")
    #options.set("minimizer","strategy","tminuit")
    #options.set("minimizer","strategy","robust")
    #nuisance_constraint="shape:free;rate:free"
    options.set("global", "debug", "true")

    # maximum likelihood estimate
    # FIXME pseudo data
    #result = mle(model, input = 'toys-asimov:1.0', n=1, with_covariance = True, nuisance_constraint = None)
    # data
    result = mle(model, input = 'data', n=1, with_covariance = True, options=options)
    print "Fit result"
    print result
    fitresults = {}
    values = {}
    for process in result[signal]:
        if '__' not in process:
            fitresults[process] = [result[signal][process][0][0], result[signal][process][0][1]]
            values[process] = fitresults[process][0]
    # export sorted fit values
    try:
        os.makedirs("results")
    except:
        pass
    f = open('results/nominal.txt','w')
    for key in sorted(fitresults.keys()):
            line = '%s %f %f\n' % (key, fitresults[key][0], fitresults[key][1])
            print line,
            f.write(line)
    f.close()

    # covariance matrix
    pars = sorted(model.get_parameters([signal]))
    n = len(pars)
    print pars

    #print result[signal]
    cov = result[signal]['__cov'][0]
    p = []
    
    #print cov

    # write out covariance matrix
    import ROOT
    ROOT.gStyle.SetOptStat(0)

    fcov = ROOT.TFile("cov.root","RECREATE")
    canvas = ROOT.TCanvas("c1","Covariance")
    h = ROOT.TH2D("covariance","covariance",n,0,n,n,0,n)
    cor = ROOT.TH2D("correlation","correlation",n,0,n,n,0,n)
    
    for i in range(n):
        h.GetXaxis().SetBinLabel(i+1,pars[i]);
        h.GetYaxis().SetBinLabel(i+1,pars[i]);
        cor.GetXaxis().SetBinLabel(i+1,pars[i])
        cor.GetYaxis().SetBinLabel(i+1,pars[i])

    for i in range(n):
        for j in range(n):
            h.SetBinContent(i+1,j+1,cov[i][j])

    h.Draw("COLZ TEXT")
    try:
        os.makedirs("plots")
    except:
        pass
    canvas.Print("plots/cov.png")
    canvas.Print("plots/cov.pdf")
    #fcov.Close()

    for i in range(n):
        for j in range(n):
            cor.SetBinContent(i+1,j+1,cov[i][j]/math.sqrt(cov[i][i]*cov[j][j]))
            #print i, j, cov[i][j], cov[i][i], cov[j][j], math.sqrt(cov[i][i]*cov[j][j]), cov[i][j]/math.sqrt(cov[i][i]*cov[j][j])

    
    #canvas2 = ROOT.TCanvas("c1","Correlation")
    #fcorr = ROOT.TFile("corr.root","RECREATE")
    cor.Draw("COLZ TEXT")
    try:
        os.makedirs("plots")
    except:
        pass
    canvas.Print("plots/corr.png")
    canvas.Print("plots/corr.pdf")
    cor.Write()
    h.Write()
    fcov.Close()


    model_summary(model)
    report.write_html('htmlout_fit')

    pred = evaluate_prediction(model, values, include_signal = True)
    write_histograms_to_rootfile(pred, outfile)

    ##Plot the fit before and after
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
    tdrstyle()
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
    fi1 = File(infile)
    fi2 = File(outfile)
    #hist_data = fi1.Get("mva_BDT_with_top_mass_eta_lj_C_mu_pt_mt_mu_met_mass_bj_pt_bj_mass_lj__DATA")
    hist_data = fi1.Get("mva_BDT__DATA")

    def loadhists(f):
        out = OrderedDict()
        for k in procnames.keys():
            #out[k] = f.Get("mva_BDT_with_top_mass_eta_lj_C_mu_pt_mt_mu_met_mass_bj_pt_bj_mass_lj__" + k)
            out[k] = f.Get("mva_BDT__" + k)
            out[k].SetTitle(procnames[k])
            Styling.mc_style(out[k], procstyles[k])
        return out
    hists_mc_pre = loadhists(fi1)
    hists_mc_post = loadhists(fi2)
    print hists_mc_pre, hists_mc_post
    Styling.data_style(hist_data)



    of = OutputFolder(subdir="plots")
    def plot_data_mc(hists_mc, hist_data, name):
        canv = ROOT.TCanvas()
        p1 = ROOT.TPad("p1", "p1", 0, 0.3, 1, 1)
        p1.Draw()
        p1.SetTicks(1, 1);
        p1.SetGrid();
        p1.SetFillStyle(0);
        p1.cd()

        stacks_d = OrderedDict()
        stacks_d["mc"] = hists_mc.values()
        stacks_d["data"] = [hist_data]
        stacks = plot_hists_stacked(
            p1,
            stacks_d,
            x_label="#eta_{lj}",
            y_label="",
            do_log_y=False
        )
        leg = legend([hist_data] + list(reversed(hists_mc.values())), styles=["p", "f"])
        ratio_pad, hratio, hline = plot_data_mc_ratio(canv, get_stack_total_hist(stacks["mc"]), hist_data)

        plot_info = PlotMetaInfo(
            name,
            "CUT",
            "WEIGHT",
            [infile],
            subdir="lqetafit",
            comments=str(result[signal])
        )
        of.savePlot(canv, plot_info)
        canv.Close()
    plot_data_mc(hists_mc_post, hist_data, "post_fit")
    plot_data_mc(hists_mc_pre, hist_data, "pre_fit")


