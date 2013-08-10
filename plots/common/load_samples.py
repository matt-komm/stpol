import os
from plots.common.sample import Sample
from plots.common.cross_sections import lumi_iso, lumi_antiiso
from plots.common.utils import setErrors
from unfold.utils import asymmetry_weight
from copy import deepcopy
from rootpy.io import File

def load_nominal_mc_samples(path, channel):
    datadir = "/".join((path, channel, "mc", "iso", "nominal", "Jul15"))
    samples = Sample.fromDirectory(datadir, out_type="dict")
    return samples

def load_samples(systematic="nominal", channel="mu", path="/".join((os.environ["STPOL_DIR"], "step3_latest")), coupling="powheg"):
    #datadir = "/".join((os.environ["STPOL_DIR"], "step3_latest", "mu", "iso", "nominal"))
    
    
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
    wzjets_other = ["DYJets", "WW", "WZ", "ZZ"]
    top = ["T_tW", "Tbar_tW", "T_s", "Tbar_s", "TTJets_FullLept", "TTJets_SemiLept"]

    components = 3

    if coupling == "powheg":
        tchan = ["T_t_ToLeptons", "Tbar_t_ToLeptons"]
    elif coupling == "comphep":
        tchan = ["TToBMuNu_t-channel", "TToBENu_t-channel", "TToBTauNu_t-channel"]
    elif coupling == "anomWtb-0100":
        tchan = ["TToBMuNu_anomWtb-0100_t-channel", "TToBENu_anomWtb-0100_t-channel", "TToBTauNu_anomWtb-0100_t-channel"]
    elif coupling == "anomWtb-unphys":
        tchan = ["TToBMuNu_anomWtb-unphys_t-channel", "TToBENu_anomWtb-unphys_t-channel", "TToBTauNu_anomWtb-unphys_t-channel"]

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
        
    wzjets = ["W1Jets_exclusive", "W2Jets_exclusive", "W3Jets_exclusive", "W4Jets_exclusive"]
    wzjets_regular = deepcopy(wzjets_other)
    wzjets_regular.extend(wzjets)
    
    if systematic in "nominal":
        sampnames = (
            ("tchan", tchan),
            ("top", top),
            ("wzjets", wzjets_regular),
            ("DATA", datasamp),
            ("qcd", datasamp_aiso),
        )

    elif systematic in ["iso__up", "iso__down"]:
        sampnames = (
            ("qcd", datasamp_aiso),
            ("top", top),
        )

    elif systematic in ["EnDown", "EnUp", "ResDown", "ResUp", "UnclusteredEnDown", "UnclusteredEnUp"]:
        sampnames = (
            ("tchan", tchan),
            ("qcd", datasamp_aiso),
            ("top", top),
            ("wzjets", wzjets_regular),
        )
    elif systematic == "mass__up":
        wzjets.extend(["W1Jets_exclusive", "W2Jets_exclusive", "W3Jets_exclusive", "W4Jets_exclusive"])
        sampnames = (
            ("tchan", ["TToLeptons_t-channel_mass166_5", "TbarToLeptons_t-channel_mass178_5"]),
            ("top", ["T_tW", "Tbar_tW", "T_s", "Tbar_s", "TTJets_mass178_5"]),
            ("qcd", datasamp_aiso),
        )
    elif systematic == "mass__down":
        #other.extend(["T_tW", "Tbar_tW", "T_s", "Tbar_s", "TTJets_mass166_5"])
        #other.extend(datasamp_aiso)
        sampnames = (
            ("tchan", ["TToLeptons_t-channel_mass166_5", "TbarToLeptons_t-channel_mass166_5"]),
            ("top", ["T_tW", "Tbar_tW", "T_s", "Tbar_s", "TTJets_mass166_5"]),
            ("qcd", datasamp_aiso),
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
        wzjets.extend(["W1Jets_exclusive", "W2Jets_exclusive", "W3Jets_exclusive", "W4Jets_exclusive"])
        sampnames = (
            ("top", ["T_tW", "Tbar_tW", "T_s", "Tbar_s", "TTJets_scaleup"]),
            ("qcd", datasamp_aiso),
        )

    elif systematic == "ttbar_scale__down":
        wzjets.extend(["W1Jets_exclusive", "W2Jets_exclusive", "W3Jets_exclusive", "W4Jets_exclusive"])
        sampnames = (
            ("top", ["T_tW", "Tbar_tW", "T_s", "Tbar_s", "TTJets_scaledown"]),
            ("qcd", datasamp_aiso),
        )

    elif systematic == "ttbar_matching__up":
        sampnames = (
            ("top", ["T_tW", "Tbar_tW", "T_s", "Tbar_s", "TTJets_matchingup"]),
            ("qcd", datasamp_aiso),
        )

    elif systematic == "ttbar_matching__down":
        wzjets.extend(["W1Jets_exclusive", "W2Jets_exclusive", "W3Jets_exclusive", "W4Jets_exclusive"])
        other = wzjets
        sampnames = (
            ("top", ["T_tW", "Tbar_tW", "T_s", "Tbar_s", "TTJets_matchingdown"]),
            ("qcd", datasamp_aiso),
        )

    elif systematic == "wjets_matching__down":
        wzjets.extend(["WJetsToLNu_matchingdown"])
        sampnames = (
            ("wzjets", wzjets),
        )

    elif systematic == "wjets_matching__up":
        wzjets.extend(["WJetsToLNu_matchingup"])
        sampnames = (
            ("wzjets", wzjets),
        )
    elif systematic == "wjets_scale__down":
        wzjets.extend(["WJetsToLNu_scaledown"])
        sampnames = (
            ("wzjets", wzjets),
        )
    elif systematic == "wjets_scale__up":
        wzjets.extend(["WJetsToLNu_scaleup"])
        sampnames = (
            ("wzjets", wzjets),
        )
    
    sampnames_new = get_sampnames_for_components(sampnames, components, tchan, wzjets_regular, top, datasamp_aiso)
    return (samples, sampnames_new)

def get_sampnames_for_components(sampnames, components, tchan, wzjets, top, qcd):
    sampnames_new = ()    
    names_tchan = None
    names_wzjets = None
    names_top = None
    names_qcd = None
    names_data = None
    other = []
    for entry in sampnames:
        (a,b) = entry
        print entry, ":", a, b
        
        if a in ["top", "qcd"] and components == 3:
            other.extend(b)
        elif a == "top":
            names_top = b
        elif a == "qcd":
            names_qcd = b
        elif a == "tchan":
            names_tchan = b
        elif a == "wzjets":
            names_wzjets = b
        elif a == "DATA":
            names_data = b
    if names_tchan == None:
        names_tchan = tchan
    if names_wzjets == None:
        names_wzjets = wzjets
    if len(other) == 0:
        if names_top == None:
            names_top = top
        if names_qcd == None:
            names_qcd = qcd
    if names_data is not None:
        if components == 3:
            sampnames_new = (
                ("tchan", names_tchan),
                ("wzjets", names_wzjets),
                ("other", other),
                ("DATA", names_data),
            )    
        else:
            sampnames_new = (
                ("tchan", names_tchan),
                ("wzjets", names_wzjets),
                ("top", names_top),
                ("qcd", names_qcd),
                ("DATA", names_data),
            )
        
    elif components == 3:
        sampnames_new = (
            ("tchan", names_tchan),
            ("wzjets", names_wzjets),
            ("other", other),
        )    
    else:
        sampnames_new = (
            ("tchan", names_tchan),
            ("wzjets", names_wzjets),
            ("top", names_top),
            ("qcd", names_qcd),
        )
    return sampnames_new


def get_qcd_scale_factor(var, channel, mva=False, mtmetcut=None):
    datadir = "/".join(("$STPOL_DIR", "qcd_estimation", "fitted", channel))
    if mtmetcut==None:
        if channel == "mu":
            mtmetcut = "50"
        elif channel == "ele":
            mtmetcut = "45"
    
    if var == "cos_theta" and mva is None:  #final cut based
        filename = "final__2j1t"
    elif var == "abs(eta_lj)":
        filename = "fit__2j1t"
    else:
        filename = "2j1t"
    filename += ("_mt_%s_plus.txt" % mtmetcut)
    f = open(filename, 'r')
    sf = float(f.readline().split()[0])
    print "QCD sf",sf
    return sf
    if channel == "mu":
        if var == "cos_theta":
            if mva is None:
                qcd_scale = 0.886077155677
            else:
                qcd_scale = 7.19018812321
        elif var in ["abs(eta_lj)"]:
            qcd_scale = 5.14037558883
        elif var == "C" or var.startswith("mva"): #with mt cut
            qcd_scale = 7.19018812321
    elif channel == "ele":
        if var == "cos_theta":    
            if mva is None:
                qcd_scale = 0.487353193424
            else:
                qcd_scale = 5.01953827556
        elif var == "abs(eta_lj)":
            qcd_scale = 2.88873446628
        elif var == "C" or var.startswith("mva"): #with mt cut
            qcd_scale = 5.01953827556
    #print "QCD SCALE",qcd_scale
    return qcd_scale

def change_to_mc(file_name):
    path = file_name.split("/")[:-1]
    index = path.index("data")
    path[index] = "mc"
    path.insert(len(path)-1, "nominal")
    path = '/'.join(path)
    return path

def create_histogram_for_fit(sample_name, sample, weight, cut_str_iso, cut_str_antiiso, channel, coupling, var="abs(eta_lj)", plot_range=None, binning=None, asymmetry=None, qcd_extra=None, mtmetcut=None):
    lumi=lumi_iso[channel]
    weight_str = str(weight)
    
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
            path = change_to_mc(sample.file_name)
            nominals = load_nominal_mc_samples(path, channel)            
            for s in nominals:
                h = sample.drawHistogram(var, cut_str_antiiso, weight=weight, plot_range=plot_range)
                hist.Add(h, -1)
            if qcd_extra is not None: #iso down or up - get nominal integral
                hist_nomi = sample.drawHistogram(var, qcd_extra, weight="1.0", plot_range=plot_range)
                for s in nominals:
                    h1 = sample.drawHistogram(var, qcd_extra, weight=weight, plot_range=plot_range)
                    hist_nomi.Add(h1, -1)
                if hist.Integral() > 0:
                    hist.Scale(hist_nomi.Integral()/hist.Integral())

        elif binning is not None:
            hist = sample.drawHistogram(var, cut_str_antiiso, weight="1.0", binning=binning)
            path = change_to_mc(sample.file_name)
            nominals = load_nominal_mc_samples(path, channel)            
            for s in nominals:
                h = sample.drawHistogram(var, cut_str_antiiso, weight=weight, binning=binning)
                hist.Add(h, -1)
            if qcd_extra is not None: #iso down or up - get nominal integral
                hist_nomi = sample.drawHistogram(var, qcd_extra, weight="1.0", plot_range=plot_range)
                for s in nominals:
                    h1 = sample.drawHistogram(var, qcd_extra, weight=weight, plot_range=plot_range)
                    hist_nomi.Add(h1, -1)
                if hist.Integral() > 0:
                    hist.Scale(hist_nomi.Integral()/hist.Integral())
        else:
            raise ValueError("Must specify either plot_range=(nbins, min, max) or binning=numpy.array(..)")
        hist.Scale(get_qcd_scale_factor(var, channel, "mva" in cut_str_iso, mtmetcut))
    setErrors(hist)    #Set error in bins with 0 error to >0
    return hist
