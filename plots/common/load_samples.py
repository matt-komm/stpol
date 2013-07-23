import os
from plots.common.sample import Sample
from plots.common.cross_sections import lumi_iso, lumi_antiiso

def load_samples(systematic="nominal"):
    #datadir = "/".join((os.environ["STPOL_DIR"], "step3_latest", "mu", "iso", "nominal"))
    #FIXME: make independent of machine (no reference to specific directories like out_step3_06_01)
    samples2 = None
    if systematic in ["EnDown", "EnUp", "ResDown", "ResUp", "UnclusteredEnDown", "UnclusteredEnUp"]:
        datadir = "/".join((os.environ["STPOL_DIR"], "out_step3_06_01", "mu", "iso", systematic))
    elif systematic != "nominal":
        datadir2 = "/".join((os.environ["STPOL_DIR"], "out_step3_06_01", "mu", "iso", "SYST"))
        datadir = "/".join((os.environ["STPOL_DIR"], "step3_mva_temp", "mu", "iso", "nominal"))
        samples2 = Sample.fromDirectory(datadir2, out_type="dict")
    else:
        datadir = "/".join((os.environ["STPOL_DIR"], "step3_mva_temp", "mu", "iso", systematic))
    samples = Sample.fromDirectory(datadir, out_type="dict")

    if samples2 is not None:
        samples.update(samples2)

    #samples["SingleMu_aiso"] = Sample.fromFile("/".join((os.environ["STPOL_DIR"], "step3_latest", "mu", "antiiso", "Nominal", "SingleMu.root")))
    wzjets = ["DYJets", "WW", "WZ", "ZZ"]
    wzjets.extend(["W1Jets_exclusive", "W2Jets_exclusive", "W3Jets_exclusive", "W4Jets_exclusive"])




    if systematic in "nominal":
        samples["SingleMu_aiso"] = Sample.fromFile("/".join((os.environ["STPOL_DIR"], "step3_mva_temp", "mu", "antiiso", systematic, "SingleMu.root")))
        sampnames = (
            ("tchan", ["T_t_ToLeptons", "Tbar_t_ToLeptons"]),
            ("top", ["T_tW", "Tbar_tW", "T_s", "Tbar_s", "TTJets_FullLept", "TTJets_SemiLept"]),
            ("wzjets", wzjets),
            ("DATA", ["SingleMu"]),
            ("qcd", ["SingleMu_aiso"]),
        )

    elif systematic in ["EnDown", "EnUp", "ResDown", "ResUp", "UnclusteredEnDown", "UnclusteredEnUp"]:
        sampnames = (
            ("tchan", ["T_t_ToLeptons", "Tbar_t_ToLeptons"]),
            ("top", ["T_tW", "Tbar_tW", "T_s", "Tbar_s", "TTJets_FullLept", "TTJets_SemiLept"]),
            ("wzjets", wzjets),
        )
    elif systematic == "mass__plus":
        sampnames = (
            ("tchan", ["TToLeptons_t-channel_mass166_5", "TbarToLeptons_t-channel_mass178_5"]),
            ("top", ["T_tW", "Tbar_tW", "T_s", "Tbar_s", "TTJets_mass178_5"]),
        )
    elif systematic == "mass__minus":
        sampnames = (
            ("tchan", ["TToLeptons_t-channel_mass166_5", "TbarToLeptons_t-channel_mass166_5"]),
            ("top", ["T_tW", "Tbar_tW", "T_s", "Tbar_s", "TTJets_mass166_5"]),
        )
    elif systematic == "tchan_scale__plus":
        sampnames = (
            #("tchan", ["TToLeptons_t-channel_scaleup", "TBarToLeptons_t-channel_scaleup"]),
            ("tchan", ["TToLeptons_t-channel_scaleup", "Tbar_t_scaleup"]),
        )

    elif systematic == "tchan_scale__minus":
        sampnames = (
            #("tchan", ["TToLeptons_t-channel_scaledown", "TBarToLeptons_t-channel_scaledown"]),
            ("tchan", ["TToLeptons_t-channel_scaledown", "Tbar_t_scaledown"]),
        )

    elif systematic == "ttbar_scale__plus":
        sampnames = (
            ("top", ["T_tW", "Tbar_tW", "T_s", "Tbar_s", "TTJets_scaleup"]),
        )

    elif systematic == "ttbar_scale__minus":
        sampnames = (
            ("top", ["T_tW", "Tbar_tW", "T_s", "Tbar_s", "TTJets_scaledown"]),
        )

    elif systematic == "ttbar_matching__plus":
        sampnames = (
            ("top", ["T_tW", "Tbar_tW", "T_s", "Tbar_s", "TTJets_matchingup"]),
        )

    elif systematic == "ttbar_matching__minus":
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
    print systematic
    return (samples, sampnames)

def get_qcd_scale_factor():
    #FIXME - automate, take from some "central" file
    return 0.912881608

def create_histogram_for_fit(sample_name, sample, weight_str, cut_str_iso, cut_str_antiiso, var="abs(eta_lj)", plot_range=[15, 0, 4.5]):
    #Create histogram with sample metadata
    lumi=lumi_iso["mu"] #FIXME: Add electorns later as a parameter
    if sample_name not in ["DATA", "qcd"]:
        if "sherpa" in sample.name:
            weight_str += "*gen_weight"
        hist = sample.drawHistogram(var, cut_str_iso, weight=weight_str, plot_range=plot_range)
        hist.Scale(sample.lumiScaleFactor(lumi))
        #hist.normalize_lumi(lumi)
    elif sample_name == "DATA":   #no weights here
        hist = sample.drawHistogram(var, cut_str_iso, weight="1.0", plot_range=plot_range)
    elif sample_name in "qcd":   #take from antiiso data
        hist = sample.drawHistogram(var, cut_str_antiiso, weight="1.0", plot_range=plot_range)
        hist.Scale(get_qcd_scale_factor())
    return hist
