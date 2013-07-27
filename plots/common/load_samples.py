import os
from plots.common.sample import Sample
from plots.common.cross_sections import lumi_iso, lumi_antiiso

def load_samples(systematic="nominal", path="/".join((os.environ["STPOL_DIR"], "step3_latest"))):
    #datadir = "/".join((os.environ["STPOL_DIR"], "step3_latest", "mu", "iso", "nominal"))
    #FIXME: make independent of machine (no reference to specific directories like out_step3_06_01)
    
    
    samples2 = None
    if systematic in ["EnDown", "EnUp", "ResDown", "ResUp", "UnclusteredEnDown", "UnclusteredEnUp"]:
        datadir = "/".join((path, "mu", "mc", "iso", systematic, "Jul15"))
    elif systematic != "nominal":
        datadir2 = "/".join((path, "mu", "mc_syst", "iso", "SYST", "Jul15"))
        #datadir = "/".join((os.environ["STPOL_DIR"], "Jul22_partial", "mu", "iso", "nominal"))
        datadir = "/".join((path, "mu", "mc", "iso", "nominal", "Jul15"))
        samples2 = Sample.fromDirectory(datadir2, out_type="dict")
    else:
        datadir = "/".join((path, "mu", "mc", "iso", systematic, "Jul15"))
        #datadir = "/".join((os.environ["STPOL_DIR"], "Jul22_partial", "mu", "iso", "nominal"))
    samples = Sample.fromDirectory(datadir, out_type="dict")
    
    datadir_data = "/".join((path, "mu", "data", "iso", "Jul15"))
    samples.update(Sample.fromDirectory(datadir_data, out_type="dict"))
    if samples2 is not None:
        samples.update(samples2)
    
    wzjets = ["DYJets", "WW", "WZ", "ZZ"]
    wzjets.extend(["W1Jets_exclusive", "W2Jets_exclusive", "W3Jets_exclusive", "W4Jets_exclusive"])

    if systematic in "nominal":
        samples["SingleMu1_aiso"] = Sample.fromFile("/".join((path, "mu", "data", "antiiso", "Jul15", "SingleMu1.root")))
        samples["SingleMu2_aiso"] = Sample.fromFile("/".join((path, "mu", "data", "antiiso", "Jul15", "SingleMu2.root")))
        samples["SingleMu3_aiso"] = Sample.fromFile("/".join((path, "mu", "data", "antiiso", "Jul15", "SingleMu3.root")))
        #return
        sampnames = (
            ("tchan", ["T_t_ToLeptons", "Tbar_t_ToLeptons"]),
            #("tchan", ["Tbar_t_ToLeptons"]),
            ("top", ["T_tW", "Tbar_tW", "T_s", "Tbar_s", "TTJets_FullLept", "TTJets_SemiLept"]),
            ("wzjets", wzjets),
            ("DATA", ["SingleMu1", "SingleMu2", "SingleMu3"]),
            ("qcd", ["SingleMu1_aiso", "SingleMu2_aiso", "SingleMu3_aiso"]),
        )

    elif systematic in ["EnDown", "EnUp", "ResDown", "ResUp", "UnclusteredEnDown", "UnclusteredEnUp"]:
        sampnames = (
            ("tchan", ["T_t_ToLeptons", "Tbar_t_ToLeptons"]),
            ("top", ["T_tW", "Tbar_tW", "T_s", "Tbar_s", "TTJets_FullLept", "TTJets_SemiLept"]),
            ("wzjets", wzjets),
        )
    elif systematic == "mass__up":
        sampnames = (
            ("tchan", ["TToLeptons_t-channel_mass166_5", "TbarToLeptons_t-channel_mass178_5"]),
            ("top", ["T_tW", "Tbar_tW", "T_s", "Tbar_s", "TTJets_mass178_5"]),
        )
    elif systematic == "mass__down":
        sampnames = (
            ("tchan", ["TToLeptons_t-channel_mass166_5", "TbarToLeptons_t-channel_mass166_5"]),
            ("top", ["T_tW", "Tbar_tW", "T_s", "Tbar_s", "TTJets_mass166_5"]),
        )
    elif systematic == "tchan_scale__up":
        sampnames = (
            #("tchan", ["TToLeptons_t-channel_scaleup", "TBarToLeptons_t-channel_scaleup"]),
            ("tchan", ["TToLeptons_t-channel_scaleup", "Tbar_t_scaleup"]),
        )

    elif systematic == "tchan_scale__down":
        sampnames = (
            #("tchan", ["TToLeptons_t-channel_scaledown", "TBarToLeptons_t-channel_scaledown"]),
            ("tchan", ["TToLeptons_t-channel_scaledown", "Tbar_t_scaledown"]),
        )
    elif systematic == "ttbar_scale__up":
        sampnames = (
            ("top", ["T_tW", "Tbar_tW", "T_s", "Tbar_s", "TTJets_scaleup"]),
        )

    elif systematic == "ttbar_scale__down":
        sampnames = (
            ("top", ["T_tW", "Tbar_tW", "T_s", "Tbar_s", "TTJets_scaledown"]),
        )

    elif systematic == "ttbar_matching__up":
        sampnames = (
            ("top", ["T_tW", "Tbar_tW", "T_s", "Tbar_s", "TTJets_matchingup"]),
        )

    elif systematic == "ttbar_matching__down":
        sampnames = (
            ("top", ["T_tW", "Tbar_tW", "T_s", "Tbar_s", "TTJets_matchingdown"]),
        )

    """ TODO:
    WJetsToLNu_matchingdown.root
    WJetsToLNu_matchingup.root
    WJetsToLNu_scaledown
    WJetsToLNu_scaledown.root
    WJetsToLNu_scaleup.root
    """
    return (samples, sampnames)

def get_qcd_scale_factor(var, channel):
    #FIXME - automate, take from some "central" file
    if channel == "mu":
        if var == "cos_theta":    
            return 0.725338051044
        elif var == "abs(eta_lj)":
            return 4.1846044046
    elif channel == "ele":
        if var == "cos_theta":    
            return 0.124929101662
        elif var == "abs(eta_lj)":
            return 0.678110491459

def create_histogram_for_fit(sample_name, sample, weight, cut_str_iso, cut_str_antiiso, channel, var="abs(eta_lj)", plot_range=None, binning=None):
    lumi=lumi_iso[channel]
    weight_str = str(weight)   
    print sample_name
    print weight
    cut_str_iso = "(1)"
    if sample_name not in ["DATA", "qcd"]:
        if plot_range is not None:
            hist = sample.drawHistogram(var, cut_str_iso, weight=weight_str, plot_range=plot_range)
        elif binning is not None:
            hist = sample.drawHistogram(var, cut_str_iso, weight=weight_str, binning=binning)
        else:
            raise ValueError("Must specify either plot_range=(nbins, min, max) or binning=numpy.array(..)")
        hist.Scale(sample.lumiScaleFactor(lumi))
    elif sample_name == "DATA":   #no weights here
        if plot_range is not None:
        	hist = sample.drawHistogram(var, cut_str_iso, weight="1.0", plot_range=plot_range)
        elif binning is not None:
            hist = sample.drawHistogram(var, cut_str_iso, weight="1.0", binning=binning)
        else:
            raise ValueError("Must specify either plot_range=(nbins, min, max) or binning=numpy.array(..)")
    elif sample_name in "qcd":   #take from antiiso data
        if plot_range is not None:
        	hist = sample.drawHistogram(var, cut_str_antiiso, weight="1.0", plot_range=plot_range)
        elif binning is not None:
            hist = sample.drawHistogram(var, cut_str_antiiso, weight="1.0", binning=binning)
        else:
            raise ValueError("Must specify either plot_range=(nbins, min, max) or binning=numpy.array(..)")
        hist.Scale(get_qcd_scale_factor(var, channel))
    return hist
