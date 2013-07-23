import ROOT
import os
from plots.common.sample import Sample
from plots.common.utils import mkdir_p
from plots.common.cross_sections import lumi_iso, lumi_antiiso
import logging
import subprocess
import shutil
from plots.common.load_samples import *

#outdir = "histos" #NB: please don't use such relative paths, especcially when doing rmtree. data can be destroyed
outdir = "/".join([os.environ["STPOL_DIR"], "lqetafit", "histos"])

NOMINAL_WEIGHT = "pu_weight*b_weight_nominal*muon_IDWeight*muon_IsoWeight*muon_TriggerWeight"

def makehistos(cuts, cuts_antiiso, systematics):
    #Draw the histograms of eta_lj in the final selection sans the eta cut

    #logging.basicConfig(level="INFO")
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)
    logging.debug('This message should appear on the console')
    try:
        shutil.rmtree(outdir)
    except OSError:
        logging.warning("Couldn't remove directory %s" % outdir)

    mkdir_p(outdir)
    #print systematics
    for main_syst, sub_systs in systematics.items():
        systname = main_syst
        #print "A",main_syst, sub_systs
        if systname == "partial":
            for sub_syst, updown in sub_systs.items():
                for (k, v) in updown.items():
                    ss = {}
                    ss[k] = v
                    make_histos_for_syst(sub_syst, ss, cuts, cuts_antiiso)
        elif systname != "nominal":
            for sub_syst, path in sub_systs.items():
                ss = {}
                ss[sub_syst] = path
                make_histos_for_syst(systname, ss, cuts, cuts_antiiso)
        else:
            make_histos_for_syst(systname, sub_systs, cuts, cuts_antiiso)

    hadd_histos(outdir)

def make_histos_for_syst(main_syst, sub_systs, cuts, cuts_antiiso):
        if sub_systs.keys()[0] in ["plus", "minus"] and main_syst in ["Res", "En", "UnclusteredEn"]:
            ss_type=sub_systs[sub_systs.keys()[0]]
        elif sub_systs.keys()[0] in ["plus", "minus"]:
            ss_type=main_syst + "__" + sub_systs.keys()[0]
        else:
            ss_type=main_syst
        (samples, sampnames) = load_samples(ss_type)
        #print ss_type, samples
        #print main_syst, sub_systs, cuts, cuts_antiiso, outdir
        outhists = {}
        for sn, samps in sampnames:
            hists = []
            for sampn in samps:
                for sys, sys_types in sub_systs.items():
                    #print "B",sys, sys_types
                    if sys == "nominal":
                        weight_str = sys_types
                        hname = "%s__%s" % ("eta_lj", sn)
                        write_histogram(hname, weight_str, samples, sn, sampn, cuts, cuts_antiiso)
                    elif sn in ["DATA", "qcd"] and sys != "nominal":
                        #No systematics if data
                        continue
                    elif main_syst in ["Res", "En", "UnclusteredEn"]:
                        hname = "%s__%s__%s__%s" % ("eta_lj", sn, main_syst, sys)
                        write_histogram(hname, NOMINAL_WEIGHT, samples, sn, sampn, cuts, cuts_antiiso)
                    else:
                        hname = "%s__%s__%s" % ("eta_lj", sn, ss_type)
                        write_histogram(hname, NOMINAL_WEIGHT, samples, sn, sampn, cuts, cuts_antiiso)


def write_histogram(hname, weight, samples, sn, sampn, cuts, cuts_antiiso):
    weight_str = weight
    #print samples
    samp = samples[sampn]
    outfile = ROOT.TFile(outdir + "/%s_%s.root" % (sampn,hname), "RECREATE")

    #print weight_str
    hist = create_histogram_for_fit(sn, samp, weight_str, cuts, cuts_antiiso)
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


if __name__=="__main__":
    systematics = {}
    systematics["nominal"]={}
    systematics["nominal"]["nominal"] = NOMINAL_WEIGHT
    systs_infile = ["pileup", "btaggingBC", "btaggingL", "muonID", "muonIso", "muonTrigger"]
    systs_infile_file=["En", "Res", "UnclusteredEn"]
    for sys in systs_infile:
        systematics["nominal"][sys] = {}
    for sys in systs_infile_file:
        systematics[sys] = {}

    #FIXME: add pileup variations
    systematics["nominal"]["pileup"]["plus"] = "pu_weight*b_weight_nominal*muon_IDWeight*muon_IsoWeight*muon_TriggerWeight"
    systematics["nominal"]["pileup"]["minus"] = "pu_weight*b_weight_nominal*muon_IDWeight*muon_IsoWeight*muon_TriggerWeight"
    systematics["nominal"]["btaggingBC"]["plus"] = "pu_weight*b_weight_nominal_BCup*muon_IDWeight*muon_IsoWeight*muon_TriggerWeight"
    systematics["nominal"]["btaggingBC"]["minus"] = "pu_weight*b_weight_nominal_BCdown*muon_IDWeight*muon_IsoWeight*muon_TriggerWeight"
    systematics["nominal"]["btaggingL"]["plus"] = "pu_weight*b_weight_nominal_Lup*muon_IDWeight*muon_IsoWeight*muon_TriggerWeight"
    systematics["nominal"]["btaggingL"]["minus"] = "pu_weight*b_weight_nominal_Ldown*muon_IDWeight*muon_IsoWeight*muon_TriggerWeight"
    systematics["nominal"]["muonID"]["plus"] = "pu_weight*b_weight_nominal*muon_IDWeight_up*muon_IsoWeight*muon_TriggerWeight"
    systematics["nominal"]["muonID"]["minus"] = "pu_weight*b_weight_nominal*muon_IDWeight_down*muon_IsoWeight*muon_TriggerWeight"
    systematics["nominal"]["muonIso"]["plus"] = "pu_weight*b_weight_nominal*muon_IDWeight*muon_IsoWeight_up*muon_TriggerWeight"
    systematics["nominal"]["muonIso"]["minus"] = "pu_weight*b_weight_nominal*muon_IDWeight*muon_IsoWeight_down*muon_TriggerWeight"
    systematics["nominal"]["muonTrigger"]["plus"] = "pu_weight*b_weight_nominal*muon_IDWeight*muon_IsoWeight*muon_TriggerWeight_up"
    systematics["nominal"]["muonTrigger"]["minus"] = "pu_weight*b_weight_nominal*muon_IDWeight*muon_IsoWeight*muon_TriggerWeight_down"
    #TODO: Add PDF-s
    #TODO: Add W+Jets

    #TODO: systematics from separate files
    #systs_inflile = , 'mass','top_scale','tchan_scale','matching']
    systematics["partial"] = {}
    #systematics["partial"]["mass"] = {}
    #systematics["partial"]["mass"]["minus"] = {}
    #systematics["partial"]["mass"]["plus"] = {}
    systematics["partial"]["tchan_scale"] = {}
    systematics["partial"]["tchan_scale"]["minus"] = {}
    systematics["partial"]["tchan_scale"]["plus"] = {}
    systematics["partial"]["ttbar_scale"] = {}
    systematics["partial"]["ttbar_scale"]["minus"] = {}
    systematics["partial"]["ttbar_scale"]["plus"] = {}
    systematics["partial"]["ttbar_matching"] = {}
    systematics["partial"]["ttbar_matching"]["minus"] = {}
    systematics["partial"]["ttbar_matching"]["plus"] = {}

    #TODO JES, JER, UncE ['en','unclusen'
    systematics["Res"]["minus"]="ResDown"
    systematics["Res"]["plus"]="ResUp"
    systematics["En"]["minus"]="EnDown"
    systematics["En"]["plus"]="EnDown"
    systematics["UnclusteredEn"]["minus"]="UnclusteredEnDown"
    systematics["UnclusteredEn"]["plus"]="UnclusteredEnUp"


    cut_str = "n_jets==2 && n_tags==1 && top_mass>130 && top_mass<220 && rms_lj<0.025 && mt_mu>50"
    cut_str_antiiso = cut_str+" && mu_iso>0.3 && mu_iso<0.5"

    makehistos(cut_str, cut_str_antiiso, systematics)
