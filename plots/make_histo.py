import argparse
import logging
import sys, os, copy, itertools, imp
import ROOT

from plots.common.sample import Sample
from plots.common.cuts import Cuts, Cut, Weights, Var
from plots.common.odict import OrderedDict
from rootpy.plotting import Hist
from plots import histo_defs

#FIXME: put to subpath
import tree

logger = logging.getLogger("make_histo")
logging.basicConfig(level=logging.INFO)
cp = copy.deepcopy

class Plottable:
    def __init__(self, *args):
        self.args = args

def totalFromList(l, leaf_type=None):
    total_name = "__".join([c[0] for c in l])
    total = None
    for cn, c in l:
        if leaf_type:
            assert(isinstance(c, leaf_type))
        if not total:
            total = c
        else:
            total = total * c
    return total_name, total

def totalUniVariation(weights):
    pl = [tree.getPathLeaves(c) for c in weights]

    weight_stacks = []
    for i in range(len(pl)):
        cur_stack = []
        for weights in pl[:i]:
            cur_stack.append(weights[0])
        for weight_sys in pl[i][1:]:
            cur_substack = []
            cur_substack += cur_stack
            cur_substack.append(weight_sys)
            for weights in pl[i+1:]:
                cur_substack.append(weights[0])
            weight_stacks.append(cur_substack)
    nom_stack = []
    for w in pl:
        nom_stack.append(w[0])
    weight_stacks.append(nom_stack)
    return [totalFromList(w) for w in weight_stacks]

def mult_prod(*args):
    prods = []
    for arg in args:
        pathleaves = [tree.getPathLeaves(c) for c in arg]
        p = list(itertools.product(*pathleaves))
        prods.append(p)
    return itertools.product(*prods)

class HistPlottable(Plottable):
    def __init__(self, cut, weight, var):
        self.cut_name, self.cut = cut
        self.weight_name, self.weight = weight
        self.var_name, self.var = var

    def draw(self, sample):
        #Cache the entry list with the cut
        elist_name = "__".join(["elist", self.cut_name])
        elist = sample.tfile.Get(elist_name)
        if elist and isinstance(elist, ROOT.TEntryList):
            logger.debug("Loaded entry list %s" % elist)
        else:
            logger.debug("Starting to cache entry list for cut %s" % self.cut_name)
            elist = sample.cacheEntries(elist_name, str(self.cut))
            logger.debug("Done caching entry list: %d entries" % elist.GetN())
        
        try:
            hist = sample.drawHistogram(
                self.var.varfn, str(self.cut), weight=str(self.weight),
                binning=self.var.binning, entrylist=elist
            )
            hist.SetName(self.var_name.split(".")[-2])
        except:
            hist = None
        return hist

def sampleBaseName(sample):
    for l in ["mu", "ele"]:
        spl = sample.split("/")
        if l in sample:
            lep_idx = spl.index(l)
            return "/".join(spl[:lep_idx]), "/".join(spl[lep_idx:-1]), spl[-1]

def draw(cutlist, weightlist, varlist, samp_fname, ofdir="hists"):
    samp = Sample.fromFile(samp_fname)
    samp_base, samp_dir, samp_name = sampleBaseName(samp_fname)
    ofdir = os.path.join(ofdir, samp_base, samp_dir)
    print ofdir
    
    try:
        os.makedirs(ofdir)
    except:
        pass
    assert(os.path.exists(ofdir))

    ofn = os.path.join(ofdir, samp_name)
    ofi = ROOT.TFile(ofn, "RECREATE")
    assert(os.path.exists(ofn))
    ofi.cd()

    #Create weights where only one weight out of the list is variated
    weights = totalUniVariation(weightlist)

    histo_defs = list(mult_prod(cutlist, varlist))
    print "Projecting out %d histograms" % (len(histo_defs)*len(weights))
    
    for cuts, variables in histo_defs:
        assert len(variables)==1
        cut_name, cut = totalFromList(cuts)
        var_name, variable = variables[0]
        logger.info(", ".join([cut_name, var_name]))
        for weight_name, weight in weights:
            logger.debug(weight_name)
            logger.debug("Plotting %s, %s, %s" % (cuts, weight, variables))
            hcmd = HistPlottable(
                (cut_name, cut),
                (weight_name, weight),
                (var_name, variable)
            )
            hist = hcmd.draw(samp)
            if not hist:
                logger.warning("Couldn't draw histogram.")
                continue
            
            if samp.isMC:
                hist.Scale(samp.lumiScaleFactor(1))
            
            path = os.path.join(cut_name, weight_name, hcmd.var_name)

            try:
                d = ofi.mkdir(path)
            except rootpy.ROOTError as e:
                logger.info(str(e))
            d = ofi.Get(path)
            hist.SetDirectory(d)
            d.cd()

            hist.Write("", ROOT.TObject.kOverwrite)

    ofi.Close()
    print ofi.GetPath()

if __name__=="__main__":

    parser = argparse.ArgumentParser(
        description='Prepares histograms from samples'
    )
    parser.add_argument("-c", dest='conf',
        default="plots/histo_defs.py", type=str,
        help="Configuration file for histograms."
    )
    parser.add_argument("infiles",
        type=str, nargs='+',
        help="Input .ROOT file with step3 TTrees."
    )
    args = parser.parse_args()

    mod = imp.load_source('histo_input', args.conf)
    logger.info("Loaded input configuration file %s" % args.conf)

    for inf in args.infiles:
        logger.info("Processing file %s" % inf)
        draw(mod.cuts, mod.weights, mod.variables, inf)

import unittest
class Test(unittest.TestCase):

    cuts = [
        ("CHANNEL", [
            ("mu", Cuts.lepton("mu")),
        ]),
        ("NJETS", [
            ("2J", Cuts.n_jets(2)),
        ]),
        ("NTAGS", [
            ("0T", Cuts.n_tags(0)),
        ]),
        ("MET", [
            ("mtw", [
                ("40", Cut("mt_mu>40"))
            ])
        ]),
    ]

    weights = [
        ("PU", [
            ("nominal", Weights.pu()),
        ])
    ]

    variables = [
        ("VARS", [
            ("cos_theta", [
                ("fixed1", Var("cos_theta", (20, -1, 1))),
            ])
        ])
    ]

    def testDraw(self):
        sn = "step3_latest/mu/mc/iso/nominal/Jul15/T_t_ToLeptons.root"
        ofn = os.path.join("hists", sn)
        draw(self.cuts, self.weights, self.variables, sn)
        assert(os.path.exists(ofn))
        import rootpy.io
        fi = rootpy.io.File(ofn)
        hi = fi.Get("CHANNEL.mu__NJETS.2J__NTAGS.0T__MET.mtw.40/PU.nominal/VARS.cos_theta.fixed1/cos_theta")
        assert(hi)
        for root, dirs, items in fi.walk():
            for item in items:
                print root, item
