import ROOT
import rootpy
import re,glob
from rootpy.io import File
from rootpy.plotting import Hist
from plots.common.utils import NestedDict
from plots.common.odict import OrderedDict
from plots.common.stack_plot import plot_hists_stacked
from plots.common.utils import PhysicsProcess, merge_hists, PatternDict
from plots.common.sample_style import Styling
import SingleTopPolarization.Analysis.sample_types as sample_types
import pdb

def load_histos(filenames):
    if isinstance(filenames, basestring):
        filenames = [filenames]
    outdict = PatternDict()
    for fn in filenames:
        fi = File(fn)
        for root, dirs, items in fi:
            for it in items:
                k = "/".join([root, it])
                item = fi.Get(k)
                k = "/".join([fn, k.replace("__", "/").replace(".", "__")])
                outdict[k] = item
    return outdict

if __name__=="__main__":

    outd = load_histos("hists.root")
    for k, v in outd.items():
        print k, v, v.Integral()