import ROOT
from plots.common.utils import filter_alnum
from cross_sections import xs as sample_xs_map
import logging
from rootpy.io.file import File
import re
import pickle
from plots.common.utils import mkdir_p, escape
logger = logging.getLogger("histogram")

try:
    import rootpy
except Exception as e:
    logger.error("rootpy needed: install rootpy using setup/install-pylibs.sh")
    raise e
try:
    from sqlalchemy.ext.declarative import declarative_base
    Base = declarative_base()
    from sqlalchemy import Column, Integer, String
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
except Exception as e:
    logger.error("SQLAlchemy needed: please install by running setup/install-pylibs.sh")
    raise e


class Histogram(Base):
    __tablename__ = "histograms"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    histogram_entries = Column(Integer)

    var = Column(String)
    cut = Column(String)
    weight = Column(String)
    sample_name = Column(String)
    sample_entries_cut = Column(Integer)
    sample_entries_total = Column(Integer)
    hist_dir = Column(String)
    hist_file = Column(String)

    def __init__(self, *args, **kwargs):
        super(Histogram, self).__init__(*args, **kwargs)
        self.pretty_name = self.name
        self.hist = None

    @staticmethod
    def make(thist, **kwargs):
        hist = Histogram()
        hist.setHist(thist, **kwargs)
        return hist

    def setHist(self, hist, **kwargs):
        self.hist = hist
        self.name = str(self.hist.GetName())
        self.histogram_entries = int(kwargs.get("histogram_entries", -1))
        self.var = kwargs.get("var")
        self.cut = kwargs.get("cut", None)
        self.weight = kwargs.get("weight", None)
        self.sample_name = kwargs.get("sample_name")
        self.sample_entries_cut = kwargs.get("sample_entries_cut", None)
        self.sample_entries_total = kwargs.get("sample_entries_total", None)
        self.integral = None
        self.err = None
        self.is_normalized = False
        self.update()

    def calc_int_err(self):
        err = ROOT.Double()
        integral = self.hist.IntegralAndError(1, self.hist.GetNbinsX(), err)
        self.err = err
        self.integral = integral
        return (self.integral, self.err)

    def normalize(self, target=1.0):
        if self.hist.Integral()>0:
            self.hist.Scale(target/self.hist.Integral())
            self.is_normalized = True
        else:
            logger.warning("Histogram %s integral=0, not scaling." % str(self))

    # def normalize_lumi(self, lumi=1.0):
    #     expected_events = sample_xs_map[self.sample_name] * lumi
    #     total_events = self.sample_entries_total
    #     scale_factor = float(expected_events)/float(total_events)
    #     self.hist.Scale(scale_factor)

    def update(self, file=None, dir=None):
        self.name = str(self.hist.GetName())
        if file and dir:
            self.hist_dir = str(dir.GetName())
            self.hist_file = str(file.GetName())
        else:
            try:
                self.hist_dir = self.hist.GetDirectory().GetName()
            except ReferenceError as e:
                self.hist_dir = None
            try:
                self.hist_file = self.hist.GetDirectory().GetFile().GetName()
            except ReferenceError as e:
                self.hist_file = None
        if dir:
            self.hist.SetDirectory(dir)
        self.pretty_name = str(self.hist.GetTitle())

    def loadFile(self):
        self.fi = ROOT.TFile(self.hist_file)
        #ROOT.gROOT.cd()
        self.hist = self.fi.Get(self.hist_dir).Get(self.name)#.Clone()
        #self.fi.Close()
        self.update()

    def __repr__(self):
        return "<Histogram(%s, %s, %s)>" % (self.var, self.cut, self.weight)

    def __add__(self, other):
        hi = self.hist.Clone(self.name + "_plus_" + other.name)
        hi.Add(other.hist)
        return Histogram.make(hi)
    
    @staticmethod
    def sum(histograms):
        if len(histograms)>0:
            hi = histograms[0]
        else:
            return ValueError("Must have at least 1 histogram")
        for h in histograms[1:]:
            hi = hi + h
        hi.hist.SetName("summed")
        hi.hist.SetTitle("summed")
        hi.update()
        return hi

    @staticmethod
    def unique_name(var, cut, weight):
        cut_str = cut if cut is not None else "NOCUT"
        weight_str = weight if weight is not None else "NOWEIGHT"
        return filter_alnum(var + "_" + cut_str + "_" + weight_str)


class HistMetaData:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

class HistCollection:
    """
    A class that manages saving and loading a collection of histograms to and from the disk.
    """
    def __init__(self, hists, metadata={}, name="coll", fi=None):
        self.name = name
        self.hists = hists
        self.metadata = metadata
        for k, v in self.hists.items():
            if k not in self.metadata.keys():
                self.metadata[k] = HistMetaData()
        self.fi = fi
        logger.debug("Created HistCollection with name %s, hists %s" % (name, str(hists)))

    def __del__(self):
        if self.fi:
            logger.debug("Closing file %s of HistCollection" % self.fi.GetPath())
            self.fi.Close()

    def get(self, hname):
        return self.hists[hname], self.metadata[hname]

    def save(self, out_dir):
        """
        Saves this HistCollection to files out_dir/hists__{name}.root and out_dir/hists__{name}.pickle.
        The root file contains the histograms, while the .pickle file contains the histogram metadata.
        The out_dir is created if it doesn't exist.
        The TFile will have a directory structure corresponding to the '/'-separated keys of the input dictionary,
        so hists["A/B/C"] = TH1F("myhist", ...) => TFile.Get("A/B/C/myhist"))

        out_dir - a string indicating the output directory
        """
        mkdir_p(out_dir) #recursively create the directory
        histo_file = out_dir + "/%s.root" % escape(self.name)
        fi = File(histo_file, "RECREATE")
        if not fi:
            raise Exception("Couldn't open file for writing")
        logger.info("Saving histograms to ROOT file %s" % histo_file)
        for hn, h in self.hists.items():
            dirn = "/".join(hn.split("/")[:-1])
            fi.cd()
            try:
                d = fi.Get(dirn)
            except rootpy.io.DoesNotExist:
                d = rootpy.io.utils.mkdir(dirn, recurse=True)
            d.cd()
            h.SetName(hn.split("/")[-1])
            h.SetDirectory(d)
            #md.hist_path = h.GetPath()

        mdpath = histo_file.replace(".root", ".pickle")
        logger.info("Saving metadata to pickle file %s" % mdpath)
        pickle.dump(self.metadata, open(mdpath, "w"))
        fi.Write()
        fi.Close()
        return

    @staticmethod
    def load(fname):
        fi = File(fname)
        name = re.match(".*/(.*)\.root", fname).group(1)
        logger.info("Opened file %s" % fi.GetPath())
        metadata = pickle.load(open(fname.replace(".root", ".pickle")))
        hists = {}
        for path, dirs, hnames in fi.walk():
            if len(hnames)>0:
                for hn in hnames:
                    if path:
                        hname = path + "/" + hn
                    else:
                        hname = hn
                    logger.debug("Getting %s" % hname)
                    hists[hname] = fi.Get(hname)
                    
                    md = metadata[hname]
        return HistCollection(hists, metadata, name, fi)

def norm(hist):
    if hist.Integral()>0:
        hist.Scale(1.0/hist.Integral())
    else:
        logger.error("Histogram integral was 0: %s" % hist.GetName())

def calc_int_err(hist):
    err = ROOT.Double()
    integral = hist.IntegralAndError(1, hist.GetNbinsX(), err)
    return (integral, err)
