import os
from plots.common.sample import Sample
from plots.common.cross_sections import lumi_iso, lumi_antiiso
#from plots.common.utils import setErrors
from unfold.utils import asymmetry_weight
from copy import deepcopy
from rootpy.io import File
from plots.common.cuts import *

#Set as const right now.
#If configurability needed in the future, do something with it
COMPONENTS = 3#"all"

def load_nominal_mc_samples(path, channel, iso):
    datadir = "/".join((path, channel, "mc", iso, "nominal", "Jul15"))
    samples = Sample.fromDirectory(datadir, out_type="dict")
    return samples


def get_samples(path, channel, systematic):
    samples2 = None
    if systematic in ["EnDown", "EnUp", "ResDown", "ResUp", "UnclusteredEnDown", "UnclusteredEnUp"]:
        datadir = "/".join((path, channel, "mc", "iso", systematic, "Jul15"))
    elif systematic != "nominal":
        #datadir2 = "/".join((path, channel, "mc_syst", "iso", "SYST", "Jul15"))
        #datadir = "/".join((path, channel, "mc", "iso", "nominal", "Jul15"))
        datadir = "/".join(("/hdfs/local/stpol/step3/Sep4_syst_a554579", channel, "mc", "iso", "nominal", "Jul15"))
        datadir2 = "/".join(("/home/andres/single_top/stpol/Sep4_syst_a554579/", channel, "mc_syst", "iso", "SYST", "Jul15"))
        datadir3 = "/".join(("/home/andres/single_top/stpol/Sep4_syst_a554579/", channel, "mc_syst", "iso", "SYST", "Sep4"))
        #print "dd2", datadir2
        #print "dd3", datadir3
        samples2 = Sample.fromDirectory(datadir2, out_type="dict")
        #print "samp2", samples2
        #datadir3 = "/".join(("/hdfs/local/stpol/step3/Sep1_wjets_fsim", channel, "mc_syst", "nominal", "wjets_fsim"))
        samples2.update(Sample.fromDirectory(datadir3, out_type="dict"))
        
        #print "samp3", samples2
    else:
        #datadir = "/".join((path, channel, "mc", "iso", systematic, "Jul15"))
        datadir = "/".join(("/hdfs/local/stpol/step3/Sep4_syst_a554579", channel, "mc", "iso", systematic, "Jul15"))
        datadir2 = "/".join(("/home/andres/single_top/stpol/Sep4_syst_a554579/", channel, "mc_syst", "iso", "SYST", "Jul15"))
        datadir3 = "/".join(("/home/andres/single_top/stpol/Sep4_syst_a554579/", channel, "mc_syst", "iso", "SYST", "Sep4"))
        #datadir2 = "/".join((path, channel, "mc_syst", "iso", "SYST", "Jul15"))
        samples2 = Sample.fromDirectory(datadir2, out_type="dict")
        samples2.update(Sample.fromDirectory(datadir3, out_type="dict"))
    samples = Sample.fromDirectory(datadir, out_type="dict")
    datadir_data = "/".join((path, channel, "data", "iso", "Jul15"))
    datadir_data_Aug1 = "/".join((path, channel, "data", "iso", "Aug1"))
    samples.update(Sample.fromDirectory(datadir_data, out_type="dict"))
    samples.update(Sample.fromDirectory(datadir_data_Aug1, out_type="dict"))
    if samples2 is not None:
        samples.update(samples2)
    
    if channel == "mu":
        samples["SingleMu1_aiso"] = Sample.fromFile("/".join((path, channel, "data", "antiiso", "Jul15", "SingleMu1.root")))
        samples["SingleMu2_aiso"] = Sample.fromFile("/".join((path, channel, "data", "antiiso", "Jul15", "SingleMu2.root")))
        samples["SingleMu3_aiso"] = Sample.fromFile("/".join((path, channel, "data", "antiiso", "Jul15", "SingleMu3.root")))
        samples["SingleMu_miss_aiso"] = Sample.fromFile("/".join((path, channel, "data", "antiiso", "Jul15", "SingleMu_miss.root")))        
    elif channel == "ele":
        samples["SingleEle1_aiso"] = Sample.fromFile("/".join((path, channel, "data", "antiiso", "Jul15", "SingleEle1.root")))
        samples["SingleEle2_aiso"] = Sample.fromFile("/".join((path, channel, "data", "antiiso", "Jul15", "SingleEle2.root")))
        samples["SingleEle_miss_aiso"] = Sample.fromFile("/".join((path, channel, "data", "antiiso", "Jul15", "SingleEle_miss.root")))
    
    return samples


def get_sample_names(channel, systematic, coupling):
    if coupling == "powheg":
        tchan = ["T_t_ToLeptons", "Tbar_t_ToLeptons"]
    elif coupling == "comphep":
        tchan = ["TToBMuNu_t-channel", "TToBENu_t-channel", "TToBTauNu_t-channel"]
    elif coupling == "anomWtb-0100":
        tchan = ["TToBMuNu_anomWtb-0100_t-channel", "TToBENu_anomWtb-0100_t-channel", "TToBTauNu_anomWtb-0100_t-channel"]
    elif coupling == "anomWtb-unphys":
        tchan = ["TToBMuNu_anomWtb-unphys_t-channel", "TToBENu_anomWtb-unphys_t-channel", "TToBTauNu_anomWtb-unphys_t-channel"]

    if channel == "mu":
        datasamp = ["SingleMu1", "SingleMu2", "SingleMu3", "SingleMu_miss"]
        datasamp_aiso = ["SingleMu1_aiso", "SingleMu2_aiso", "SingleMu3_aiso", "SingleMu_miss_aiso"]
    elif channel == "ele":
        datasamp = ["SingleEle1", "SingleEle2", "SingleEle_miss"]
        datasamp_aiso = ["SingleEle1_aiso", "SingleEle2_aiso", "SingleEle_miss_aiso"]
    
    dyjets = ["DYJets"]
    dibosons = ["WW", "WZ", "ZZ"]
    ttbar = ["TTJets_FullLept", "TTJets_SemiLept"]
    schan = ["T_s", "Tbar_s"]
    tWchan = ["T_tW", "Tbar_tW"]
    wjets = ["W1Jets_exclusive", "W2Jets_exclusive", "W3Jets_exclusive", "W4Jets_exclusive"]
    
    #nominal  ...  "EnDown", "EnUp", "ResDown", "ResUp", "UnclusteredEnDown", "UnclusteredEnUp"
    sampnames = {
            "tchan": tchan,
            "schan": schan,
            "tWchan": tWchan,
            "ttbar": ttbar,
            "wjets": wjets,
            "dyjets": dyjets,
            "dibosons": dibosons,
            "DATA": datasamp,
            "qcd": datasamp_aiso,
    }

    if systematic in ["iso__up", "iso__down"]:
        sampnames["qcd"] = datasamp_aiso        

    elif systematic == "mass__up":
        sampnames["tchan"] = ["T_t_ToLeptons_mass175_5", "Tbar_t_ToLeptons_mass175_5"]
        sampnames["ttbar"] = ["TTJets_mass175_5"]

    elif systematic == "mass__down":
        sampnames["tchan"] = ["T_t_ToLeptons_mass169_5", "Tbar_t_ToLeptons_mass169_5"]
        sampnames["ttbar"] = ["TTJets_mass169_5"]

    elif systematic == "tchan_scale__up":
        sampnames["tchan"] = ["T_t_ToLeptons_scaleup", "Tbar_t_ToLeptons_scaleup"]

    elif systematic == "tchan_scale__down":
        sampnames["tchan"] = ["T_t_ToLeptons_scaledown", "Tbar_t_ToLeptons_scaledown"]

    elif systematic == "ttbar_scale__up":
        sampnames["ttbar"] = ["TTJets_scaleup"]

    elif systematic == "ttbar_scale__down":
        sampnames["ttbar"] = ["TTJets_scaledown"]

    elif systematic == "ttbar_matching__up":
        sampnames["ttbar"] = ["TTJets_matchingup"]

    elif systematic == "ttbar_matching__down":
        sampnames["ttbar"] = ["TTJets_matchingdown"]

    elif systematic == "wjets_FSIM_nominal":
        sampnames["wjets"] = ["W1JetsToLNu", "W2JetsToLNu", "W3JetsToLNu", "W4JetsToLNu"]

    elif systematic == "wjets_FSIM_matching__down":
        sampnames["wjets"] = ["W1JetsToLNu_matchingdown", "W2JetsToLNu_matchingdown", "W3JetsToLNu_matchingdown", "W4JetsToLNu_matchingdown"]

    elif systematic == "wjets_FSIM_matching__up":
        sampnames["wjets"] = ["W1JetsToLNu_matchingup", "W2JetsToLNu_matchingup", "W3JetsToLNu_matchingup", "W4JetsToLNu_matchingup"]

    elif systematic == "wjets_FSIM_scale__down":
        sampnames["wjets"] = ["W1JetsToLNu_scaledown", "W2JetsToLNu_scaledown", "W3JetsToLNu_scaledown", "W4JetsToLNu_scaledown"]

    elif systematic == "wjets_FSIM_scale__up":
        sampnames["wjets"] = ["W1JetsToLNu_scaleup", "W2JetsToLNu_scaleup", "W3JetsToLNu_scaleup", "W4JetsToLNu_scaleup"]
    
    return sampnames



def load_samples(systematic="nominal", channel="mu", path="/".join((os.environ["STPOL_DIR"], "step3_latest")), coupling="powheg"):
    
    samples = get_samples(path, channel, systematic)
    sampnames = get_sample_names(channel, systematic, coupling)

    sampnames_new = group_sample_names(sampnames, COMPONENTS, systematic)
    return (samples, sampnames_new)

def group_sample_names(sampnames, components, systematic):
    sampnames_new = {}

    groups = {
            "tchan": ["tchan"],
            "schan": ["schan"],
            "tWchan": ["tWchan"],
            "ttbar": ["ttbar"],
            "wjets": ["wjets"],
            "dyjets": ["dyjets"],
            "dibosons": ["dibosons"],
            "qcd": ["qcd"]
    }

    if components == 3:
        groups = {
            "tchan": ["tchan"],
            "other": ["schan", "tWchan", "ttbar", "qcd"],
            "wzjets": ["wjets", "dyjets", "dibosons"]
        }
    elif components == 4:
        groups = {
            "tchan": ["tchan"],
            "other": ["schan", "tWchan", "ttbar"],
            "qcd":   ["qcd"],
            "wzjets": ["wjets", "dyjets", "dibosons"]
        }


    if systematic == "nominal":
        groups["DATA"] = ["DATA"]

    for group, items in groups.items():
        sampnames_new[group] = []
        for process in items:
            sampnames_new[group].extend(sampnames[process])
        
    names = sampnames_new.items()
    return names


def get_qcd_scale_factor(var, channel, mva=None, mtmetcut=None):
    datadir = "/".join((os.environ["STPOL_DIR"], "qcd_estimation", "fitted", channel))
    if mtmetcut==None:
        if channel == "mu":
            mtmetcut = "50"
        elif channel == "ele":
            mtmetcut = "45"
    
    if var == "cos_theta" and mva is None:  #final cut based
        filename = "final__2j1t"
    elif var == "abs(eta_lj)":
        filename = "fit_2j1t"
    else:
        filename = "2j1t"
    filename += ("_mt_%s_plus.txt" % mtmetcut)
    f = open('/'.join([datadir, filename]), 'r')
    sf = float(f.readline().split()[0])
    return sf

def get_path(file_name):
    path = file_name.split("/")[:-1]
    return path

def change_to_mc_nominal(file_name):
    path = get_path(file_name)
    index = path.index("mc_syst")
    path[index] = "mc"
    del path[index+2]
    path.insert(len(path)-1, "nominal")
    path = '/'.join(path)
    return path

def change_to_mc(file_name):
    path = get_path(file_name)
    index = path.index("data")
    path[index] = "mc"
    path.insert(len(path)-1, "nominal")
    path = '/'.join(path)
    return path

def create_histogram_for_fit(sample_name, sample, weight, cut_str_iso, cut_str_antiiso, channel, coupling, var="abs(eta_lj)", plot_range=None, binning=None, asymmetry=None, qcd_extra=None, mtmetcut=None, hname=None):
    lumi=lumi_iso[channel]
    weight_str = str(weight)
    #weight_str = "1"
    #print "sample name", sample.name, hname
    if (hname and "FSIM" in hname) and ("JetsToLNu" in sample.name):
        if "mva" not in var: 
            cut_str_iso2 = str(Cuts.hlt(channel)*Cuts.lepton(channel)*Cuts.n_jets(2)*Cuts.n_tags(1)*Cuts.metmt(channel, mtmetcut)*Cuts.mva_wp(channel))
        else:
            cut_str_iso2 = str(Cuts.hlt(channel)*Cuts.lepton(channel)*Cuts.n_jets(2)*Cuts.n_tags(1)*Cuts.metmt(channel, mtmetcut))
        if plot_range is not None:
            binning=plot_range
        hist = sample.drawHistogram(var, cut_str_iso2, weight=weight_str, binning=binning)
        hist_yield = sample.drawHistogram(var, cut_str_iso, weight=weight_str, binning=binning)
        hist.Scale(sample.lumiScaleFactor(lumi))
        hist_yield.Scale(sample.lumiScaleFactor(lumi))
        if hist.Integral()>0: 
            print "Scaling FSIM", channel, hist_yield.Integral()/hist.Integral()
            hist.Scale(hist_yield.Integral()/hist.Integral())
    elif sample_name not in ["DATA", "qcd"] and not sample.name.startswith("Single"):
        if sample.name.endswith("ToLeptons") and asymmetry is not None:
            weight_str = str(Weight(str(weight)) * Weights.asymmetry_weight(asymmetry))
        if plot_range is not None:
            #print "HISTO", sample_name, sample.name, " ___" , cut_str_iso, "___", weight_str
            hist = sample.drawHistogram(var, cut_str_iso, weight=weight_str, binning=plot_range)
        elif binning is not None:
            hist = sample.drawHistogram(var, cut_str_iso, weight=weight_str, binning=binning)
        else:
            raise ValueError("Must specify either plot_range=(nbins, min, max) or binning=numpy.array(..)")        
        hist.Scale(sample.lumiScaleFactor(lumi))
        
    elif sample_name == "DATA":   #no weights here
        if plot_range is not None:
        	hist = sample.drawHistogram(var, cut_str_iso, weight="1.0", binning=plot_range)
        elif binning is not None:
            hist = sample.drawHistogram(var, cut_str_iso, weight="1.0", binning=binning)
        else:
            raise ValueError("Must specify either plot_range=(nbins, min, max) or binning=numpy.array(..)")
    elif sample_name in "qcd" or sample.name.startswith("Single"):   #take from antiiso data
        if plot_range is not None:
            hist = sample.drawHistogram(var, cut_str_antiiso, weight="1.0", binning=plot_range)
            path = change_to_mc(sample.file_name)
            nominals = load_nominal_mc_samples(path, channel, "antiiso")
            for s in nominals:      #subtract MC
                h = sample.drawHistogram(var, cut_str_antiiso, weight=weight, binning=plot_range)
                h.Scale(sample.lumiScaleFactor(lumi))
                hist.Add(h, -1)
                h.SetDirectory(0)
            if qcd_extra is not None: #iso down or up - get nominal integral
                hist_nomi = sample.drawHistogram(var, qcd_extra, weight="1.0", binning=plot_range)
                hist_nomi.SetDirectory(0)
                for s in nominals:
                    h1 = sample.drawHistogram(var, qcd_extra, weight=weight, binning=plot_range)
                    h1.Scale(sample.lumiScaleFactor(lumi))
                    h1.SetDirectory(0)
                    hist_nomi.Add(h1, -1)
                if hist.Integral() > 0:
                    hist.Scale(hist_nomi.Integral()/hist.Integral())
                
        elif binning is not None:
            hist = sample.drawHistogram(var, cut_str_antiiso, weight="1.0", binning=binning)
            path = change_to_mc(sample.file_name)
            nominals = load_nominal_mc_samples(path, channel, "antiiso")            
            #print("before subtraction", hist.Integral())
            for s in nominals:
                h = sample.drawHistogram(var, cut_str_antiiso, weight=weight, binning=binning)
                h.SetDirectory(0)
                hist.Add(h, -1)
            #print("after subtraction", hist.Integral())
            if qcd_extra is not None: #iso down or up - get nominal integral
                hist_nomi = sample.drawHistogram(var, qcd_extra, weight="1.0", binning=binning)
                hist_nomi.SetDirectory(0)
                for s in nominals:
                    h1 = sample.drawHistogram(var, qcd_extra, weight=weight, binning=binning)
                    h1.Scale(sample.lumiScaleFactor(lumi))
                    h1.SetDirectory(0)
                    hist_nomi.Add(h1, -1)
                if hist.Integral() > 0:
                    hist.Scale(hist_nomi.Integral()/hist.Integral())
        else:
            raise ValueError("Must specify either plot_range=(nbins, min, max) or binning=numpy.array(..)")
        hist.Scale(get_qcd_scale_factor(var, channel, "mva" in cut_str_iso, mtmetcut))
        #Set MC errors to 0 for QCD        
        for bin in range(1, hist.GetNbinsX()+1):
            hist.SetBinError(bin, 0.000001)        
    #setErrors(hist)    #Set error in bins with 0 error to >0
    #print "sample", sample_name, hist.GetName()
    hist.SetDirectory(0)
    return hist
