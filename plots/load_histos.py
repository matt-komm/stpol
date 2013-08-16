import ROOT
import rootpy
import re, glob, argparse
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
    outdict = dict()
    for fn in filenames:
        fi = File(fn)
        for root, dirs, items in fi:
            for it in items:
                k = "/".join([root, it])
                item = fi.Get(k)
                #k = "/".join([fn, k.replace("__", "/")])
                print k, item
                if not isinstance(item, ROOT.TH1F):
                    pdb.set_trace()
                outdict[k] = item
    return outdict

if __name__=="__main__":

    parser = argparse.ArgumentParser(
        description='FIXME'
    )

    parser.add_argument('infile', action='store',
        help="The input file name with histograms."
    )
    args = parser.parse_args()

    outd = load_histos(args.infile)
    for k, v in list(sorted(outd.items(), key=lambda x: x[0])):
        print k, v, v.Integral()
        if v.Integral() < 0.00001:
            print k, "was emtpy"
