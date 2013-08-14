import re, glob
from collections import deque
from rootpy.io import File
import itertools
from plots.common.utils import NestedDict
import ROOT
import logging

logger = logging.getLogger("load_histos2")
logger.setLevel(logging.DEBUG)

def load_file(fi, pat):
    #depth = len(pat.split("/"))
    pat = re.compile(pat)
    ret = []

    ROOT.gROOT.cd()
    n = 0
    for root, dirs, items in fi.walk():
        #logger.debug(root)
        n+=1
        #if len(items)==0:
        #    continue
        #if n%100 == 0:
        #    logger.debug(n)
        m = pat.match(root)
        if root.split("/")[0] == fi.GetName():
            root = "/".join(root.split("/")[1:])
        #root = "/".join(root.split("/")[1:])
        if not m:
            continue
        pr = [None]*len(dirs+items)
        for n, it in zip(range(len(dirs+items)), dirs+items):
            pr[n] = (tuple(list(m.groups())+[it]), fi.Get(root + "/" + it))
        ret += pr
    #fi.Close()
    return ret

def rekeys(fi, pat):
    if not hasattr(fi, "GetListOfKeys") or len(pat)==0:
        return [fi]
    top = pat.popleft()
    return [
        list(
            rekeys(fi.Get(k.GetName()), pat)
        )
        for k in fi.GetListOfKeys() if top.match(k.GetName())
    ]


if __name__=="__main__":
    fnames = glob.glob("hists/merged/*.root")

    #subpath = "hdfs/local/stpol/step3/Aug4_0eb863_full/ele/mc/iso/nominal/Jul15/T_t_ToLeptons.root/channel/ele/ele__iso/jet/2j/tag/1t/met/met__met/signalenr/mva/mva__ele__tight__0_6"
    subpath = "hdfs/local/stpol/step3/Aug4_0eb863_full/ele/mc/iso/"

    pat = ".*/.*/cos_theta.*"

    # for fn in files:
    #     logger.info("Loading hists from file " + fn)
    #     ret += load_file(fn, pat)

    # syst_scenarios = NestedDict()

    # for (sample_var, sample, weight_var, var), hist in ret:
    #     spl = weight_var.split("__")
    #     wn = spl[1]
    #     sample_var = sample_var.lower()
    #     wtype = None
    #     wdir = None
    #     stype = None
    #     sdir = None

    #     syst = None
    #     #Nominal weight, look for variated samples
    #     if wn=="nominal":
    #         if sample_var=="nominal":
    #             continue
    #         print "S:", wn, sample_var
    #         syst = sample_var
    #     #Variated weight, use only nominal sample
    #     else:
    #         if sample_var!="nominal":
    #             continue
    #         print "W:", wn, sample_var
    #         syst = wn
    #     if wn=="nominal" and sample_var=="nominal":
    #         syst_scenarios[sample]["nominal"]["none"] = hist
    #     else:
    #         systname, d = get_updown(syst)
    #         syst_scenarios[sample][systname][d] = hist

    # syst_scenarios = syst_scenarios.as_dict()
    # for sample, d1 in syst_scenarios.items():
    #     for scenario, d2 in d1.items():
    #         for direction, hist in d2.items():
    #             print sample, scenario, direction, hist
