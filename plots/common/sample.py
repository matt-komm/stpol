import ROOT
import logging
from plots.common.utils import filter_alnum, NestedDict
from plots.common.histogram import *
import numpy
from cross_sections import xs as sample_xs_map
import rootpy
from rootpy.plotting import Hist, Hist2D

import os

class HistogramException(Exception):
    pass
class TObjectOpenException(Exception):
    pass


def get_sample_name(filename):
    """
    Returns the sample name from the input file name
    """
    return filename.split("/")[-1].split(".")[0]


process_names = {
    "WJets_sherpa.*": "WJets_sherpa",
    "SingleMu.*": "SingleMu",
    "SingleEle.*": "SingleEle"
}
def get_process_name(sn):
    for k, v in process_names.items():
        if re.match(k, sn):
            return v
    return sn

logger = logging.getLogger("sample.py")
#logger.setLevel(logging.WARNING)

class Sample:
    def __del__(self):
        logger.debug("Closing sample %s" % self.name)
        self.tfile.Close()

    def __init__(self, name, file_name, tree_name = "Events", process_name=None):
        """
            name - The name of this sample. Typically the filename of the .root file containing the TTree
            file_name - The path to the file that you want to open as a TFile
            process_name - an optional parameter describing the physical process name. Used for e.g. cross-section retrieval
            tree_name - the name of the events TTree to open in the file
        """
        self.name = name
        if not process_name:
            self.process_name = name
        else:
            self.process_name = process_name
        self.tree_name = tree_name
        self.file_name = file_name
        try:
            self.tfile = ROOT.TFile(file_name)
            if not self.tfile:
                raise FileOpenException("Could not open TFile %s: %s" % (self.file_name, self.tfile))
        except Exception as e:
            raise e
        try:
            self.tree = self.tfile.Get("trees/"+tree_name)
        except Exception as e:
            raise TObjectOpenException("Could not open tree "+tree_name+" from file %s: %s" % (self.file_name, self.tfile))

        if not self.tree:
            raise TObjectOpenException("Could not open tree "+tree_name+" from file %s: %s" % (self.tfile.GetName(), self.tree))

        self.tree.SetBranchStatus("*", 1)
        self.tree.SetCacheSize(500*1024*1024)
        self.tree.AddBranchToCache("*")

        if self.tfile.Get("trees/WJets_weights"):
            self.tree.AddFriend("trees/WJets_weights")
        if self.tfile.Get("trees/MVA"):
            self.tree.AddFriend("trees/MVA")
        #self.tree.AddBranchToCache("*", 1)

        # add friend tree from another file containing mva values
        self.file_name_mva = file_name[:-5] + "_mva.root"
        if os.path.isfile(self.file_name_mva):
            self.tree.AddFriend("trees/MVA", self.file_name_mva)

        self.event_count = None
        self.event_count = self.getEventCount()
        if self.event_count<=0:
            logger.warning("Sample was empty: %s" % self.name)
            #raise Exception("Sample event count was <= 0: %s" % self.name)

        self.isMC = not self.file_name.split("/")[-1].startswith("Single")

        logger.debug("Opened sample %s with %d final events, %d processed" % (self.name, self.getEventCount(), self.getTotalEventCount()))
        logger.debug("Sample path is %s" % self.tfile.GetPath())

    def getEventCount(self):
        if self.event_count is None:
            self.event_count = self.tree.GetEntries()
        return self.event_count

    def getTree(self):
        return self.tree

    def getBranches(self):
        return [x.GetName() for x in self.tree.GetListOfBranches()]

    def getTotalEventCount(self):
        count_hist = self.tfile.Get("trees").Get("count_hist")
        if not count_hist:
            raise TObjectOpenException("Failed to open count histogram")
        return count_hist.GetBinContent(1)

    def lumiScaleFactor(self, lumi):
        expected_events = sample_xs_map[self.process_name] * lumi
        total_events = self.getTotalEventCount()
        scale_factor = float(expected_events)/float(total_events)
        return scale_factor

    def cacheEntries(self, name, cut_str, cache=0):
        """
        Creates a TEntryList event cache corresponding to a cut.
        This will allow subsequent operations to be speeded up if the same
        phase space is considered. Created in the mem dir of the sample file.

        Args:
            name: the name of the new event list. Should be unique in the
                ROOT sense of the word.
            cut_str: a cut string according to which to select the events.

        Returns:
            an instance of the created TEntryList.
        """
        self.tfile.cd()
        elist = self.tfile.Get(name)
        if not elist:
            logger.debug("Event list does not exist.")
            elist = ROOT.TEntryList(name, name)
        else:
            logger.debug("Event list exists.")
        self.tree.SetEntryList(cache)
        logger.debug("Before caching entries %d events" % self.tree.GetEntries())
        self.tree.Draw(">>" + elist.GetName(), cut_str, "entrylist")
        return elist

    def drawHistogram(self, var, cut_str, **kwargs):
        logger.debug("drawHistogram: var=%s, cut_str=%sm kwargs=%s" % (str(var), str(cut_str), str(kwargs)))
        if not isinstance(var, basestring):
            raise TypeError("Sample.drawHistogram expects variable as a plain string, but received: %s" % str(var))
        name = self.name + "_" + unique_name(var, cut_str, kwargs.get("weight"))

        #Internally use the same variable name, but for backwards compatibility still keep plot_range available
        #To be phased out
        binning = kwargs.get("plot_range", None)
        binning = kwargs.get("binning", binning)

        frac_entries = kwargs.get("frac_entries", 1.0)
        weight_str = kwargs.get("weight", None)
        dtype = kwargs.get("dtype", "F")
        entrylist = kwargs.get("entrylist", None)

        ROOT.gROOT.cd()
        ROOT.TH1F.AddDirectory(True)
        if len(binning)==3 and (isinstance(binning, tuple) or isinstance(binning, list)):
            hist = Hist(*list(binning), type=dtype)
        elif isinstance(binning, list):
            hist = Hist(binning, type=dtype)
        else:
            raise ValueError("binning must be a 3-tuple (nbins, min, max) or a list [low1, low2, ..., highN]")

        hist.Sumw2()
        name += "_" + hist.GetName()
        hist.SetName(name)

        draw_cmd = var + ">>%s" % hist.GetName()

        if entrylist:
            cut_str = "1.0"
            self.tree.SetEntryList(0)
            self.tree.SetEntryList(entrylist)
        else:
            self.tree.SetEntryList(0)

        if weight_str:
            cutweight_cmd = weight_str + " * " + "(" + cut_str + ")"
        else:
            cutweight_cmd = "(" + cut_str + ")"

        logger.debug("Calling TTree.Draw('%s', '%s')" % (draw_cmd, cutweight_cmd))

        n_entries = self.tree.Draw(draw_cmd, cutweight_cmd, "goff BATCH", int(self.getEventCount()*frac_entries))
        logger.debug("Histogram drawn with %d entries, integral=%.2f" % (n_entries, hist.Integral()))

        if n_entries<0:
            raise HistogramException("Could not draw histogram: %s" % self.name)

        if hist.Integral() != hist.Integral():
            raise HistogramException("Histogram had 'nan' Integral(), probably weight was 'nan'")
        if not hist:
            raise TObjectOpenException("Could not get histogram: %s" % hist)
        if hist.GetEntries() != n_entries:
            raise HistogramException("Histogram drawn with %d entries, but actually has %d" % (n_entries, hist.GetEntries()))
        ROOT.TH1F.AddDirectory(False)

        hist_new = hist.Clone(filter_alnum(name))
        logger.debug(list(hist_new.y()))

        return hist_new

    # This should be unified with the above!
    def drawHistogram2D(self, var_x, var_y, cut_str, **kwargs):
        logger.debug("drawHistogram: var_x=%s, var_y=%s, cut_str=%sm kwargs=%s" % (str(var_x), str(var_y), str(cut_str), str(kwargs)))
        name = self.name + "_" + unique_name(var_x+"_"+var_y, cut_str, kwargs.get("weight"))

        plot_range_x = kwargs.get("plot_range_x", None)
        plot_range_y = kwargs.get("plot_range_y", None)
        binning_x = kwargs.get("binning_x", None)
        binning_y = kwargs.get("binning_y", None)

        weight_str = kwargs.get("weight", None)
        dtype = kwargs.get("dtype", "F")

        ROOT.gROOT.cd()
        ROOT.TH2F.AddDirectory(True)
        if plot_range_x and plot_range_y:
            print "PR", plot_range_x, ":", plot_range_y
            hist = Hist2D(plot_range_x[0], plot_range_x[1], plot_range_x[2], plot_range_y[0], plot_range_y[1], plot_range_y[2], type=dtype, name="htemp")
        elif binning_x is not None and binning_y is not None:
            hist = Hist2D(binning_x, binning_y, type=dtype)
        else:
            raise ValueError("Must specify either plot_range_x=(nbins, min, max) and plot_range_y=(nbinbs, min, max) or binning_x=numpy.array(..) and binning_y=numpy.array(..)")

        hist.Sumw2()

        draw_cmd = var_y+":"+var_x + ">>%s" % hist.GetName()
        if weight_str:
            cutweight_cmd = weight_str + " * " + "(" + cut_str + ")"
        else:
            cutweight_cmd = "(" + cut_str + ")"

        logger.debug("Calling TTree.Draw('%s', '%s')" % (draw_cmd, cutweight_cmd))

        n_entries = self.tree.Draw(draw_cmd, cutweight_cmd, "goff BATCH")
        logger.debug("Histogram drawn with %d entries, integral=%.2f" % (n_entries, hist.Integral()))

        if n_entries<0:
            raise HistogramException("Could not draw histogram: %s" % self.name)

        if hist.Integral() != hist.Integral():
            raise HistogramException("Histogram had 'nan' Integral(), probably weight was 'nan'")
        if not hist:
            raise TObjectOpenException("Could not get histogram: %s" % hist)
        if hist.GetEntries() != n_entries:
            raise HistogramException("Histogram drawn with %d entries, but actually has %d" % (n_entries, hist.GetEntries()))
        ROOT.TH2F.AddDirectory(False)

        hist_new = hist.Clone(filter_alnum(name))

        return hist_new

    def getColumn(self, col, cut):
        N = self.tree.Draw(col, cut, "goff")
        N = int(N)
        if N < 0:
            raise Exception("Could not get column %s: N=%d" % (col, N))
        buf = self.tree.GetV1()
        arr = ROOT.TArrayD(N, buf)
        logger.debug("Column retrieved, copying to numpy array")
        out = numpy.copy(numpy.frombuffer(arr.GetArray(), count=arr.GetSize()))
        return out

    def getEntries(self, cut):
        return int(self.tree.GetEntries(cut))

    @staticmethod
    def fromFile(file_name,tree_name="Events"):
        sample_name = (file_name.split(".root")[0]).split("/")[-1]
        sample = Sample(sample_name, file_name, tree_name)
        return sample

    @staticmethod
    def fromDirectory(directory, out_type="dict", prefix="", tree_name="Events"):
        import glob
        file_names = glob.glob(directory + "/*.root")
        logger.debug("Sample.fromDirectory saw file names %s in %s" % (str(file_names), directory))
        if out_type=="list":
            samples = [Sample.fromFile(file_name, tree_name) for file_name in file_names]
        elif out_type=="dict":
            samples = dict((prefix+file_name.split("/")[-1].split(".")[0], Sample.fromFile(file_name, tree_name)) for file_name in file_names)
        else:
            raise ValueError("out_type must be 'list' or 'dict'")
        return samples

    def __repr__(self):
        return "<Sample(%s, %s)>" % (self.name, self.file_name)

    def __str__(self):
        return self.__repr__()

def is_mc(name):
    return not "SingleMu" in name

def get_paths(basedir=None, samples_dir="step3_latest", dataset=None):
    """
    basedir - the path where your STPOL directory is located
    samples_dir - the subdirectory in STPOL/...

    Returns a dictionary with the path structure of the samples in the format of
    out[dataset_name][mc/data][mu/ele][systematic_scenario][isolation] = "/path/to/samples"
    where dataset_name is the name/tag of the reprocessing
    """
    if not basedir:
        basedir = os.environ["STPOL_DIR"]
    datadirs = dict()
    fnames = NestedDict()
    for root, paths, files in os.walk(basedir + "/" + samples_dir):
        rootfiles = filter(lambda x: x.endswith(".root"), files)
        for fi in rootfiles:
            fn = root + "/" + fi

            spl = fn.split("/")
            try:
                idx = spl.index("mu")
            except ValueError:
                idx = spl.index("ele")

            spl = spl[idx:]
            lepton = spl[0]
            sample_type = spl[1]
            iso = spl[2]

            if len(spl)==6:
                systematic=spl.pop(3)
            elif len(spl)==5:
                systematic="NONE"
            else:
                raise ValueError("Couldn't parse filename: %s" % fn)
            _dataset = spl[3]
            fname = spl[4]

            fnames[_dataset][sample_type][lepton][systematic][iso] = root
            break
    if not dataset:
        return fnames.as_dict()
    elif dataset == "latest":
        return fnames["Jul15"].as_dict()
    else:
        return fnames[dataset].as_dict()

import unittest
class TestSample(unittest.TestCase):
    testfile = "step3_latest/mu/mc/iso/nominal/Jul15/T_t_ToLeptons.root"
    def testDrawHistogramFixedBinning(self):
        samp = Sample.fromFile(self.testfile)
        hi = samp.drawHistogram("cos_theta", "n_jets==2 && n_tags==1 && abs(eta_lj)>2.5", plot_range=[20, -1, 1])
        self.assertTrue(hi.Integral()>0)

    def testDrawHistogramVariableBinning(self):
        samp = Sample.fromFile(self.testfile)
        def dr(**kw):
            return samp.drawHistogram("cos_theta", "n_jets==2 && n_tags==1 && abs(eta_lj)>2.5", **kw)
        hi = dr(plot_range=[20, -1, 1])
        hi2 = dr(binning=[-1, 0, 0.25, 1])
        self.assertNotEqual(hi.GetName(), hi2.GetName())
        self.assertEqual(hi.Integral(), hi2.Integral())

    def testDrawHistogramCached(self):
        samp = Sample.fromFile(self.testfile)
        cut = "n_jets==2 && n_tags==1 && abs(eta_lj)>2.5"
        cache = samp.cacheEntries("2j1t", cut)
        hi = samp.drawHistogram("cos_theta", cut, plot_range=[20, -1, 1], entrylist=cache)
        self.assertTrue(hi.Integral()>0)
        for v in ["n_jets", "n_tags", "true_cos_theta", "met", "mt_mu", "mt_el"]:
            hi2 = samp.drawHistogram(v, cut, plot_range=[20, 0, 10], entrylist=cache)
            self.assertTrue(hi2.Integral()>0)
            logger.info("Mean = %.2f, RMS = %.2f" % (hi2.GetMean(), hi2.GetRMS()))

        hi3 = samp.drawHistogram("cos_theta", cut, plot_range=[20, -1, 1])
        self.assertNotEqual(hi.GetName(), hi3.GetName())
        self.assertEqual(list(hi.x()), list(hi3.x()))
        self.assertEqual(hi.GetEntries(), hi3.GetEntries())
