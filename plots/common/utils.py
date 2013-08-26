import ROOT
from odict import OrderedDict
import string
import logging
logger = logging.getLogger("utils")
logger.setLevel(logging.WARNING)
import os
import re
import glob
from copy import deepcopy
import pdb
logger.debug('Importing rootpy...')
from rootpy.plotting.hist import Hist, Hist2D


class PatternDict(OrderedDict):
    def __getitem__(self, k):
        pat = re.compile(k)
        ret = []
        for key in self.keys():
            m = pat.match(key)
            if not m:
                continue
            if len(m.groups())>0:
                ret.append((m.groups(), dict.__getitem__(self, key)))
            else:
                ret.append(dict.__getitem__(self, key))
        if len(ret)==1:
            ret = ret[0]
        return ret


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

def get_file_list(merge_cmds, dir, fullpath=True, permissive=True):
    """
    Returns the file list from the input directory that matches the corresponding merge pattern
    dir - the input directory path
    merge_cmds - a dict with (string, list(regex patterns)) pairs specifying the merges
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

    # remove files ending in _mva.root, which contain friend trees with mva outputs
    out_files = filter(lambda x: not x.endswith("_mva.root"), out_files)

    #If you called this method and got nothing, then probably womething went wrong and you don't want the output
    if len(out_files)==0 and not permissive:
        raise Exception("Couldn't match any files to merge_cmds %s in directory %s" % (str(merge_cmds), dir))
    return sorted(out_files)

class PhysicsProcess:
    desired_plot_order_mc = ["diboson", "WJets", "DYJets", "TTJets", "tWchan", "schan", "tchan", "qcd"]
    desired_plot_order__mc_log = ["schan", "diboson", "tchan", "tWchan", "DYJets", "TTJets", "WJets", "qcd"]
    desired_plot_order = ["data"] + desired_plot_order_mc
    desired_plot_order_log = ["data"] + desired_plot_order__mc_log

    def __init__(self, name, subprocesses, pretty_name=None):
        self.name = name
        self.subprocesses = subprocesses
        if pretty_name:
            self.pretty_name = pretty_name
        else:
            self.pretty_name = name

    @classmethod
    def get_proc_dict(self, lepton_channel, systematic_scenario="nominal"):
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
        out_d["qcd"] = self.qcd
        out_d["tchan"] = self.tchan_d[systematic_scenario]
        return out_d

    @classmethod
    def get_merge_dict(self, in_d):
        """
        Returns a dictionary with
        {physic_process: [list, of, subsamples], ...}
        where all elements are strings.
        Used for merging.
        """
        out_d = OrderedDict()
        for name, process in in_d.items():
            out_d[name] = process.subprocesses
        return out_d

    @staticmethod
    def name_histograms(processes_d, hist_d):
        """
        Names the histograms in a dicionary according to the
        """
        for procname, hist in hist_d.items():
            try:
                hist.SetTitle(processes_d[procname].pretty_name)
                logger.debug("Setting histogram %s title to %s" % (hist, processes_d[procname].pretty_name))
            except KeyError: #QCD does not have a defined PhysicsProcess but that's fine because we take it separately
                logger.warning("Process %s not in the process dict %s" % (procname, str(processes_d.keys())))

    def getFiles(self, path):
        """
        Returns a list of files that match this process according to its subprocess patterns.

        Args:
            path: a path in the filesystem to recursively search for matches.

        Returns:
            a list of matching file names with full path.
        """
        pats = [re.compile(sp) for sp in self.subprocesses]
        out = []
        for root, dirs, items in os.walk(path):
            for it in items:
                if not it.endswith(".root"):
                    continue
                pname = it.split(".root")[0]
                for pat in pats:
                    if pat.match(pname):
                        fn = os.path.join(root, it)
                        out.append(fn)
        return out

    systematic = {}

PhysicsProcess.SingleMu = PhysicsProcess("SingleMu", ["SingleMu.*"], pretty_name="data")
PhysicsProcess.SingleEle = PhysicsProcess("SingleEle", ["SingleEle.*"], pretty_name="data")
PhysicsProcess.diboson = PhysicsProcess("diboson", ["[WZ][WZ]"], pretty_name="diboson")
PhysicsProcess.WJets_mg_exc = PhysicsProcess("WJets", ["W[1-4]Jets_exclusive"],
#    pretty_name="W(#rightarrow l #nu) + jets"
    pretty_name="W"
)
PhysicsProcess.WJets = PhysicsProcess.WJets_mg_exc
PhysicsProcess.DYJets = PhysicsProcess("DYJets", ["DYJets"],
    pretty_name="DY"
)
PhysicsProcess.TTJets_exc = PhysicsProcess("TTJets", ["TTJets_.*Lept"],
    pretty_name="t#bar{t}"
)
PhysicsProcess.TTJets = PhysicsProcess.TTJets_exc


PhysicsProcess.tWchan = PhysicsProcess("tW", ["T.*_tW"], pretty_name="tW")
PhysicsProcess.schan = PhysicsProcess("s", ["T.*_s"],
    pretty_name="s-channel"
)

"""
FIXME: Probably it would be better to organize the systematics differently
One PhysicsProcess should logically represent a group Feynman diagrams, e.g. t-channel
and the systematics
should be gathered somehow under the same PhysicsProcess
I've renamed it to tchan_d for now (d for dict) so that other codes would still work.
But we need to find a way to logically organize
Samples (root files)
physics processes: t-channel, W+jets etc
systematic scenarios
into a common structure
"""
PhysicsProcess.tchan_d = {}
PhysicsProcess.tchan_d["nominal"] = PhysicsProcess("tchan", ["T.*_t_ToLeptons"],
    pretty_name="signal (t-channel)"
)

PhysicsProcess.qcd = PhysicsProcess("qcd", ["qcd"],
    pretty_name="QCD"
)


PhysicsProcess.tchan_d["tchan_scale__down"] = PhysicsProcess("tchan_scale__down", ["T.*_t_ToLeptons_scaledown"],
    pretty_name="signal (t-channel)"
)

PhysicsProcess.tchan_d["tchan_scale__up"] = PhysicsProcess("tchan_scale__up", ["T.*_t_ToLeptons_scaleup"],
    pretty_name="signal (t-channel)"
)

PhysicsProcess.tchan_d["mass__down"] = PhysicsProcess("mass_down", ["T.*_t_ToLeptons_mass166_5"],
    pretty_name="signal (t-channel)"
)
#FIXME when sample available
PhysicsProcess.tchan_d["mass__up"] = PhysicsProcess("mass__up", ["T.*_t_ToLeptons_mass178_5", "T_t_ToLeptons_mass166_5"],
    pretty_name="signal (t-channel)"
)


PhysicsProcess.tchan_d["comphep"] = PhysicsProcess("tchan_comphep", ["TToB(.*)Nu_t-channel"],
    pretty_name="signal (t-channel) comphep"
)

PhysicsProcess.tchan_d["anomWtb-0100"] = PhysicsProcess("tchan_comphep_anomWtb-0100", ["TToB(.*)Nu_anomWtb-0100_t-channel"],
    pretty_name="anom. Wtb-0100 signal (t-channel)"
)

PhysicsProcess.tchan_d["anomWtb-unphys"] = PhysicsProcess("tchan_comphep_anomWtb_unphys", ["TToB(.*)Nu_anomWtb-unphys_t-channel"],
    pretty_name="anom. unphys. signal (t-channel)"
)

PhysicsProcess.tchan = PhysicsProcess.tchan_d["nominal"]


merge_cmds = PhysicsProcess.get_merge_dict(
    PhysicsProcess.get_proc_dict("mu")
)

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

def reorder(src, dest, reverse=True):
    """
    Reorders objects in the src dictionary according to the dest order list.

    Args:
        src: the source dictionary
        dest: a list with the desired order of the keys.

    Keywords:
        reverse: return the output in the reversed order.

    Returns:
        a list with the objects in the desired order.
    """
    ret = []
    if reverse:
        dest = list(reversed(dest))
    for i in dest[::-1]:
        ret.append(src[i])
    return ret

def merge_hists(hists_d, merge_groups, order=PhysicsProcess.desired_plot_order):
    """
    Merges the dictionary of input histograms according to the merge rules, which are specified
    as a key-value dictionary, where the key is the target and value a list of (regular) expressions
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
    logger.debug("merge_hists: input histograms %s" % str(hists_d))

    for merge_name, items in merge_groups.items():
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

    out_d_ordered = OrderedDict()

    for elem in order:
        try:
            out_d_ordered[elem] = out_d.pop(elem)
            if hasattr(PhysicsProcess, merge_name):
                if type(getattr(PhysicsProcess, merge_name)) is dict:   #take nominal name if multiple options
                    out_d_ordered[elem].SetTitle(getattr(PhysicsProcess, merge_name)["nominal"].pretty_name)
                else:   #regular
                    out_d_ordered[elem].SetTitle(getattr(PhysicsProcess, merge_name).pretty_name)
        except KeyError: #We don't care if there was an element in the order which was not present in the merge output
            pass

    #Put anything that was not in the order list simply to the end
    for k, v in out_d.items():
        out_d_ordered[k] = v

    return out_d_ordered


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


