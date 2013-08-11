#from ROOT
import os
from plots.common.sample import Sample
from plots.common.utils import mkdir_p
from plots.common.cross_sections import lumi_iso, lumi_antiiso
import logging
import subprocess
import shutil
from plots.common.load_samples import load_samples, load_nominal_mc_samples, create_histogram_for_fit
from plots.common.cuts import *
from rootpy.io import File

def generate_out_dir(channel, var, mva_cut="-1", coupling="powheg", asymmetry=None, mtmetcut=None):
    dirname = channel + "__" +var
    if float(mva_cut) > -1:    
        mva = "__mva_"+str(mva_cut)
        mva = mva.replace(".","_")
        dirname += mva
    if coupling != "powheg":
        dirname += "__" + coupling
    if asymmetry is not None:
        dirname += "__asymm_" + str(asymmetry)
    if mtmetcut is not None:
        dirname += "__mtmet_" + str(mtmetcut)
    return dirname



def make_systematics_histos(var, cuts, cuts_antiiso, systematics, outdir="/".join([os.environ["STPOL_DIR"], "lqetafit", "histos"]), indir="/".join([os.environ["STPOL_DIR"], "step3_latest"]), channel="mu", coupling="powheg", binning=None, plot_range=None, asymmetry=None, mtmetcut=None):
    #logging.basicConfig(level="INFO")
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)
    logging.debug('This message should appear on the console')
    try:
        shutil.rmtree(outdir)
    except OSError:
        logging.warning("Couldn't remove directory %s" % outdir)

    mkdir_p(outdir)
    for main_syst, sub_systs in systematics.items():
        systname = main_syst
        if systname == "partial":
            for sub_syst, updown in sub_systs.items():
                for (k, v) in updown.items():
                    ss = {}
                    ss[k] = v
                    make_histos_for_syst(var, sub_syst, ss, cuts, cuts_antiiso, outdir, indir, channel, coupling=coupling, binning=binning, plot_range=plot_range, asymmetry=asymmetry, mtmetcut=mtmetcut)
        elif systname != "nominal":
            for sub_syst, path in sub_systs.items():
                ss = {}
                ss[sub_syst] = path
                make_histos_for_syst(var, systname, ss, cuts, cuts_antiiso, outdir, indir, channel, coupling=coupling, binning=binning, plot_range=plot_range, asymmetry=asymmetry, mtmetcut=mtmetcut)
        else:
            make_histos_for_syst(var, systname, sub_systs, cuts, cuts_antiiso, outdir, indir, channel, coupling=coupling, binning=binning, plot_range=plot_range, asymmetry=asymmetry, mtmetcut=mtmetcut)

    hadd_histos(outdir)

def make_histos_for_syst(var, main_syst, sub_systs, cuts, cuts_antiiso, outdir, indir, channel, coupling, binning=None, plot_range=None, asymmetry=None, mtmetcut=None):
        if sub_systs.keys()[0] in ["up", "down"] and main_syst in ["Res", "En", "UnclusteredEn"]:
            ss_type=sub_systs[sub_systs.keys()[0]]
        elif sub_systs.keys()[0] in ["up", "down"]:
            ss_type=main_syst + "__" + sub_systs.keys()[0]
        else:
            ss_type=main_syst
        (samples, sampnames) = load_samples(ss_type, channel, indir, coupling)
        
        outhists = {}
        for sn, samps in sampnames:
            hists = []
            for sampn in samps:
                for sys, sys_types in sub_systs.items():
                    if sys == "nominal":
                        weight_str = sys_types
                        hname = "%s__%s" % (var, sn)
                        write_histogram(var, hname, weight_str, samples, sn, sampn, cuts, cuts_antiiso, outdir, channel, coupling, binning=binning, plot_range=plot_range, asymmetry=asymmetry, mtmetcut=mtmetcut)
                    elif sn in ["DATA"] and sys != "nominal":
                        #No systematics if data
                        continue
                    elif main_syst in ["Res", "En", "UnclusteredEn"]:
                        if coupling != "powheg": #these systs not available for comphep (currently)
                            continue
                        hname = "%s__%s__%s__%s" % (var, sn, main_syst, sys)
                        write_histogram(var, hname, Weights.total_weight(channel), samples, sn, sampn, cuts, cuts_antiiso, outdir, channel, coupling, binning=binning, plot_range=plot_range, asymmetry=asymmetry, mtmetcut=mtmetcut)
                    elif main_syst=="nominal":
                        for st_name, st in sys_types.items():
                            weight_str = st
                            hname = "%s__%s__%s__%s" % (var, sn, sys, st_name)
                            write_histogram(var, hname, weight_str, samples, sn, sampn, cuts, cuts_antiiso, outdir, channel, coupling, binning=binning, plot_range=plot_range, asymmetry=asymmetry, mtmetcut=mtmetcut)
                    else: #main_syst=="partial"
                        hname = "%s__%s__%s" % (var, sn, ss_type)
                        write_histogram(var, hname, Weights.total_weight(channel), samples, sn, sampn, cuts, cuts_antiiso, outdir, channel,  coupling, binning=binning, plot_range=plot_range, asymmetry=asymmetry, mtmetcut=mtmetcut)


def write_histogram(var, hname, weight, samples, sn, sampn, cuts, cuts_antiiso, outdir, channel, coupling, binning=None, plot_range=None, asymmetry=None, mtmetcut=None):
    weight_str = weight
    #print hname, samples
    samp = samples[sampn]
    outfile = File(outdir + "/%s_%s.root" % (sampn,hname), "RECREATE")
    if sn=="DATA":
        weight_str = "1"
    if var == "eta_lj":
        var = "abs("+var+")"
    qcd_extra = None
    
    if "iso__down" in hname:
        if var == "abs(eta_lj)":
            cuts_antiiso = str(Cuts.eta_fit_antiiso_down(channel))
            qcd_extra = str(Cuts.eta_fit_antiiso(channel)) #hack for now
        else:
            for x in str(cuts_antiiso).split("&&"):
                if "mva" in x:
                    cut = x
            cut = cut.replace("(","").replace(")","")
            cuts_antiiso = str(Cuts.mva_antiiso_down(channel, mva_var=var)) + " && ("+cut+")"
            qcd_extra = str(Cuts.mva_antiiso(channel, mva_var=var)) + " && ("+cut+")" #hack for now
    elif "iso__up" in hname:
        if var == "abs(eta_lj)":
            cuts_antiiso = str(Cuts.eta_fit_antiiso_up(channel))
            qcd_extra = str(Cuts.eta_fit_antiiso(channel)) #hack for now
        else:
            for x in str(cuts_antiiso).split("&&"):
                if "mva" in x:
                    cut = x
            cut = cut.replace("(","").replace(")","")
            cuts_antiiso = str(Cuts.mva_antiiso_up(channel, mva_var=var)) + " && ("+cut+")"
            qcd_extra = str(Cuts.mva_antiiso(channel, mva_var=var)) + " && ("+cut+")" #hack for now
    #print "!", hname, cuts_antiiso    
    hist = create_histogram_for_fit(sn, samp, weight_str, cuts, cuts_antiiso, channel, coupling, var, binning=binning, plot_range=plot_range, asymmetry=asymmetry, qcd_extra=qcd_extra, mtmetcut=mtmetcut)
    outfile.cd() #Must cd after histogram creation

    #Write histogram to file
    logging.info("Writing histogram %s to file %s" % (hist.GetName(), outfile.GetPath()))
    logging.info("%i entries, %.2f events" % (hist.GetEntries(), hist.Integral()))
    hist.SetName(hname)
    hist.SetDirectory(outfile)
    hist.Write() #Double write?
    outfile.Write()
    outfile.Close()

def hadd_histos(outdir):
    #Add the relevant histograms together
    outfile = generate_file_name(False)
    subprocess.check_call(("hadd -f {0}/"+outfile+" {0}/*.root").format(outdir), shell=True)


def generate_file_name(sherpa):
    name = "lqeta"
    if sherpa:
        name += "_sherpa"
    name += ".root"
    return name


def generate_systematics(channel, coupling):
    systematics = {}
    systematics["nominal"]={}
    systematics["nominal"]["nominal"] = str(Weights.total_weight(channel))
    #systs_infile = ["pileup", "btaggingBC", "btaggingL", "muonID", "muonIso", "muonTrigger", "wjets_flat", "wjets_shape"]
    if channel == "mu":
        systs_infile = ["btaggingBC", "btaggingL", "leptonID", "leptonIso", "leptonTrigger", "wjets_flat", "wjets_shape"]
    elif channel == "ele":
        systs_infile = ["btaggingBC", "btaggingL", "leptonID", "leptonTrigger", "wjets_flat", "wjets_shape"]
    for sys in systs_infile:
        systematics["nominal"][sys] = {}
    if coupling == "powheg":
        systs_infile_file=["En", "Res", "UnclusteredEn"]
        for sys in systs_infile_file:
           systematics[sys] = {}
    
    #FIXME: add pileup variations?
    #systematics["nominal"]["pileup"]["up"] = "pu_weight*b_weight_nominal*muon_IDWeight*muon_IsoWeight*muon_TriggerWeight*wjets_mg_flavour_flat_weight*wjets_mg_flavour_shape_weight"
    #systematics["nominal"]["pileup"]["down"] = "pu_weight*b_weight_nominal*muon_IDWeight*muon_IsoWeight*muon_TriggerWeight*wjets_mg_flavour_flat_weight*wjets_mg_flavour_shape_weight"
    systematics["nominal"]["btaggingBC"]["up"] = str(Weights.pu()*Weights.b_weight("BC", "up")*Weights.lepton_weight(channel) * Weights.wjets_madgraph_shape_weight() * Weights.wjets_madgraph_flat_weight())
    systematics["nominal"]["btaggingBC"]["down"] = str(Weights.pu()*Weights.b_weight("BC", "down")*Weights.lepton_weight(channel) * Weights.wjets_madgraph_shape_weight() * Weights.wjets_madgraph_flat_weight())
    systematics["nominal"]["btaggingL"]["up"] = str(Weights.pu()*Weights.b_weight("L", "up")*Weights.lepton_weight(channel) * Weights.wjets_madgraph_shape_weight() * Weights.wjets_madgraph_flat_weight())
    systematics["nominal"]["btaggingL"]["down"] = str(Weights.pu()*Weights.b_weight("L", "down")*Weights.lepton_weight(channel) * Weights.wjets_madgraph_shape_weight() * Weights.wjets_madgraph_flat_weight())
    systematics["nominal"]["wjets_flat"]["up"] = str(Weights.pu()*Weights.b_weight()*Weights.lepton_weight(channel) * Weights.wjets_madgraph_shape_weight() * Weights.wjets_madgraph_flat_weight("wjets_up"))
    systematics["nominal"]["wjets_flat"]["down"] = str(Weights.pu()*Weights.b_weight()*Weights.lepton_weight(channel) * Weights.wjets_madgraph_shape_weight() * Weights.wjets_madgraph_flat_weight("wjets_down"))
    systematics["nominal"]["wjets_shape"]["up"] = str(Weights.pu()*Weights.b_weight()*Weights.lepton_weight(channel) * Weights.wjets_madgraph_shape_weight("wjets_up") * Weights.wjets_madgraph_flat_weight())
    systematics["nominal"]["wjets_shape"]["down"] = str(Weights.pu()*Weights.b_weight()*Weights.lepton_weight(channel) * Weights.wjets_madgraph_shape_weight("wjets_down") * Weights.wjets_madgraph_flat_weight())
    systematics["nominal"]["leptonID"]["up"] = str(Weights.pu()*Weights.b_weight()*Weights.lepton_weight(channel, "ID", "up") * Weights.wjets_madgraph_shape_weight() * Weights.wjets_madgraph_flat_weight())
    systematics["nominal"]["leptonID"]["down"] =  str(Weights.pu()*Weights.b_weight()*Weights.lepton_weight(channel, "ID", "down") * Weights.wjets_madgraph_shape_weight() * Weights.wjets_madgraph_flat_weight())
    if channel == "mu":
        systematics["nominal"]["leptonIso"]["up"] = str(Weights.pu()*Weights.b_weight()*Weights.lepton_weight(channel, "Iso", "up") * Weights.wjets_madgraph_shape_weight() * Weights.wjets_madgraph_flat_weight())
        systematics["nominal"]["leptonIso"]["down"] = str(Weights.pu()*Weights.b_weight()*Weights.lepton_weight(channel, "Iso", "down") * Weights.wjets_madgraph_shape_weight() * Weights.wjets_madgraph_flat_weight())
    systematics["nominal"]["leptonTrigger"]["up"] = str(Weights.pu()*Weights.b_weight()*Weights.lepton_weight(channel, "Trigger", "up") * Weights.wjets_madgraph_shape_weight() * Weights.wjets_madgraph_flat_weight())
    systematics["nominal"]["leptonTrigger"]["down"] = str(Weights.pu()*Weights.b_weight()*Weights.lepton_weight(channel, "Trigger", "down") * Weights.wjets_madgraph_shape_weight() * Weights.wjets_madgraph_flat_weight())
    
    #TODO: Add PDF-s
    
    systematics["partial"] = {}
    """systematics["partial"]["mass"] = {}
    systematics["partial"]["mass"]["down"] = {}
    systematics["partial"]["mass"]["up"] = {}"""
    """systematics["partial"]["tchan_scale"] = {}
    systematics["partial"]["tchan_scale"]["down"] = {}
    systematics["partial"]["tchan_scale"]["up"] = {}"""
    systematics["partial"]["ttbar_scale"] = {}
    systematics["partial"]["ttbar_scale"]["down"] = {}
    systematics["partial"]["ttbar_scale"]["up"] = {}
    systematics["partial"]["ttbar_matching"] = {}
    systematics["partial"]["ttbar_matching"]["down"] = {}
    systematics["partial"]["ttbar_matching"]["up"] = {}
    """systematics["partial"]["wjets_scale"] = {}
    systematics["partial"]["wjets_scale"]["down"] = {}
    systematics["partial"]["wjets_scale"]["up"] = {}"""
    """systematics["partial"]["wjets_matching"] = {}
    systematics["partial"]["wjets_matching"]["down"] = {}
    systematics["partial"]["wjets_matching"]["up"] = {}"""
    systematics["partial"]["iso"] = {}
    systematics["partial"]["iso"]["down"] = {}
    systematics["partial"]["iso"]["up"] = {}

    if coupling == "powheg":
        systematics["Res"]["down"]="ResDown"
        systematics["Res"]["up"]="ResUp"
        systematics["En"]["down"]="EnDown"
        systematics["En"]["up"]="EnUp"
        systematics["UnclusteredEn"]["down"]="UnclusteredEnDown"
        systematics["UnclusteredEn"]["up"]="UnclusteredEnUp"
    return systematics
