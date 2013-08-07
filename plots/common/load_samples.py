import os
from plots.common.sample import Sample
from plots.common.cross_sections import lumi_iso, lumi_antiiso
from plots.common.utils import *
from unfold.prepare_unfolding import asymmetry_weight

def load_samples(systematic="nominal", channel="mu", path="/".join((os.environ["STPOL_DIR"], "step3_latest")), coupling="powheg"):
    #datadir = "/".join((os.environ["STPOL_DIR"], "step3_latest", "mu", "iso", "nominal"))
    #FIXME: make independent of machine (no reference to specific directories like out_step3_06_01)
    
    
    samples2 = None
    if systematic in ["EnDown", "EnUp", "ResDown", "ResUp", "UnclusteredEnDown", "UnclusteredEnUp"]:
        datadir = "/".join((path, channel, "mc", "iso", systematic, "Jul15"))
    elif systematic != "nominal":
        datadir2 = "/".join((path, channel, "mc_syst", "iso", "SYST", "Jul15"))
        #datadir2 = "/".join(("/home", "andres", "single_top", "stpol", "out", "step3_anomalous_clean", channel, "syst_07_28", "iso", "SYST"))
        #datadir2 = "/".join((path, channel, "mc_syst", "iso", "SYST", "Jul15"))
        datadir = "/".join((path, channel, "mc", "iso", "nominal", "Jul15"))
        samples2 = Sample.fromDirectory(datadir2, out_type="dict")
    else:
        datadir = "/".join((path, channel, "mc", "iso", systematic, "Jul15"))
        datadir2 = "/".join((path, channel, "mc_syst", "iso", "SYST", "Jul15"))
        #datadir2 = "/".join(("/home", "andres", "single_top", "stpol", "out", "step3_anomalous_clean", channel, "syst_07_28", "iso", "SYST"))
        #datadir2 = "/".join((path, channel, "mc_syst", "iso", "SYST", "Jul15"))
        samples2 = Sample.fromDirectory(datadir2, out_type="dict")
    samples = Sample.fromDirectory(datadir, out_type="dict")
    datadir_data = "/".join((path, channel, "data", "iso", "Jul15"))
    samples.update(Sample.fromDirectory(datadir_data, out_type="dict"))
    if samples2 is not None:
        samples.update(samples2)
    #print "__________"
    #print samples
    #print "__________"
    wzjets = ["DYJets", "WW", "WZ", "ZZ"]
    top = ["T_tW", "Tbar_tW", "T_s", "Tbar_s", "TTJets_FullLept", "TTJets_SemiLept"]

    

    if coupling == "powheg":
        tchan = ["T_t_ToLeptons", "Tbar_t_ToLeptons"]
    elif coupling == "comphep":
        tchan = ["TToBMuNu_t-channel", "TToBENu_t-channel", "TToBTauNu_t-channel"]
    elif coupling == "anomWtb-0100":
        tchan = ["TToBMuNu_anomWtb-0100_t-channel", "TToBENu_anomWtb-0100_t-channel", "TToBTauNu_anomWtb-0100_t-channel"]
    elif coupling == "anomWtb-unphys":
        tchan = ["TToBMuNu_anomWtb-unphys_t-channel", "TToBENu_anomWtb-unphys_t-channel", "TToBTauNu_anomWtb-unphys_t-channel"]

    if systematic in "nominal":
        if channel == "mu":
            samples["SingleMu1_aiso"] = Sample.fromFile("/".join((path, channel, "data", "antiiso", "Jul15", "SingleMu1.root")))
            samples["SingleMu2_aiso"] = Sample.fromFile("/".join((path, channel, "data", "antiiso", "Jul15", "SingleMu2.root")))
            samples["SingleMu3_aiso"] = Sample.fromFile("/".join((path, channel, "data", "antiiso", "Jul15", "SingleMu3.root")))
            #samples["SingleMu4_aiso"] = Sample.fromFile("/".join((path, channel, "data", "antiiso", "Jul15", "SingleMu4.root")))
            datasamp = ["SingleMu1", "SingleMu2", "SingleMu3"]#, "SingleMu4"]
            datasamp_aiso = ["SingleMu1_aiso", "SingleMu2_aiso", "SingleMu3_aiso"]#, "SingleMu4_aiso"]
        elif channel == "ele":
            samples["SingleEle1_aiso"] = Sample.fromFile("/".join((path, channel, "data", "antiiso", "Jul15", "SingleEle1.root")))
            samples["SingleEle2_aiso"] = Sample.fromFile("/".join((path, channel, "data", "antiiso", "Jul15", "SingleEle2.root")))
            datasamp = ["SingleEle1", "SingleEle2"]
            datasamp_aiso = ["SingleEle1_aiso", "SingleEle2_aiso"]
        
        wzjets.extend(["W1Jets_exclusive", "W2Jets_exclusive", "W3Jets_exclusive", "W4Jets_exclusive"])
        other = wzjets
        #other.extend(top)
        #other.extend(datasamp_aiso)
        sampnames = (
            ("tchan", tchan),
            ("top", top),
            ("wzjets", wzjets),
            #("other", other),
            ("DATA", datasamp),
            ("qcd", datasamp_aiso),
        )

    elif systematic in ["EnDown", "EnUp", "ResDown", "ResUp", "UnclusteredEnDown", "UnclusteredEnUp"]:
        if channel == "mu":
            samples["SingleMu1_aiso"] = Sample.fromFile("/".join((path, channel, "data", "antiiso", "Jul15", "SingleMu1.root")))
            samples["SingleMu2_aiso"] = Sample.fromFile("/".join((path, channel, "data", "antiiso", "Jul15", "SingleMu2.root")))
            samples["SingleMu3_aiso"] = Sample.fromFile("/".join((path, channel, "data", "antiiso", "Jul15", "SingleMu3.root")))
            #samples["SingleMu4_aiso"] = Sample.fromFile("/".join((path, channel, "data", "antiiso", "Jul15", "SingleMu4.root")))
            datasamp_aiso = ["SingleMu1_aiso", "SingleMu2_aiso", "SingleMu3_aiso"]#, "SingleMu4_aiso"]
        elif channel == "ele":
            samples["SingleEle1_aiso"] = Sample.fromFile("/".join((path, channel, "data", "antiiso", "Jul15", "SingleEle1.root")))
            samples["SingleEle2_aiso"] = Sample.fromFile("/".join((path, channel, "data", "antiiso", "Jul15", "SingleEle2.root")))
            datasamp_aiso = ["SingleEle1_aiso", "SingleEle2_aiso"]
        wzjets.extend(["W1Jets_exclusive", "W2Jets_exclusive", "W3Jets_exclusive", "W4Jets_exclusive"])
        other = wzjets
        #other.extend(top)
        #other.extend(datasamp_aiso)
        sampnames = (
            ("tchan", tchan),
            #("other", other),
            ("top", top),
            ("wzjets", wzjets),
        )
    elif systematic == "mass__up":
        if channel == "mu":
            samples["SingleMu1_aiso"] = Sample.fromFile("/".join((path, channel, "data", "antiiso", "Jul15", "SingleMu1.root")))
            samples["SingleMu2_aiso"] = Sample.fromFile("/".join((path, channel, "data", "antiiso", "Jul15", "SingleMu2.root")))
            samples["SingleMu3_aiso"] = Sample.fromFile("/".join((path, channel, "data", "antiiso", "Jul15", "SingleMu3.root")))
            #samples["SingleMu4_aiso"] = Sample.fromFile("/".join((path, channel, "data", "antiiso", "Jul15", "SingleMu4.root")))
            datasamp_aiso = ["SingleMu1_aiso", "SingleMu2_aiso", "SingleMu3_aiso"]#, "SingleMu4_aiso"]
        elif channel == "ele":
            samples["SingleEle1_aiso"] = Sample.fromFile("/".join((path, channel, "data", "antiiso", "Jul15", "SingleEle1.root")))
            samples["SingleEle2_aiso"] = Sample.fromFile("/".join((path, channel, "data", "antiiso", "Jul15", "SingleEle2.root")))
            datasamp_aiso = ["SingleEle1_aiso", "SingleEle2_aiso"]
        #other = wzjets
        #other.extend(["T_tW", "Tbar_tW", "T_s", "Tbar_s", "TTJets_mass178_5"])
        #other.extend(datasamp_aiso)
        wzjets.extend(["W1Jets_exclusive", "W2Jets_exclusive", "W3Jets_exclusive", "W4Jets_exclusive"])
        sampnames = (
            ("tchan", ["TToLeptons_t-channel_mass166_5", "TbarToLeptons_t-channel_mass178_5"]),
            ("top", ["T_tW", "Tbar_tW", "T_s", "Tbar_s", "TTJets_mass178_5"]),
            #("other", other),
        )
    elif systematic == "mass__down":
        if channel == "mu":
            samples["SingleMu1_aiso"] = Sample.fromFile("/".join((path, channel, "data", "antiiso", "Jul15", "SingleMu1.root")))
            samples["SingleMu2_aiso"] = Sample.fromFile("/".join((path, channel, "data", "antiiso", "Jul15", "SingleMu2.root")))
            samples["SingleMu3_aiso"] = Sample.fromFile("/".join((path, channel, "data", "antiiso", "Jul15", "SingleMu3.root")))
            #samples["SingleMu4_aiso"] = Sample.fromFile("/".join((path, channel, "data", "antiiso", "Jul15", "SingleMu4.root")))
            datasamp_aiso = ["SingleMu1_aiso", "SingleMu2_aiso", "SingleMu3_aiso"]#, "SingleMu4_aiso"]
        elif channel == "ele":
            samples["SingleEle1_aiso"] = Sample.fromFile("/".join((path, channel, "data", "antiiso", "Jul15", "SingleEle1.root")))
            samples["SingleEle2_aiso"] = Sample.fromFile("/".join((path, channel, "data", "antiiso", "Jul15", "SingleEle2.root")))
            datasamp_aiso = ["SingleEle1_aiso", "SingleEle2_aiso"]
        wzjets.extend(["W1Jets_exclusive", "W2Jets_exclusive", "W3Jets_exclusive", "W4Jets_exclusive"])
        other = wzjets
        #other.extend(["T_tW", "Tbar_tW", "T_s", "Tbar_s", "TTJets_mass166_5"])
        #other.extend(datasamp_aiso)
        sampnames = (
            ("tchan", ["TToLeptons_t-channel_mass166_5", "TbarToLeptons_t-channel_mass166_5"]),
            ("top", ["T_tW", "Tbar_tW", "T_s", "Tbar_s", "TTJets_mass166_5"]),
            #("other", other),
        )
    elif systematic == "tchan_scale__up":
        sampnames = (
            ("tchan", ["T_t_ToLeptons_scaleup", "Tbar_t_ToLeptons_scaleup"]),            
        )

    elif systematic == "tchan_scale__down":
        sampnames = (
            ("tchan", ["T_t_ToLeptons_scaledown", "Tbar_t_ToLeptons_scaledown"]),
        )
    elif systematic == "ttbar_scale__up":
        if channel == "mu":
            samples["SingleMu1_aiso"] = Sample.fromFile("/".join((path, channel, "data", "antiiso", "Jul15", "SingleMu1.root")))
            samples["SingleMu2_aiso"] = Sample.fromFile("/".join((path, channel, "data", "antiiso", "Jul15", "SingleMu2.root")))
            samples["SingleMu3_aiso"] = Sample.fromFile("/".join((path, channel, "data", "antiiso", "Jul15", "SingleMu3.root")))
            #samples["SingleMu4_aiso"] = Sample.fromFile("/".join((path, channel, "data", "antiiso", "Jul15", "SingleMu4.root")))
            datasamp_aiso = ["SingleMu1_aiso", "SingleMu2_aiso", "SingleMu3_aiso"]#, "SingleMu4_aiso"]
        elif channel == "ele":
            samples["SingleEle1_aiso"] = Sample.fromFile("/".join((path, channel, "data", "antiiso", "Jul15", "SingleEle1.root")))
            samples["SingleEle2_aiso"] = Sample.fromFile("/".join((path, channel, "data", "antiiso", "Jul15", "SingleEle2.root")))
            datasamp_aiso = ["SingleEle1_aiso", "SingleEle2_aiso"]
        wzjets.extend(["W1Jets_exclusive", "W2Jets_exclusive", "W3Jets_exclusive", "W4Jets_exclusive"])
        other = wzjets
        #other.extend(["T_tW", "Tbar_tW", "T_s", "Tbar_s", "TTJets_scaleup"])
        #other.extend(datasamp_aiso)
        sampnames = (
            ("top", ["T_tW", "Tbar_tW", "T_s", "Tbar_s", "TTJets_scaleup"]),
            #("other", other),
        )

    elif systematic == "ttbar_scale__down":
        if channel == "mu":
            samples["SingleMu1_aiso"] = Sample.fromFile("/".join((path, channel, "data", "antiiso", "Jul15", "SingleMu1.root")))
            samples["SingleMu2_aiso"] = Sample.fromFile("/".join((path, channel, "data", "antiiso", "Jul15", "SingleMu2.root")))
            samples["SingleMu3_aiso"] = Sample.fromFile("/".join((path, channel, "data", "antiiso", "Jul15", "SingleMu3.root")))
            #samples["SingleMu4_aiso"] = Sample.fromFile("/".join((path, channel, "data", "antiiso", "Jul15", "SingleMu4.root")))
            datasamp_aiso = ["SingleMu1_aiso", "SingleMu2_aiso", "SingleMu3_aiso"]#, "SingleMu4_aiso"]
        elif channel == "ele":
            samples["SingleEle1_aiso"] = Sample.fromFile("/".join((path, channel, "data", "antiiso", "Jul15", "SingleEle1.root")))
            samples["SingleEle2_aiso"] = Sample.fromFile("/".join((path, channel, "data", "antiiso", "Jul15", "SingleEle2.root")))
            datasamp_aiso = ["SingleEle1_aiso", "SingleEle2_aiso"]
        wzjets.extend(["W1Jets_exclusive", "W2Jets_exclusive", "W3Jets_exclusive", "W4Jets_exclusive"])
        other = wzjets
        #other.extend(["T_tW", "Tbar_tW", "T_s", "Tbar_s", "TTJets_scaledown"])
        #other.extend(datasamp_aiso)
        sampnames = (
            ("top", ["T_tW", "Tbar_tW", "T_s", "Tbar_s", "TTJets_scaledown"]),
            #("other", other),
        )

    elif systematic == "ttbar_matching__up":
        if channel == "mu":
            samples["SingleMu1_aiso"] = Sample.fromFile("/".join((path, channel, "data", "antiiso", "Jul15", "SingleMu1.root")))
            samples["SingleMu2_aiso"] = Sample.fromFile("/".join((path, channel, "data", "antiiso", "Jul15", "SingleMu2.root")))
            samples["SingleMu3_aiso"] = Sample.fromFile("/".join((path, channel, "data", "antiiso", "Jul15", "SingleMu3.root")))
            #samples["SingleMu4_aiso"] = Sample.fromFile("/".join((path, channel, "data", "antiiso", "Jul15", "SingleMu4.root")))
            datasamp_aiso = ["SingleMu1_aiso", "SingleMu2_aiso", "SingleMu3_aiso"]#, "SingleMu4_aiso"]
        elif channel == "ele":
            samples["SingleEle1_aiso"] = Sample.fromFile("/".join((path, channel, "data", "antiiso", "Jul15", "SingleEle1.root")))
            samples["SingleEle2_aiso"] = Sample.fromFile("/".join((path, channel, "data", "antiiso", "Jul15", "SingleEle2.root")))
            datasamp_aiso = ["SingleEle1_aiso", "SingleEle2_aiso"]
        wzjets.extend(["W1Jets_exclusive", "W2Jets_exclusive", "W3Jets_exclusive", "W4Jets_exclusive"])
        #other = wzjets
        #other.extend(["T_tW", "Tbar_tW", "T_s", "Tbar_s", "TTJets_matchingup"])
        sampnames = (
            ("top", ["T_tW", "Tbar_tW", "T_s", "Tbar_s", "TTJets_matchingup"]),
            #("other", other),
        )

    elif systematic == "ttbar_matching__down":
        if channel == "mu":
            samples["SingleMu1_aiso"] = Sample.fromFile("/".join((path, channel, "data", "antiiso", "Jul15", "SingleMu1.root")))
            samples["SingleMu2_aiso"] = Sample.fromFile("/".join((path, channel, "data", "antiiso", "Jul15", "SingleMu2.root")))
            samples["SingleMu3_aiso"] = Sample.fromFile("/".join((path, channel, "data", "antiiso", "Jul15", "SingleMu3.root")))
            #samples["SingleMu4_aiso"] = Sample.fromFile("/".join((path, channel, "data", "antiiso", "Jul15", "SingleMu4.root")))
            datasamp_aiso = ["SingleMu1_aiso", "SingleMu2_aiso", "SingleMu3_aiso"]#, "SingleMu4_aiso"]
        elif channel == "ele":
            samples["SingleEle1_aiso"] = Sample.fromFile("/".join((path, channel, "data", "antiiso", "Jul15", "SingleEle1.root")))
            samples["SingleEle2_aiso"] = Sample.fromFile("/".join((path, channel, "data", "antiiso", "Jul15", "SingleEle2.root")))
            datasamp_aiso = ["SingleEle1_aiso", "SingleEle2_aiso"]
        wzjets.extend(["W1Jets_exclusive", "W2Jets_exclusive", "W3Jets_exclusive", "W4Jets_exclusive"])
        other = wzjets
        #other.extend(["T_tW", "Tbar_tW", "T_s", "Tbar_s", "TTJets_matchingdown"])
        #other.extend(datasamp_aiso)
        sampnames = (
            ("top", ["T_tW", "Tbar_tW", "T_s", "Tbar_s", "TTJets_matchingdown"]),
            #("other", other),
        )

    elif systematic == "wjets_matching__down":
        if channel == "mu":
            samples["SingleMu1_aiso"] = Sample.fromFile("/".join((path, channel, "data", "antiiso", "Jul15", "SingleMu1.root")))
            samples["SingleMu2_aiso"] = Sample.fromFile("/".join((path, channel, "data", "antiiso", "Jul15", "SingleMu2.root")))
            samples["SingleMu3_aiso"] = Sample.fromFile("/".join((path, channel, "data", "antiiso", "Jul15", "SingleMu3.root")))
            #samples["SingleMu4_aiso"] = Sample.fromFile("/".join((path, channel, "data", "antiiso", "Jul15", "SingleMu4.root")))
            datasamp_aiso = ["SingleMu1_aiso", "SingleMu2_aiso", "SingleMu3_aiso"]#, "SingleMu4_aiso"]
        elif channel == "ele":
            samples["SingleEle1_aiso"] = Sample.fromFile("/".join((path, channel, "data", "antiiso", "Jul15", "SingleEle1.root")))
            samples["SingleEle2_aiso"] = Sample.fromFile("/".join((path, channel, "data", "antiiso", "Jul15", "SingleEle2.root")))
            datasamp_aiso = ["SingleEle1_aiso", "SingleEle2_aiso"]
        wzjets.extend(["WJetsToLNu_matchingdown"])
        other = wzjets
        sampnames = (
            ("wzjets", wzjets),
        )
        #system.exit(0)

    elif systematic == "wjets_matching__up":
        if channel == "mu":
            samples["SingleMu1_aiso"] = Sample.fromFile("/".join((path, channel, "data", "antiiso", "Jul15", "SingleMu1.root")))
            samples["SingleMu2_aiso"] = Sample.fromFile("/".join((path, channel, "data", "antiiso", "Jul15", "SingleMu2.root")))
            samples["SingleMu3_aiso"] = Sample.fromFile("/".join((path, channel, "data", "antiiso", "Jul15", "SingleMu3.root")))
            #samples["SingleMu4_aiso"] = Sample.fromFile("/".join((path, channel, "data", "antiiso", "Jul15", "SingleMu4.root")))
            datasamp_aiso = ["SingleMu1_aiso", "SingleMu2_aiso", "SingleMu3_aiso"]#, "SingleMu4_aiso"]
        elif channel == "ele":
            samples["SingleEle1_aiso"] = Sample.fromFile("/".join((path, channel, "data", "antiiso", "Jul15", "SingleEle1.root")))
            samples["SingleEle2_aiso"] = Sample.fromFile("/".join((path, channel, "data", "antiiso", "Jul15", "SingleEle2.root")))
            datasamp_aiso = ["SingleEle1_aiso", "SingleEle2_aiso"]
        wzjets.extend(["WJetsToLNu_matchingup"])
        other = wzjets
        sampnames = (
            ("wzjets", wzjets),
        )
    elif systematic == "wjets_scale__down":
        if channel == "mu":
            samples["SingleMu1_aiso"] = Sample.fromFile("/".join((path, channel, "data", "antiiso", "Jul15", "SingleMu1.root")))
            samples["SingleMu2_aiso"] = Sample.fromFile("/".join((path, channel, "data", "antiiso", "Jul15", "SingleMu2.root")))
            samples["SingleMu3_aiso"] = Sample.fromFile("/".join((path, channel, "data", "antiiso", "Jul15", "SingleMu3.root")))
            #samples["SingleMu4_aiso"] = Sample.fromFile("/".join((path, channel, "data", "antiiso", "Jul15", "SingleMu4.root")))
            datasamp_aiso = ["SingleMu1_aiso", "SingleMu2_aiso", "SingleMu3_aiso"]#, "SingleMu4_aiso"]
        elif channel == "ele":
            samples["SingleEle1_aiso"] = Sample.fromFile("/".join((path, channel, "data", "antiiso", "Jul15", "SingleEle1.root")))
            samples["SingleEle2_aiso"] = Sample.fromFile("/".join((path, channel, "data", "antiiso", "Jul15", "SingleEle2.root")))
            datasamp_aiso = ["SingleEle1_aiso", "SingleEle2_aiso"]
        wzjets.extend(["WJetsToLNu_scaledown"])
        other = wzjets
        sampnames = (
            ("wzjets", wzjets),
        )
    elif systematic == "wjets_scale__up":
        if channel == "mu":
            samples["SingleMu1_aiso"] = Sample.fromFile("/".join((path, channel, "data", "antiiso", "Jul15", "SingleMu1.root")))
            samples["SingleMu2_aiso"] = Sample.fromFile("/".join((path, channel, "data", "antiiso", "Jul15", "SingleMu2.root")))
            samples["SingleMu3_aiso"] = Sample.fromFile("/".join((path, channel, "data", "antiiso", "Jul15", "SingleMu3.root")))
            #samples["SingleMu4_aiso"] = Sample.fromFile("/".join((path, channel, "data", "antiiso", "Jul15", "SingleMu4.root")))
            datasamp_aiso = ["SingleMu1_aiso", "SingleMu2_aiso", "SingleMu3_aiso"]#, "SingleMu4_aiso"]
        elif channel == "ele":
            samples["SingleEle1_aiso"] = Sample.fromFile("/".join((path, channel, "data", "antiiso", "Jul15", "SingleEle1.root")))
            samples["SingleEle2_aiso"] = Sample.fromFile("/".join((path, channel, "data", "antiiso", "Jul15", "SingleEle2.root")))
            datasamp_aiso = ["SingleEle1_aiso", "SingleEle2_aiso"]
        wzjets.extend(["WJetsToLNu_scaleup"])
        other = wzjets
        sampnames = (
            ("wzjets", wzjets),
        )

    return (samples, sampnames)

def get_qcd_scale_factor(var, channel, mva=False):
    #FIXME - automate, take from some "central" file
    
    if channel == "mu":
        if var == "cos_theta":
            if mva is None:
                qcd_scale = 0.400106115551
            else:
                qcd_scale = 3.30901987434
        elif var in ["abs(eta_lj)"]:
            qcd_scale = 2.36704374649
        elif var == "C" or var.startswith("mva"): #with mt cut
            qcd_scale = 3.30901987434
    elif channel == "ele":
        if var == "cos_theta":    
            if mva is None:
                qcd_scale = 0.380505601735
            else:
                qcd_scale = 3.86190227034
        elif var == "abs(eta_lj)":
            qcd_scale = 2.22605022286
        elif var == "C" or var.startswith("mva"): #with mt cut
            qcd_scale = 3.86190227034
    print "QCD SCALE",qcd_scale
    return qcd_scale

def create_histogram_for_fit(sample_name, sample, weight, cut_str_iso, cut_str_antiiso, channel, coupling, var="abs(eta_lj)", plot_range=None, binning=None, asymmetry=None):
    lumi=lumi_iso[channel]
    weight_str = str(weight)
    print plot_range
    print sample
    print sample_name
    print cut_str_iso
    if sample_name not in ["DATA", "qcd"] and not sample.name.startswith("Single"):
        if sample.name.endswith("ToLeptons") and asymmetry is not None:
            weight_str = asymmetry_weight(asymmetry, weight)
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
    elif sample_name in "qcd" or sample.name.startswith("Single"):   #take from antiiso data
        if plot_range is not None:
        	hist = sample.drawHistogram(var, cut_str_antiiso, weight="1.0", plot_range=plot_range)
        elif binning is not None:
            hist = sample.drawHistogram(var, cut_str_antiiso, weight="1.0", binning=binning)
        else:
            raise ValueError("Must specify either plot_range=(nbins, min, max) or binning=numpy.array(..)")
        hist.Scale(get_qcd_scale_factor(var, channel, "mva" in cut_str_iso))
    setErrors(hist)    #Set error in bins with 0 error to >0
    return hist
