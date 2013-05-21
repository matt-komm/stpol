import ROOT
import logging
from plots.common.histogram import Histogram
from plots.common.utils import filter_alnum
import numpy

class Sample:
    def __init__(self, name, file_name):
        self.name = name
        self.file_name = file_name
        self.logger = logging.getLogger(str(self))

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
            self.logger.warning("Sample was empty: %s" % self.name)
            #raise Exception("Sample event count was <= 0: %s" % self.name)

        self.isMC = not self.file_name.startswith("Single")

        self.logger.info("Opened sample %s with %d final events, %d processed" % (self.name, self.getEventCount(), self.getTotalEventCount()))

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

    def drawHistogram(self, var, cut_str, dtype="float", **kwargs):
        name = self.name + "_" + Histogram.unique_name(var, cut_str, kwargs.get("weight"))

        plot_range = kwargs.get("plot_range", [100, 0, 100])

        weight_str = kwargs.get("weight", None)

        ROOT.gROOT.cd()
        if dtype=="float":
            hist = ROOT.TH1F("htemp", "htemp", plot_range[0], plot_range[1], plot_range[2])
        elif dtype=="int":
            hist = ROOT.TH1I("htemp", "htemp", plot_range[0], plot_range[1], plot_range[2])

        hist.Sumw2()

        draw_cmd = var + ">>htemp"

        if weight_str:
            cutweight_cmd = weight_str + " * " + "(" + cut_str + ")"
        else:
            cutweight_cmd = "(" + cut_str + ")"

        self.logger.debug("Calling TTree.Draw('%s', '%s')" % (draw_cmd, cutweight_cmd))

        n_entries = self.tree.Draw(draw_cmd, cutweight_cmd, "goff")
        self.logger.debug("Histogram drawn with %d entries, integral=%.2f" % (n_entries, hist.Integral()))

        if n_entries<0:
            raise HistogramException("Could not draw histogram")

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
        self.logger.debug("Column retrieved, copying to numpy array")
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
    def fromDirectory(directory):
        import glob
        file_names = glob.glob(directory + "/*.root")
        samples = [Sample.fromFile(file_name) for file_name in file_names]
        return samples

    def __repr__(self):
        return "<Sample(%s, %s)>" % (self.name, self.file_name)

    def __str__(self):
        return self.__repr__()
