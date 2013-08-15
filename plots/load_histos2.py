import re, glob, sys
from collections import deque
from rootpy.io import File
import itertools
from plots.common.utils import NestedDict, PatternDict
import ROOT
import logging

logger = logging.getLogger("load_histos2")
logger.setLevel(logging.DEBUG)

def load_file(fnames, pats):
    res = {}
    ret = {}
    for patn, pat in pats.items():
        res[patn] = re.compile(pat)
        ret[patn] = PatternDict()

    n = 0
    for fn in fnames:
        fi = File(fn)
        ROOT.gROOT.cd()
        for root, dirs, items in fi.walk():
            for it in items:
                n += 1
                # if n%10==0:
                #     sys.stdout.write(".")
                #     sys.stdout.flush()
                if n%25000 == 0:
                    logger.debug("%d, %s, %s" % (
                            n,
                            str([(k, len(ret[k].keys())) for k in ret.keys()]),
                            fi.GetPath()
                        )
                    )
                    #logger.debug(root)
                for patn, pat in res.items():
                    if pat.match(root):
                        ret[patn][root] = fi.Get(
                            "/".join(
                                [root, it]
                            )
                        ).Clone()
        fi.Close()
    logger.info("Matched %d histograms to pattern %s" % (len(ret.keys()), pat.pattern))
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
    fnames = glob.glob("hists/e/mu/*.root")

    base = ".*/Aug4_0eb863_full/mu/"
    cut = "channel/mu/mu__iso/jet/2j/tag/1t/met/met__mtw/signalenr/cutbased/mtop/mtop__SR/etalj/etalj__g2_5/"
    
    pat_mc_varsamp = ""
    pat_mc_varsamp += base
    pat_mc_varsamp += "mc_syst/iso/(.*)/Jul15/(.*)/"
    pat_mc_varsamp += cut
    pat_mc_varsamp += "(weight__nominal__mu)/abs_eta_lj"

    pat_mc_varproc = ""
    pat_mc_varproc += base
    pat_mc_varproc += "mc/iso/(.*)/Jul15/(.*)/"
    pat_mc_varproc += cut
    pat_mc_varproc += "(weight__nominal__mu)/abs_eta_lj"

    pat_data = ""
    pat_data += base
    pat_data += "(data)/iso/.*/(.*)/"
    pat_data += cut
    pat_data += "(weight__unweighted.*)/abs_eta_lj"

    pat_mc_nom = ""
    pat_mc_nom += base
    pat_mc_nom += "mc/iso/(nominal)/Jul15/(.*)/"
    pat_mc_nom += cut
    pat_mc_nom += "(.*)/abs_eta_lj"


    rets_data = load_file(fnames,
        {
            "mc_varsamp": pat_mc_varsamp,
            "mc_varproc": pat_mc_varproc,
            "mc_nom": pat_mc_nom,
            "data": pat_data,
        }
    )
    # for fi in files:
    #     fi.Close()

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
