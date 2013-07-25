import ROOT
from odict import OrderedDict
import string
import logging
logger = logging.getLogger("utils")
import os
import re
import glob
from copy import deepcopy

from rootpy.plotting.hist import Hist, Hist2D


class NestedDict(OrderedDict):
    def __missing__(self, key):
        self[key] = NestedDict()
        return self[key]

    def as_dict(self):
        out_d = OrderedDict()
        for k, v in self.items():
            if isinstance(v, NestedDict):
                r = v.as_dict()
            else:
                r = v
            out_d[k] = r
        return out_d

def get_file_list(merge_cmds, dir, fullpath=True):
    """
    Returns the file list from the input directory that matches the corresponding merge pattern
    dir - the input directory path
    merge_cmds - a dict with string, list(regex patterns) pairs specifying the merges
    fullpath - return the full path of the file (or only the filename)
    returns - a list with the matched filenames
    """
    files = glob.glob("/".join([dir, "*.root"]))
    logger.debug("using directory %s" % dir)
    logger.debug("dir contains %s" % files)
    out_files = []
    for cmds in merge_cmds.values():
        for pat in cmds:
            out_files += filter(lambda x: re.match(pat, x.split("/")[-1]), files)
    if not fullpath:
        out_files = map(lambda x: x.split("/")[-1], out_files)
    return out_files

class PhysicsProcess:
    desired_plot_order = ["data", "diboson", "WJets", "DYJets", "TTJets", "tWchan", "schan", "tchan"]
    desired_plot_order_log = ["data", "schan", "diboson", "tchan", "tWchan", "DYJets", "TTJets", "WJets" ]
    def __init__(self, name, subprocesses, pretty_name=None):
        self.name = name
        self.subprocesses = subprocesses
        if pretty_name:
            self.pretty_name = pretty_name
        else:
            self.pretty_name = name

    @classmethod
    def get_dict(self, lepton_channel, systematic_channel="nominal"):
        """
        Returns the collection of PhysicsProcesses, that contain samples to be merged for the
        particular lepton channel and systematic scenario.
        """
        out_d = OrderedDict()
        if lepton_channel=="mu":
            out_d["data"] = self.SingleMu
        elif lepton_channel=="ele":
            out_d["data"] = self.SingleEle
        else:
            raise ValueError("Unrecognized lepton channel: %s" % lepton_channel)
        out_d["diboson"] = self.diboson
        out_d["WJets"] = self.WJets_mg_exc
        out_d["DYJets"] = self.DYJets
        out_d["TTJets"] = self.TTJets_exc
        out_d["tWchan"] = self.tWchan
        out_d["schan"] = self.schan
        out_d["tchan"] = self.tchan
        return out_d

    @classmethod
    def get_merge_dict(self, lepton_channel="mu", **kwargs):
        """
        Returns a dictionary with
        {physic_process: [list, of, subsamples], ...}
        where all elements are strings.
        Used for merging.
        """
        in_d = self.get_dict(lepton_channel, **kwargs)
        out_d = OrderedDict()
        for name, process in in_d.items():
            out_d[name] = process.subprocesses
        return out_d
    systematic = {}

PhysicsProcess.SingleMu = PhysicsProcess("SingleMu", ["SingleMu.*"], pretty_name="data")
PhysicsProcess.SingleEle = PhysicsProcess("SingleEle", ["SingleEle.*"], pretty_name="data")
PhysicsProcess.diboson = PhysicsProcess("diboson", ["[WZ][WZ]"])
PhysicsProcess.WJets_mg_exc = PhysicsProcess("WJets", ["W[1-4]Jets_exclusive"], pretty_name="W(#rightarrow l #nu) + j (mg)")
#PhysicsProcess.WJets_mg_inc = PhysicsProcess("WJets", ["W[1-4]Jets_exclusive"], pretty_name="W(#rightarrow l #nu,qq) + j (mg)")
PhysicsProcess.DYJets = PhysicsProcess("DYJets", ["DYJets"], pretty_name="DY-jets")
PhysicsProcess.TTJets_exc = PhysicsProcess("TTJets", ["TTJets_.*Lept"], pretty_name="t#bar{t} (#rightarrow ll, lq) (mg)")
PhysicsProcess.tWchan = PhysicsProcess("tW", ["T.*_tW"], pretty_name="tW-channel")
PhysicsProcess.schan = PhysicsProcess("s", ["T.*_s"], pretty_name="s-channel")
PhysicsProcess.tchan = PhysicsProcess("tchan", ["T.*_t_ToLeptons"], pretty_name="t-channel")

#for syst in ["scaleup", "scaledown"]:
#    for nominal in [PhysicsProcess.tchan]:
#        proc = deepcopy(nominal)
#        proc.subprocesses = [x+"_%s" % syst for x in proc.subprocesses]
#        PhysicsProcess.systematic[syst][proc.name] = proc

merge_cmds = PhysicsProcess.get_merge_dict(lepton_channel="mu")

def lumi_textbox(lumi, pos="top-left", state='preliminary', line2=None):
    """
    This method creates and draws the "CMS Preliminary" luminosity box,
    displaying the lumi in 1/fb and the COM energy.

    **Mandatory arguments:
    lumi - the integrated luminosity in 1/pb

    **Optional arguments:
    pos - a string specifying the position of the lumi box.

    state - which analysis state is it: preliminary, internal, or '' for final publication

    line2 - optional line 2 to show for example if this is e-channel or mu-channel

    **returns:
    A TPaveText instance with the lumi information
    """
    if pos=="top-left":
        coords = [0.2, 0.86, 0.66, 0.91]
    if pos=="top-right":
        coords = [0.5, 0.86, 0.96, 0.91]

    if line2:
        coords[1]-=0.05

    text = ROOT.TPaveText(coords[0], coords[1], coords[2], coords[3], "NDC")
    text.AddText("CMS %s #sqrt{s} = 8 TeV, #int L dt = %.1f fb^{-1}" % (state, float(lumi)/1000.0))
    if line2:
        text.AddText(line2)
    text.SetShadowColor(ROOT.kWhite)
    text.SetLineColor(ROOT.kWhite)
    text.SetFillColor(ROOT.kWhite)
    text.Draw()
    return text

def merge_hists(hists_d, merge_groups, order=PhysicsProcess.desired_plot_order):
    """
    Merges the dictionary of input histograms according to the merge rules, which are specified
    as a key-value dictionary, where the key is the target and value a list of (regex) expressions
    to merge under the key.
    For example, {
        "WJets": ["W[1-4]Jets_.*"],
        "tchan": ["T_t_ToLeptons", "Tbar_t_ToLeptons"],
    } will perform the corresponding merges. The values of the merge dict are the keys of the input histogram dict.

    returns - a dictionary with the merged histograms. Optionally you can specify a list with the desired order of the keys.
    """
    for v in hists_d.values():
        if not isinstance(v, Hist) and not isinstance(v, ROOT.TH1I) and not isinstance(v, ROOT.TH1F) and not isinstance(v, Hist2D) and not isinstance(v, ROOT.TH2I) and not isinstance(v, ROOT.TH2F):
            raise ValueError("First argument(hists_d) must be a dict of Histograms, but found %s" % v)

    out_d = OrderedDict()
    logging.debug("merge_hists: input histograms %s" % str(hists_d))
    
    
    for name in order:
        if name in merge_groups.keys():
            merge_name=name
            items=merge_groups[name]
        else:
            continue
        logger.debug("Merging %s to %s" % (items, merge_name))

        matching_keys = []
        for item in items:
            t = filter(lambda x: re.match(item + "$", x), hists_d.keys())
            matching_keys += t
            logger.debug("Matched %s to %s" % (str(t), item))
        if len(matching_keys)==0:
            continue
        logger.debug("Merging matched %s" % str(matching_keys))
        hist = hists_d[matching_keys[0]].Clone()
        for item in matching_keys[1:]:
            hist.Add(hists_d[item])

        out_d[merge_name] = hist
        out_d[merge_name].SetTitle(merge_name)
        out_d[merge_name].SetName(merge_name)
    return out_d


def filter_alnum(s):
    """Filter out everything except ascii letters and digits"""
    return filter(lambda x: x in string.ascii_letters+string.digits + "_", s)

def get_hist_int_err(hist):
    """
    Returns (integral, err) of the TH1 hist.
    """
    err = ROOT.Double()
    integral = hist.IntegralAndError(1, hist.GetNbinsX(), err)
    return (float(integral), float(err))

def get_max_bin(hists):
    """
    Returns the maximum value of the bin heights in the list of TH1 objects
    """
    return max([h.GetMaximum() for h in hists])

def get_sample_name(arg):
    if isinstance(arg, ROOT.TFile):
        return get_sample_name(str(arg.GetPath()))
    else:
        return arg.split("/")[-1].split(".")[0]

def get_sample_dict(path, sample_d):
    out_d = OrderedDict()
    for (name, samples) in sample_d.items():
        files = []
        for samp in samples:
            fn = path + "/" + samp + ".root"
            try:
                fi = ROOT.TFile(fn)
            except Exception as e:
                logging.getLogger().warning("Could not open sample %s: %s" % (fn, str(e)))
                fi = None
            if fi:
                files.append(fi)
        out_d[name] = files
    return out_d

def mkdir_p(d):
    try:
        os.makedirs(d)
    except Exception as e:
        logging.debug(str(e))
    return

def get_stack_total_hist(thstack):
    return sum([h for h in thstack.GetHists()])

def filter_hists(indict, pat):
    """
    Returns the values of the dictionary whose keys match the pattern. The return type is a dictionary, whose keys are the first group of the pattern.
    Example: filter_hists({"asd/mystuff":1}, ".*/(mystuff)") will return {"mystuff":1}
    indict - a dictionary
    pat - a regex pattern that has at least 1 parenthesized group
    """
    out = OrderedDict()
    for k,v in indict.items():
        m = re.match(pat, k)
        if not m:
            continue
        out[m.group(1)] = v
    return out

def escape(s):
    return re.sub("[\/ \( \) \\ \. \* \+ \> \< \# \{ \}]", "", s)

