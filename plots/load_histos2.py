import re, glob, sys, os
from collections import deque
from rootpy.io import File
from rootpy.plotting import Hist
import itertools
from plots.common.utils import NestedDict, PatternDict
import ROOT
import logging

logger = logging.getLogger("load_histos2")
logger.setLevel(logging.INFO)
import pdb

# import plots.common.utils
# plots.common.utils.logger.setLevel(logging.DEBUG)

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
        logger.debug("Processing file %s" % fn)
        for root, dirs, items in fi.walk():
            for it in items:
                n += 1
                # if n%10==0:
                #     sys.stdout.write(".")
                #     sys.stdout.flush()
                if n%25000 == 0:
                    logger.info("%d, %s, %s" % (
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
    logger.info("Matched %s histograms" % (str([(k, len(ret[k].keys())) for k in ret.keys()])))
    return ret

from SingleTopPolarization.Analysis import sample_types
def get_syst_from_sample_name(sn):
    """
    Gets the sample base name (process name), systematic
    scenario name and variation direction from the name
    of a systematically variated (at production) sample.
    
    For example:
        'TTJets_FullLept_scaledown' =>
            ('TTJets_FullLept', 'ttbar_scale', 'down')

        'WJetsToLNu_matchingup' =>
            ('WJetsToLNu', 'wjets_matching', 'down')
        
        
        'T_t_ToLeptons_mass178_5' =>
            ('T_t_ToLeptons', 'mass', 'up')
    
    Since there is no standard naming scheme for the
    systematic samples (yet), this mapping must be hardcoded
    at the moment (within reason)
    
    Args:
        sn: a string with the sample name (the filename with
            the .root suffix removed)
            
    Returns:
        A 3-tuple with (process_name, systematic_name, systematic_dir)
    """
    
    si = sample_types.sample_infos[sn]

    #Check if the sample is MC and of the SYST type
    if si.has("mc") and si.has("syst"):
        
        #All of these can be handled in the same way
        for k in ["mass", ".*scale", ".*matching", "sig_anom", "sig_gen"]:
            m = si.has(k + "__.*", ret=True)
            if len(m)==1:
                m = m[0]
                syst, systdir = m.split("__")
                return (si.subprocess, syst, systdir)
            
    #If you called this method and got here: problems
    raise Exception("Unhandled systematic: %s" % sn)        

def get_updown(syst):
    syst = syst.lower()
    
    if syst=="unweighted" or syst == "nominal":
        return syst, None
    idx = None
    for d in ["up", "down"]:
        if d in syst:
            idx = syst.index(d)
            break
    if not idx:
        raise ValueError("Unrecognized syst: %s" % syst)
    
    systtype = syst[0:idx]
    systtype = systtype.strip("_")#.strip("weight__")
    systdir = d
    return systtype, systdir

def get_all_systs(syst_scenarios):
    allsysts = []
    for sampn, systd in syst_scenarios.items():
        allsysts += systd.keys()
    allsysts = list(sorted(list(set(allsysts))))
    return allsysts

def split_name(name):
    spl = name.split("__")
    var = spl[0]
    sample = spl[1]
    
    systtype = "nominal"
    systdir = None
    
    if len(spl)>2:
        systtype = spl[2]
    if len(spl)>3:
        systdir = spl[3]
        
    return {
        "var":var, "sample":sample,
        "type":systtype, "dir":systdir
    }

def syst_overview(hists):
    from tabulate import tabulate
    diffs = NestedDict()
    table = []
    for k1, v1 in hists:
        spl1 = hname_decode(k1)
        if spl1["type"]=="nominal":
            for k2, v2 in hists:
                spl2 = hname_decode(k2)
                if not spl2["sample"]==spl1["sample"]:
                    continue
                h = v1-v2
                diffs[spl2["sample"]][spl2["type"]][spl2["dir"]] = h
                table.append([
                    "N" if sum(v2.errors())<0.00001 else "Y",
                    "N" if h.Integral()<0.00001 and  h.GetRMS()<0.00001 else "Y",
                    spl1["sample"], spl2["type"], spl2["dir"],
                    "%.2E" % h.Integral(),
                    "%.2E" % h.GetMean(),
                    "%.2E" % h.GetRMS(),
                    "%.2E" % sum(v2.errors()),
                ])
    table.sort(key=lambda x: (x[2], x[3]))
    table = [["available", "non-zero", "sample", "syst", "dir", "int(d)", "mean(d)", "RMS(d)", "sumerr(e)"]] + table
    print tabulate(table, headers="firstrow")

def hname_encode(varname, sampn, systname=None, systdir=None):
    l = [varname, sampn]
    if systname:
        l.append(systname)
    if systdir:
        l.append(systdir)
    return "__".join(l)

def hname_decode(hname):
    spl = hname.split("__")
    var = spl[0]
    sample = spl[1]
    
    systtype = "nominal"
    systdir = None
    
    if len(spl)>2:
        systtype = spl[2]
    if len(spl)>3:
        systdir = spl[3]
        
    return {
        "var":var, "sample":sample,
        "type":systtype, "dir":systdir
    }
    
def set_missing_hist(hist):
    hist.SetName(hist.GetName()+"__MISSING")
    #for i in range(hist.GetNbinsX()):
    #    hist.SetBinError(i, 0)

def load_theta_format(inf, styles=None):
    from plots.common.sample_style import Styling
    if not styles:
        styles = {}

    hists = SystematicHistCollection()
    fi = File(inf)
    ROOT.gROOT.cd()
    #rate_sfs = load_fit_results("final_fit/results/%s.txt" % fit_results[channel])
    for root, dirs, items in fi.walk():
        for it in items:

            hn = hname_decode(it)
            variable, sample, syst, systdir = hn["var"], hn["sample"], hn["type"], hn["dir"]

            k = os.path.join(root, it)
            it = fi.Get(k).Clone()

            #Skip anything not a histogram
            if not isinstance(it, ROOT.TH1F):
                continue

            if sample == "DATA":
                sample = sample.lower()

            if sample.lower() != "data":
                sty = styles.get(sample.lower(), sample)
                try:
                    Styling.mc_style(it, sty)
                except:
                    logger.debug("Could not style histogram from sample: %s" % sample)
            else:
                Styling.data_style(it)
            hists[variable][syst][systdir][sample]= it

    #hists = hists.as_dict()
    fi.Close()

    return hists

class SystematicHistCollection(NestedDict):

    def items_flat(self):
        for variable, h1 in super(SystematicHistCollection, self).items():
            for syst, h2 in h1.items():
                for systdir, h3 in h2.items():
                    for sample, h4 in h3.items():
                        yield ((variable, sample, syst, systdir), h4)

if __name__=="__main__":

    import cPickle as pickle
    import os

    varname = "cos_theta"
    channel="mu"
    fnames = glob.glob("hists/e/mu/*.root")

    cutstr = "channel/mu/%s__iso/jet/2j/tag/1t/met/met__mtw/signalenr/mva/.*tight.*/" % channel
    

    cut = cutstr
    cut_antiiso = cut.replace("iso", "antiiso")
    base = ".*/Aug4_0eb863_full/%s/"%channel

    pat_mc_varsamp = ""
    pat_mc_varsamp += base
    pat_mc_varsamp += "mc_syst/iso/(.*)/Jul15/(.*)/"
    pat_mc_varsamp += cut
    pat_mc_varsamp += "(weight__nominal__%s)/"%channel + varname

    pat_mc_varproc = ""
    pat_mc_varproc += base
    pat_mc_varproc += "mc/iso/(.*)/Jul15/(.*)/"
    pat_mc_varproc += cut
    pat_mc_varproc += "(weight__nominal__%s)/"%channel + varname

    pat_data = ""
    pat_data += base
    pat_data += "(data)/iso/.*/(Single.*)/"
    pat_data += cut
    pat_data += "(weight__unweighted.*)/" + varname

    pat_mc_nom = ""
    pat_mc_nom += base
    pat_mc_nom += "mc/iso/(nominal)/Jul15/(.*)/"
    pat_mc_nom += cut
    pat_mc_nom += "(weight__.*__%s)/"%channel + varname

    pat_data_antiiso = ""
    pat_data_antiiso += base
    pat_data_antiiso += "data/antiiso/.*/(.*)/"
    pat_data_antiiso += cut_antiiso
    pat_data_antiiso += "(weight__unweighted.*)/" + varname

    rets_data = load_file(fnames,
        {
            "mc_varsamp": pat_mc_varsamp,
            "mc_varproc": pat_mc_varproc,
            "mc_nom": pat_mc_nom,
            "data": pat_data,
            "data_antiiso": pat_data_antiiso,
        }
    )

    hists = {}
    hsources = (
        rets_data["data"][pat_data]+
        rets_data["mc_nom"][pat_mc_nom]+
        rets_data["mc_varproc"][pat_mc_varproc]+
        rets_data["mc_varsamp"][pat_mc_varsamp]
    )

    hqcd = sum([x[1] for x in rets_data["data_antiiso"][pat_data_antiiso]])
    
    hqcd_up = hqcd.Clone()
    hqcd_up.Scale(2.0)
    
    hqcd_down = hqcd.Clone()
    hqcd_down.Scale(0.5)

    #Add the variated data-driven QCD templates
    hsources += [
        (("data", "qcd", "weight__unweighted"), hqcd),
        (("data", "qcd", "weight__qcd_yield_up"), hqcd_up),
        (("data", "qcd", "weight__qcd_yield_down"), hqcd_down),
    ]

        #f = open('temp.pickle','wb')
        #pickle.dump(hsources, f)
        #f.close()

    #load the histos from the temporary pickle
    #f = open('temp.pickle','rb')
    #hsources = pickle.load(f)

    syst_scenarios = NestedDict()
    for (sample_var, sample, weight_var), hist in hsources:
        if sample_var=="data":
            pdb.set_trace() 
        if "__ele" in weight_var:
            continue
        
        if ".root" in sample:
            sample = sample[:sample.index(".root")]
        
        if "__" in weight_var:
            spl = weight_var.split("__")
            wn = spl[1]
        else:
            wn = weight_var
        sample_var = sample_var.lower()
        wtype = None
        wdir = None
        stype = None
        sdir = None

        syst = None

        # if sample=="qcd":
        #     pdb.set_trace()

        #Nominal weight, look for variated samples
        if wn=="nominal":
            syst = sample_var
        elif wn=="unweighted":
            syst="unweighted"
        else:
            #Variated weight, use only nominal sample or data in case of data-driven shapes
            if not (sample_var=="nominal" or sample_var=="data"):
                continue
            #print "W:", wn, sample_var, sample
            syst = wn
        if wn=="nominal" and sample_var=="nominal":
            syst_scenarios[sample]["nominal"][None] = hist

        #A systematic scenario which has a separate systematic sample
        elif sample_var == "syst":
            r = get_syst_from_sample_name(sample)
            if not r:
                continue
            sample, systname, d = r
            #sample = map_syst_sample_to_nominal(sample)
            syst_scenarios[sample][systname][d] = hist
        
        else:
            systname, d = get_updown(syst)
            syst_scenarios[sample][systname][d] = hist

    ######################################
    ### Save systematics, fill missing ###
    ######################################

    #T_t_ToLeptons mass_up is missing, take the mass down and flip the difference with the nominal
    mnomt = syst_scenarios["T_t_ToLeptons"]["nominal"][None].Clone()
    mdownt = syst_scenarios["T_t_ToLeptons"]["mass"]["down"].Clone()
    mupt = (mnomt+mnomt-mdownt)
    syst_scenarios["T_t_ToLeptons"]["mass"]["up"] = mupt

    #Create the output file
    of = ROOT.TFile("hists_out.root", "RECREATE")
    of.cd()

    #Get the list of all possible systematic scenarios that we have available

    allsyts = get_all_systs(syst_scenarios)

    for sampn, h1 in syst_scenarios.items():
        
        #Consider all the possible systematic scenarios
        for systname in allsyts:
            
            #If we have it available, fine, use it
            if systname in h1.keys():
                h2 = h1[systname]
                
            #If not, in case of MC and a non-trivial variation
            elif not sampn.startswith("Single") and systname not in ["unweighted", "nominal"]:
                
                #Try to get the unvariated template as a placeholder
                h = h1.get("nominal", None)
                if not h:
                    h = h1.get("unweighted", None)
                
                #Our convention is that even the unvariated template is a dict with a single
                #key for the direction of variation, which is 'None'
                h = h[None]
                
                #Add placeholder templates
                for systdir in ["up", "down"]:
                    h = h.Clone(hname_encode(varname, sampn, systname, systdir))
                    
                    set_missing_hist(h)
                    
                    #Save to file
                    h.SetDirectory(of)
                    h.Write()
                continue
            else:
                continue
            for systdir, h in h2.items():
                if systdir==None and systname=="nominal" or not sample_types.is_mc(sampn):
                    h = h.Clone(hname_encode(varname, sampn))
                elif systdir==None and systname=="unweighted":
                    h = h.Clone(hname_encode(varname, sampn, "unweighted"))
                else:
                    h = h.Clone(hname_encode(varname, sampn, systname, systdir))
                h.SetDirectory(of)
                h.Write()
    nkeys = len(of.GetListOfKeys())
    logger.info("Saved %d histograms to file %s" % (nkeys, of.GetPath()))
    of.Close()

    ########################
    ### Load systematics ###
    ########################
    of = File("hists_out.root")
    hists = dict()
    ROOT.gROOT.cd()
    for k in of.GetListOfKeys():
        hists[k.GetName()] = of.Get(k.GetName()).Clone()
        hists[k.GetName()].Rebin(5)
    logger.info("Loaded %d histograms from file %s" % (len(hists), of.GetPath()))
    of.Close()

    ########################
    ###      Merge       ###
    ########################
    from plots.common.utils import merge_hists, PhysicsProcess
    merge_cmds = PhysicsProcess.get_merge_dict(
        PhysicsProcess.get_proc_dict("mu")
    )
    hsysts = NestedDict()
    for k, v in hists.items():
        spl = split_name(k)
        hsysts[spl["type"]][spl["dir"]][spl["sample"]] = v
    hsysts = hsysts.as_dict()
    of = ROOT.TFile("hists_out_merged.root", "RECREATE")
    of.cd()

    skipped_systs = ["wjets_matching", "wjets_scale", "sig_gen", "sig_anom"]
    for syst, h1 in hsysts.items():
        if syst in skipped_systs:
            continue
        for sdir, h2 in h1.items():
            hmc = merge_hists(h2, merge_cmds)
            for hn, h in hmc.items():
                if syst=="nominal" or syst=="unweighted":
                    h.SetName("__".join([spl["var"], hn]))
                else:
                    h.SetName("__".join([spl["var"], hn, syst, sdir]))
                h.SetDirectory(of)
                h.Write()
    nkeys = len(of.GetListOfKeys())
    logger.info("Saved %d histograms to file %s" % (nkeys, of.GetPath()))
    of.Close()

    hists = load_theta_format("hists_out_merged.root")
    for k, v in hists.items_flat():
        print k, v

    # for k1, v1 in syst_scenarios.items():
    #     for k2, v2 in v1.items():
    #         for k3, v3 in v2.items():
    #             print k1, k2, k3, v3