import re, glob
from rootpy.io import File
from plots.common.utils import NestedDict
import ROOT
import logging
logger = logging.getLogger("load_histos2")

def load_file(fn, pat):
    pat = re.compile(pat)
    ret = []
    fi = File(fn)
    ROOT.gROOT.cd()
    for root, dirs, items in fi.walk():
        if len(items)==0:
            continue
        m = pat.match(root)
        if not m:
            continue
        for it in items:
            ret.append((
                tuple(list(m.groups())+[it]), fi.Get(root + "/" + it)
                )
            )
    #fi.Close()
    return ret


def get_updown(name):
    syst_dir = None
    syst_name = None
    for ud in ["up", "down"]:
        if ud in name:
            idx = name.index(ud)
            syst_dir = ud
            syst_name = name[:idx].strip("_").lower()
            break
    if not syst_dir or not syst_name:
        raise ValueError("Could not interpret the systematic scenario variation from %s" % name)
    return (syst_name, syst_dir)


if __name__=="__main__":
    files = glob.glob("/scratch/joosep/merged/*.root")

    pat = ".*hdfs/local/stpol/step3/Aug4_0eb863_full/ele/mc/iso/(.*)/Jul15/(.*).root/channel/ele/ele__iso/jet/2j/tag/1t/met/met__met/signalenr/mva/mva__ele__tight__0_6/(.*)/cos_theta.*"
    ret = []

    for fn in files:
        logger.info("Loading hists from file " + fn)
        ret += load_file(fn, pat)

    syst_scenarios = NestedDict()

    for (sample_var, sample, weight_var, var), hist in ret:
        spl = weight_var.split("__")
        wn = spl[1]
        sample_var = sample_var.lower()
        wtype = None
        wdir = None
        stype = None
        sdir = None

        syst = None
        #Nominal weight, look for variated samples
        if wn=="nominal":
            if sample_var=="nominal":
                continue
            print "S:", wn, sample_var
            syst = sample_var
        #Variated weight, use only nominal sample
        else:
            if sample_var!="nominal":
                continue
            print "W:", wn, sample_var
            syst = wn
        if wn=="nominal" and sample_var=="nominal":
            syst_scenarios[sample]["nominal"]["none"] = hist
        else:
            systname, d = get_updown(syst)
            syst_scenarios[sample][systname][d] = hist

    syst_scenarios = syst_scenarios.as_dict()
    for sample, d1 in syst_scenarios.items():
        for scenario, d2 in d1.items():
            for direction, hist in d2.items():
                print sample, scenario, direction, hist
