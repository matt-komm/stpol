import ROOT
import logging
from plots.common.utils import filter_alnum
from plots.common.histogram import *
import numpy
from cross_sections import xs as sample_xs_map
import rootpy
from rootpy.plotting import Hist, Hist2D

class HistogramException(Exception):
    pass
class TObjectOpenException(Exception):
    pass


def get_sample_name(filename):
    """
    Returns the sample name from the input file name
    """
    return filename.split("/")[-1].split(".")[0]

def get_process_name(sample_name):
    if sample_name.startswith("WJets_sherpa_nominal"):
        return "WJets_sherpa_nominal"
    else:
        return sample_name

logger = logging.getLogger("sample.py")
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
            #regex = re.compile("^W[1-4]Jets*")
            regex2 = re.compile("^Single*")
            #if regex2.match(self.process_name) is None:
            #    self.tree.AddFriend("trees/WJets_weights")
        except Exception as e:
            raise TObjectOpenException("Could not open tree "+tree_name+" from file %s: %s" % (self.file_name, self.tfile))

        if not self.tree:
            raise TObjectOpenException("Could not open tree "+tree_name+" from file %s: %s" % (self.tfile.GetName(), self.tree))

        self.tree.SetCacheSize(100*1024*1024)
        if self.tfile.Get("trees/WJets_weights"):
            self.tree.AddFriend("trees/WJets_weights")
        #self.tree.AddBranchToCache("*", 1)

        self.event_count = None
        self.event_count = self.getEventCount()
        if self.event_count<=0:
            logger.warning("Sample was empty: %s" % self.name)
            #raise Exception("Sample event count was <= 0: %s" % self.name)

        self.isMC = not self.file_name.split("/")[-1].startswith("Single")

        logger.debug("Opened sample %s with %d final events, %d processed" % (self.name, self.getEventCount(), self.getTotalEventCount()))

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

    def drawHistogram(self, var, cut_str, **kwargs):
        logger.debug("drawHistogram: var=%s, cut_str=%sm kwargs=%s" % (str(var), str(cut_str), str(kwargs)))
        name = self.name + "_" + unique_name(var, cut_str, kwargs.get("weight"))

        plot_range = kwargs.get("plot_range", None)
        binning = kwargs.get("binning", None)

        weight_str = kwargs.get("weight", None)
        dtype = kwargs.get("dtype", "F")

        ROOT.gROOT.cd()
        if plot_range:
            hist = Hist(*plot_range, type=dtype, name="htemp")
        elif binning is not None:
            hist = Hist(binning, type=dtype)
        else:
            raise ValueError("Must specify either plot_range=(nbinbs, min, max) or binning=(nbins, numpy.array(..))")

        hist.Sumw2()

        draw_cmd = var + ">>%s" % hist.GetName()

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
        hist_new = hist.Clone(filter_alnum(name))

        return hist_new

    def drawHistogram2D(self, var, var2, cut_str, **kwargs):
        logger.debug("drawHistogram: var=%s, var2=%s, cut_str=%sm kwargs=%s" % (str(var), str(var2), str(cut_str), str(kwargs)))
        name = self.name + "_" + unique_name(var+"_"+var2, cut_str, kwargs.get("weight"))

        plot_range_x = kwargs.get("plot_range_x", None)
        plot_range_y = kwargs.get("plot_range_y", None)
        binning_x = kwargs.get("binning_x", None)
        binning_y = kwargs.get("binning_y", None)

        weight_str = kwargs.get("weight", None)
        dtype = kwargs.get("dtype", "F")

        ROOT.gROOT.cd()
        if plot_range_x and plot_range_y:
            pass
            #TODO: make it work if needed
            #hist = Hist2D(*plot_range_x, *plot_range_y, type=dtype, name="htemp")
        elif binning_x is not None and binning_y is not None:
            hist = Hist2D(binning_x, binning_y, type=dtype)
        else:
            raise ValueError("Must specify either plot_range_x=(nbins, min, max) and plot_range_y=(nbinbs, min, max) or binning_x=numpy.array(..) and binning_y=numpy.array(..)")

        hist.Sumw2()

        draw_cmd = var+":"+var2 + ">>%s" % hist.GetName()

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
    def fromDirectory(directory, out_type="list", prefix="", tree_name="Events"):
        import glob
        file_names = glob.glob(directory + "/*.root")
        logging.debug("Sample.fromDirectory saw file names %s in %s" % (str(file_names), directory))
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

def load_samples(basedir=None):
    if not basedir:
        basedir = os.environ["STPOL_DIR"]
    datadirs = dict()
    datadirs["iso"] = "/".join((basedir, "step3_latest", "mu" ,"iso", "nominal"))
    #Use the anti-isolated data for QCD $STPOL_DIR/step3_latest/mu/antiiso/nominal/SingleMu.root
    # datadirs["antiiso"] = "/".join((basedir, "step3_latest", "mu" ,"antiiso", "nominal"))

    #Load all the samples in the isolated directory
    samples = Sample.fromDirectory(datadirs["iso"], out_type="dict", prefix="iso/")

    for name, sample in samples.items():
            sample.process_name = get_process_name(sample.name)
    # samples["antiiso/SingleMu"] = Sample.fromFile(datadirs["antiiso"] + "/SingleMu.root")

    return samples
