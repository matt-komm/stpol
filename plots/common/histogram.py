import ROOT
from plots.common.utils import filter_alnum
from cross_sections import xs as sample_xs_map
import logging

try:
    from sqlalchemy.ext.declarative import declarative_base
    Base = declarative_base()
    from sqlalchemy import Column, Integer, String
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
except Exception as e:
    logging.error("plots/common/histogram.py: SQLAlchemy needed, please install by running util/install_sqlalchemy.sh")
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
            logging.warning("Histogram %s integral=0, not scaling." % str(self))

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
