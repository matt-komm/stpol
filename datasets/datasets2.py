import os
import re
import logging
import argparse
from SingleTopPolarization.Analysis.common.global_tags import global_tags
from SingleTopPolarization.Analysis.common.lumi_files import lumi_files

template_path = "/".join((os.environ["STPOL_DIR"], "crabs", "templates"))

EMAIL = os.environ["USER"] + "@kbfi.ee"

#INput files for step1 (AODSIM/DATA)
step1_files = [
    "/data/22Jan_ReReco_Runs2012ABCD",
    "/mc/nominal_Summer12_DR53X",
    "/mc/systematic_Summer12_DR53X",
    "/mc/wjets_FSIM_Summer12"
]

#Input files for step2 (USER)
step2_mc_files = [
#    "/mc/Apr19", #Signal+bkg
    "/mc/Jul15",
]

step2_mc_files_qcd = [
    "/mc/Jul15_qcd", #QCD samples
]

#Systematic input files for step2 (that don't need to be variated)
step2_mc_syst_files = [
#    "/mc_syst/Apr19",
    "/mc_syst/Jul15",
]

step2_data_files = [
#    "/data/May20"
    "/data/Jul15",
]

def is_fastsim(name):
    return "FSIM" in name

class Dataset:
    def __init__(self, name, ds, step, do_skimming, is_local, template_fn, global_tag, lumi_file):
        self.name = name
        self.ds = ds
        self.step = step
        self.do_skimming = do_skimming
        self.is_local = is_local
        self.template_fn = template_fn
        self.global_tag = global_tag
        self.lumi_file = lumi_file

    def parseTemplate(self, tag, cmdline, subdir):
        out = open(self.template_fn).read()
        workdir = "WD_{0}".format(self.name)
        out = out.replace("STPOL_DIR", os.environ["STPOL_DIR"])
        out = out.replace("EMAIL", EMAIL)
        out = out.replace("GLOBALTAG", self.global_tag)
        out = out.replace("TAG", tag)
        out = out.replace("DATASET", self.ds)
        out = out.replace("WORKDIR", workdir)


        if self.step=="step1":
            if self.do_skimming:
                cmdline += " doSkimming=True"
            else:
                cmdline += " doSkimming=False"

            if is_fastsim(self.name):
                cmdline += " runOnFastSim=True"

        elif self.step=="step2":
            if is_sherpa(self.name):
                cmdline += " isSherpa=True"
            elif is_comphep(self.name):
                cmdline += " isComphep=True"

            out = out.replace("SUBCHAN", self.name)
            out = out.replace("OUTDIR", subdir)
        if self.lumi_file:
            out = out.replace("LUMIFILE", self.lumi_file)
        cmdline = cmdline.strip()
        out = out.replace("CMDLINEARGS", cmdline)
        return out

    def __str__(self):
        return "<%s, %s, %s, %s, %s, %s>" % (self.name, self.ds, self.step, self.do_skimming, self.is_local, self.template_fn)

def get_step(filename):
    step = filter(lambda x: re.match("step[0-9]*", x), filename.split("/"))
    if len(step)!=1:
        raise Exception("Could not understand step from file path: %s, %s" % (filename, str(step)))
    step = step[0]
    return step

def is_signal(sample_name):
    return sample_name in ["T_t_ToLeptons", "Tbar_t_ToLeptons", "T_t", "Tbar_t"] or sample_name.startswith("TToB")

def is_skimmable(sample_name):
    return  (
                not is_signal(sample_name) and
                not sample_name in ["TTJets_FullLept2", "TTJets_SemiLept2", "WJets_sherpa"] and
                not sample_name.startswith("TToB") and
                not sample_name.startswith("T_t_") and
                not sample_name.startswith("Tbar_t_")
            )

def is_comphep(sample_name):
    return ("comphep" in sample_name or "TToB" in sample_name)

def is_sherpa(sample_name):
    return "sherpa" in sample_name

def skip_comments(fi):
    for line in fi:
        if not line.strip().startswith('#') and len(line)>0:
            yield line.strip()

def is_locally_present(dataset_path):
    local_dataset_file = "/".join((os.environ["STPOL_DIR"], "datasets", "local_datasets.txt"))
    for line in skip_comments(open(local_dataset_file)):
        if line==dataset_path:
            return True
    return False

def is_mc(sample_name):
    return not sample_name.startswith("Single")

def get_template(step, is_mc, is_local):
    key_a = step
    key_b = "mc" if is_mc else "data"
    key_c = "local" if is_local else "grid"
    return "/".join((template_path, key_a, key_b, key_c, "crab.cfg"))

def get_global_tag(sample_name, file_path):
    isMC = is_mc(sample_name)
    key = file_path.split("/")[-1]
    tags = global_tags["mc" if isMC else "data"]
    if key in tags.keys():
        return tags[key]
    else:
        raise Exception("Don't know what to take for global tag for %s" % key)

def get_lumi_file(sample_name, file_path):
    return lumi_files[file_path.split("/")[-1]]

def parse_file(fn):
    datasets = []
    logging.debug("Parsing file %s" % fn)
    step = get_step(fn)

    for line in skip_comments(open(fn)):
        line = re.sub(" +", " ", line)
        line=line.strip()
        if line.startswith("#"):
            continue
        if len(line)==0:
            continue
        spl = line.split(" ")
        if len(spl)!=2:
            raise Exception("Line must be NAME DATASET, but is '%s'" % line)
        name = spl[0]
        ds = spl[1]

        do_skimming = is_skimmable(name)
        is_local = is_locally_present(ds) if step=="step1" else True
        template_fn = get_template(step, is_mc(name), is_local)
        global_tag = get_global_tag(name, fn)
        lumi_file = get_lumi_file(name, fn) if not is_mc(name) else None

        datasets.append(Dataset(name, ds, step, do_skimming, is_local, template_fn, global_tag, lumi_file))
    return datasets

def make_cfgs(fn, tag, cmdline, subdir=None):
    crabdir = "crabs/" + tag
    outdir = fn.replace("datasets", crabdir)
    if subdir:
        spl = outdir.split("/")
        spl.insert(-1, subdir)
        outdir = "/".join(spl)
    logging.info("Input file %s => %s" % (fn, outdir))
    os.makedirs(outdir)
    datasets = parse_file(fn)
    for d in datasets:
        ofn = outdir + "/crab_%s.cfg" % d.name
        of = open(ofn, "w")
        of.write(d.parseTemplate(tag, cmdline, subdir))
        logging.debug("Wrote %s" % ofn)
    return

if __name__=="__main__":
    #fn = "/".join((os.environ["STPOL_DIR"], "datasets", "step1", "mc", "nominal_Summer12_DR53X"))
    logging.basicConfig(level=logging.INFO)
    step_choices = ["step1", "step2", "step2_syst"]

    parser = argparse.ArgumentParser(
        description='Creates crab.cfg files based on \
        a template file.'
    )
    parser.add_argument('-s', action='append', dest='steps',
        default=None, required=True, choices=step_choices,
        help="What confid files to produce"
    )
    parser.add_argument("-t", "--tag", type=str, default="notag",
        help="A unique tag for publishing")
    parser.add_argument("--email", type=str, required=True, default=EMAIL,
        help="Your CERN e-mail address")
    args = parser.parse_args()
    EMAIL = args.email

    dataset_dir = "/".join((os.environ["STPOL_DIR"], "datasets"))

    #Step1
    if "step1" in args.steps:
        step1_base = dataset_dir + "/step1"
        logging.info("Writing step1 cfg files")
        for fn in step1_files:
            make_cfgs(step1_base + fn, args.tag , "")

    #Step2
    if "step2" in args.steps:
        step2_base = dataset_dir + "/step2"

        logging.info("Writing step2 cfg files")
        systs = ["nominal"]
        if "step2_syst" in args.steps:
            logging.info("Writing step2 systematic files")
            systs += ["EnUp", "EnDown", "ResUp", "ResDown", "UnclusteredEnUp", "UnclusteredEnDown"]

        #MC
        for fn in step2_mc_files:
            for syst in systs:
                cmdline_args = ""
                if not syst=="nominal":
                    cmdline_args += "systematic="+syst
                make_cfgs(step2_base + fn, args.tag , cmdline_args, subdir="iso/%s" % syst)
                make_cfgs(step2_base + fn, args.tag , cmdline_args + " reverseIsoCut=True", subdir="antiiso/%s" % syst)
        #Don't variate QCD files
        for fn in step2_mc_files_qcd:
            cmdline_args = ""
            syst="nominal"
            make_cfgs(step2_base + fn, args.tag , cmdline_args, subdir="iso/%s" % syst)
            make_cfgs(step2_base + fn, args.tag , cmdline_args + " reverseIsoCut=True", subdir="antiiso/%s" % syst)

        #DATA
        for fn in step2_data_files:
            cmdline_args = ""
            make_cfgs(step2_base + fn, args.tag , cmdline_args, subdir="iso")
            make_cfgs(step2_base + fn, args.tag , cmdline_args + " reverseIsoCut=True", subdir="antiiso")

        #Other systematics
        if "step2_syst" in args.steps:
            for fn in step2_mc_syst_files:
                cmdline_args = ""
                make_cfgs(step2_base + fn, args.tag , cmdline_args, subdir="iso/SYST")
                make_cfgs(step2_base + fn, args.tag , cmdline_args + " reverseIsoCut=True", subdir="antiiso/SYST")
