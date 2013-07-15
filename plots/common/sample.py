import ROOT
import logging
from plots.common.histogram import Histogram
from plots.common.utils import filter_alnum
import numpy
from cross_sections import xs as sample_xs_map

class HistogramException(Exception):
    pass
class TObjectOpenException(Exception):
    pass


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

    def __init__(self, name, file_name, process_name=None):
        """
            name - The name of this sample. Typically the filename of the .root file containing the TTree
            file_name - The path to the file that you want to open as a TFile
            process_name - an optional parameter describing the physical process name. Used for e.g. cross-section retrieval
        """

        self.name = name
        if not process_name:
            self.process_name = name
        else:
            self.process_name = process_name
        self.file_name = file_name
        logger = logging.getLogger(str(self))

        try:
            self.tfile = ROOT.TFile(file_name)
            if not self.tfile:
                raise FileOpenException("Could not open TFile %s: %s" % (self.file_name, self.tfile))
        except Exception as e:
            raise e
        try:
            self.tree = self.tfile.Get("trees").Get("Events")
        except Exception as e:
            raise TObjectOpenException("Could not open tree Events from file %s: %s" % (self.file_name, self.tfile))

        if not self.tree:
            raise TObjectOpenException("Could not open tree Events from file %s: %s" % (self.tfile.GetName(), self.tree))

        self.tree.SetCacheSize(100*1024*1024)
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
        name = self.name + "_" + Histogram.unique_name(var, cut_str, kwargs.get("weight"))

        plot_range = kwargs.get("plot_range", None)
        binning = kwargs.get("binning", None)

        weight_str = kwargs.get("weight", None)
        dtype = kwargs.get("dtype", "float")

        ROOT.gROOT.cd()
        if plot_range is not None:
            hist_args = ["htemp", "htemp"] + plot_range
        elif binning is not None:
            hist_args = "htemp", "htemp", binning[0], binning[1]
        else:
            raise ValueError("Must specify either plot_range=(nbinbs, min, max) or binning=(nbins, numpy.array(..))")

        if dtype=="float":
            histfn = ROOT.TH1F
        elif dtype=="int":
            histfn = ROOT.TH1I
        else:
            raise ValueError("Unrecognized dtype: %s" % dtype)

        hist = histfn(*hist_args)

        hist.Sumw2()

        draw_cmd = var + ">>htemp"

        if weight_str:
            cutweight_cmd = weight_str + " * " + "(" + cut_str + ")"
        else:
            cutweight_cmd = "(" + cut_str + ")"

        logger.debug("Calling TTree.Draw('%s', '%s')" % (draw_cmd, cutweight_cmd))

        n_entries = self.tree.Draw(draw_cmd, cutweight_cmd, "goff")
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

        hist = hist_new
        hist.SetTitle(name)
        hist_ = Histogram()
        hist_.setHist(hist, histogram_entries=n_entries, var=var,
            cut=cut_str, weight=kwargs["weight"] if "weight" in kwargs.keys() else None,
            sample_name=self.name,
            sample_entries_total=self.getTotalEventCount(),
            sample_entries_cut=self.getEventCount(),

        )
        return hist_

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
    def fromFile(file_name):
        sample_name = (file_name.split(".root")[0]).split("/")[-1]
        sample = Sample(sample_name, file_name)
        return sample

    @staticmethod
    def fromDirectory(directory, out_type="list", prefix=""):
        import glob
        file_names = glob.glob(directory + "/*.root")
        logging.debug("Sample.fromDirectory saw file names %s in %s" % (str(file_names), directory))
        if out_type=="list":
            samples = [Sample.fromFile(file_name) for file_name in file_names]
        elif out_type=="dict":
            samples = dict((prefix+file_name.split("/")[-1].split(".")[0], Sample.fromFile(file_name)) for file_name in file_names)
        else:
            raise ValueError("out_type must be 'list' or 'dict'")
        return samples

    def __repr__(self):
        return "<Sample(%s, %s)>" % (self.name, self.file_name)

    def __str__(self):
        return self.__repr__()

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
