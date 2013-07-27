import ROOT
import os
from plots.common.sample import Sample
from plots.common.utils import mkdir_p
from plots.common.cross_sections import lumi_iso, lumi_antiiso
import logging
import subprocess
import shutil
from plots.common.load_samples import *
from plots.common.cuts import *

def make_systematics_histos(var, cuts, cuts_antiiso, systematics, outdir="/".join([os.environ["STPOL_DIR"], "lqetafit", "histos"]), indir="/".join([os.environ["STPOL_DIR"], "step3_latest"]), channel="mu", binning=None, plot_range=None):
    #Draw the histograms of eta_lj in the final selection sans the eta cut

    outdir = '/'.join([outdir, channel])
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
        #print "A",main_syst, sub_systs
        if systname == "partial":
            for sub_syst, updown in sub_systs.items():
                for (k, v) in updown.items():
                    ss = {}
                    ss[k] = v
                    make_histos_for_syst(var, sub_syst, ss, cuts, cuts_antiiso, outdir, indir, channel, binning=binning, plot_range=plot_range)
        elif systname != "nominal":
            for sub_syst, path in sub_systs.items():
                ss = {}
                ss[sub_syst] = path
                make_histos_for_syst(var, systname, ss, cuts, cuts_antiiso, outdir, indir, channel, binning=binning, plot_range=plot_range)
        else:
            make_histos_for_syst(var, systname, sub_systs, cuts, cuts_antiiso, outdir, indir, channel, binning=binning, plot_range=plot_range)

    hadd_histos(outdir)

def make_histos_for_syst(var, main_syst, sub_systs, cuts, cuts_antiiso, outdir, indir, channel, binning=None, plot_range=None):
        if sub_systs.keys()[0] in ["up", "down"] and main_syst in ["Res", "En", "UnclusteredEn"]:
            ss_type=sub_systs[sub_systs.keys()[0]]
        elif sub_systs.keys()[0] in ["up", "down"]:
            ss_type=main_syst + "__" + sub_systs.keys()[0]
        else:
            ss_type=main_syst
        (samples, sampnames) = load_samples(ss_type, channel, indir)
        outhists = {}
        for sn, samps in sampnames:
            hists = []
            for sampn in samps:
                for sys, sys_types in sub_systs.items():
                    if sys == "nominal":
                        weight_str = sys_types
                        hname = "%s__%s" % (var, sn)
                        write_histogram(var, hname, weight_str, samples, sn, sampn, cuts, cuts_antiiso, outdir, channel, binning=binning, plot_range=plot_range)
                    elif sn in ["DATA", "qcd"] and sys != "nominal":
                        #No systematics if data
                        continue
                    elif main_syst in ["Res", "En", "UnclusteredEn"]:
                        hname = "%s__%s__%s__%s" % (var, sn, main_syst, sys)
                        write_histogram(var, hname, Weights.total_weight(channel), samples, sn, sampn, cuts, cuts_antiiso, outdir, channel,  binning=binning, plot_range=plot_range)
                    elif main_syst=="nominal":
                        for st_name, st in sys_types.items():
                            weight_str = st
                            
                            hname = "%s__%s__%s__%s" % (var, sn, sys, st_name)
                            write_histogram(var, hname, weight_str, samples, sn, sampn, cuts, cuts_antiiso, outdir, channel, binning=binning, plot_range=plot_range)
                    else: #main_syst=="partial"
                        hname = "%s__%s__%s" % (var, sn, ss_type)
                        write_histogram(var, hname, Weights.total_weight(channel), samples, sn, sampn, cuts, cuts_antiiso, outdir, channel,  binning=binning, plot_range=plot_range)


def write_histogram(var, hname, weight, samples, sn, sampn, cuts, cuts_antiiso, outdir, channel, binning=None, plot_range=None):
    weight_str = weight
    samp = samples[sampn]
    outfile = ROOT.TFile(outdir + "/%s_%s.root" % (sampn,hname), "RECREATE")

    if sn=="DATA":
        weight_str = "1"
    if var == "eta_lj":
        var = "abs("+var+")"
    hist = create_histogram_for_fit(sn, samp, weight_str, cuts, cuts_antiiso, channel, var, binning=binning, plot_range=plot_range)
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


def generate_systematics(channel):
    systematics = {}
    systematics["nominal"]={}
    systematics["nominal"]["nominal"] = str(Weights.total_weight(channel))
    #systs_infile = ["pileup", "btaggingBC", "btaggingL", "muonID", "muonIso", "muonTrigger", "wjets_flat", "wjets_shape"]
    if channel == "mu":
        systs_infile = ["btaggingBC", "btaggingL", "leptonID", "leptonIso", "leptonTrigger", "wjets_flat", "wjets_shape"]
    elif channel == "ele":
        systs_infile = ["btaggingBC", "btaggingL", "leptonID", "leptonTrigger", "wjets_flat", "wjets_shape"]
    systs_infile_file=["En", "Res", "UnclusteredEn"]
    for sys in systs_infile:
        systematics["nominal"][sys] = {}
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
    #systematics["partial"]["tchan_scale"] = {}
    #systematics["partial"]["tchan_scale"]["down"] = {}
    #systematics["partial"]["tchan_scale"]["up"] = {}
    systematics["partial"]["ttbar_scale"] = {}
    systematics["partial"]["ttbar_scale"]["down"] = {}
    systematics["partial"]["ttbar_scale"]["up"] = {}
    systematics["partial"]["ttbar_matching"] = {}
    systematics["partial"]["ttbar_matching"]["down"] = {}
    systematics["partial"]["ttbar_matching"]["up"] = {}
        
    systematics["Res"]["down"]="ResDown"
    systematics["Res"]["up"]="ResUp"
    systematics["En"]["down"]="EnDown"
    systematics["En"]["up"]="EnDown"    
    systematics["UnclusteredEn"]["down"]="UnclusteredEnDown"
    systematics["UnclusteredEn"]["up"]="UnclusteredEnUp"    
    return systematics
