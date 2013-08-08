#!/usr/bin/env python
"""
This module supports making histograms from files containing TTrees
in a systematic fashion.
"""
import argparse
import logging
import sys, os, copy, itertools, imp
import ROOT

logging.basicConfig(level=logging.WARNING)
from plots.common.sample import Sample
from plots.common.cuts import Cuts, Cut, Weights, Var
from plots.common.odict import OrderedDict
import rootpy
from rootpy.plotting import Hist
from rootpy.io import File
from plots import histo_defs
from SingleTopPolarization.Analysis import tree

logger = logging.getLogger("make_histo")
logger.setLevel(logging.INFO)

class Plottable:
    def __init__(self, *args):
        self.args = args

def totalFromList(input, leaf_type=None):
    """
    Given a list of pairs (name, obj), returns the tally
    (name1__name2__... , obj1 * obj2 * ...). The type of
    obj must support multiplication.

    Args:
        input: a list of pairs.

    Keywords:
        leaf_type: an optional leaf type which is enforced on obj.

    Returns:
        a tuple (total_name, total_obj)    
    """
    total_name = "__".join([c[0] for c in input])
    total = None
    for cn, c in input:
        if leaf_type:
            assert(isinstance(c, leaf_type))
        if not total:
            total = c
        else:
            total = total * c
    return total_name, total

def totalUniVariation(weights):
    """
    Given a list of tuples with weights such as
    [
        (w1_nominal, w1_up, w1_down),
        (w2_nominal, w2_up, w2s_down),
        ...
        (wN_nominal, wN_up, wN_down)
    ]
    this method returns the list of combinations where
    exactly one weight is variated, such as
    [
        [w1_nominal, w2_up, w3_nominal, ...],
        [w1_nominal, w2_nominal, w3_up, ...]
    ].
    Operates under the assumption that the first element
    of the tuple is the nominal weight.

    Args:
        weights: a list of tuples with the different weight combinations

    Returns:
        a list with the variated weights.

    """
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
    """
    Returns the combinatoric multiple of the root-to-leaf paths of
    a list of trees.
    [
        (tree1, [
            (c1, obj1),
            (c2, obj2)
        ]),
    (tree1, [
            (c1, obj1),
            (c2, obj2)
        ])
    
    ]
    """
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
    strip = "/hdfs/local/stpol/step3/"
    if samp_base.startswith(strip):
        samp_base.replace(strip, "")
    if samp_base.startswith("/"):
        samp_base = samp_base[1:]
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

    n = 0
    for cuts, variables in histo_defs:
        assert len(variables)==1
        cut_name, cut = totalFromList(cuts)
        var_name, variable = variables[0]
        logger.info(", ".join([cut_name, var_name]) + ": %d done" % n)
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

            #In older ROOT we have to make the directory tree manually
            d = ofi
            for _dir in path.split("/"):
                _d = d.Get(_dir)
                if not _d:
                    _d = d.mkdir(_dir)

                d = _d
                d.cd()
            d = ofi.Get(path)
            hist.SetDirectory(d)
            d.cd()

            hist.Write("", ROOT.TObject.kOverwrite)
            n += 1
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
