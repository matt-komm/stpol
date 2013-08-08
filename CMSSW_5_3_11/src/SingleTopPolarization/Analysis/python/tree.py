import itertools
from collections import deque
import copy

import logging
logging.basicConfig(level=logging.DEBUG)
from plots.common.sample import Sample
from plots.common.cuts import Cuts, Weights, mul
import rootpy
from rootpy.io import File

import ROOT
logger = logging.getLogger("tree")
logger.setLevel(logging.DEBUG)

gNodes = dict()
class Node(object):
    def __init__(self, name, parents, children, filter_funcs=[]):
        self.name = name
        self.parents = parents
        for p in parents:
            p.children.append(self)
        self.children = children
        self.filter_funcs = filter_funcs

        #FIXME: global state
        assert not name in gNodes.keys()
        gNodes[name] = self

    def __repr__(self):
        return "<%s>" % self.name

    def isLeaf(self):
        return len(self.children)==0

    def addParents(self, parents):
        self.parents += parents
        for p in parents:
            p.children.append(self)

    def delParents(self, parents):
        self.parents = filter(lambda x: x not in parents, self.parents)
        for p in parents:
            p.children = filter(lambda x: x!= self, p.children)

    def process(self, obj, parentage):
        parentage = parentage[:-1]
        # if self.isLeaf():
        #     print self.parentsName(parentage), "*" if self.isLeaf() else ""
        return self.name

    def parentsName(self, parentage, upto=0):
        if upto:
            pars = parentage[:upto]
        else:
            pars = parentage
        return "/".join(pars + [self.name])

    def getParents(self, parentage, cls=None):
        pars = [gNodes[p] for p in parentage]
        if cls:
            pars = filter(lambda x: isinstance(x, cls), pars)
        return pars

    def getPrevious(self, parentage, cls):
        last_cut = None
        for p in parentage[::-1]:
            par = gNodes[p]
            if isinstance(par, cls):
                last_cut = par
                break
        return last_cut

    def recurseDown(self, obj, parentage=[]):
        for f in self.filter_funcs:
            if not f(parentage):
                return
        parentage = copy.deepcopy(parentage)
        parentage.append(self.name)
        return [(parentage, self.process(obj, parentage)), [c.recurseDown(obj, parentage) for c in self.children]]

class HistNode(Node):
    
    def __init__(self, hist_desc, *args, **kwargs):
        super(HistNode, self).__init__(*args, **kwargs)
        self.hist_desc = hist_desc

    def process(self, obj, parentage):
        r = Node.process(self, obj, parentage)

        last_cut = self.getPrevious(parentage, CutNode)
        cache = last_cut.cache
        cut = last_cut.getCutsTotal(parentage)
        weights = self.getParents(parentage, WeightNode)

        wtot = mul([w.weight for w in weights])

        hi = obj.sample.drawHistogram(self.hist_desc["var"], str(cut), weight=wtot.weight_str, binning=self.hist_desc["binning"], entrylist=cache)
        hdir = self.parentsName(parentage[:-1])
        logger.debug("%d %s %s" % (hi.GetEntries(), self.name, self.parentsName(parentage[-6:-1])))
        hi.SetName(self.name)
        obj.saver.save(hdir, hi)
        return ("hn", r)

class ObjectSaver:
    def __init__(self, fname):
        self.tfile = File(fname, "RECREATE")

    def save(self, path, obj):
        #In older ROOT we have to make the directory tree manually
        d = self.tfile
        #logger.debug(path)
        for _dir in path.split("/"):
            try:
                _d = d.Get(_dir)
            except rootpy.io.file.DoesNotExist:
                _d = None
            #logger.debug("%s %s" % (_dir, _d))
            if not _d:
                _d = d.mkdir(_dir)

            d = _d
            d.cd()
        d = self.tfile.Get(path)
        obj.SetDirectory(d)
        d.cd()
        obj.Write("", ROOT.TObject.kOverwrite)
        logger.debug("Saving object %s in %s" % (str(obj.name), d.GetPath()))

class CutNode(Node):
    def __init__(self, cut, *args, **kwargs):
        super(CutNode, self).__init__(*args, **kwargs)
        self.cut = cut
        self.cache = 0

    def getCutsList(self, parentage):
        cutlist = [gNodes[p].cut for p in parentage if isinstance(gNodes[p], CutNode)]
        return cutlist

    def getPreviousCache(self, parentage):
        last_cut = self.getPrevious(parentage[:-1], CutNode)
        logger.debug("Last cut is %s" % last_cut)
        if not last_cut:
            cache = 0
        else:
            cache = last_cut.cache
        logger.debug("Last cut is %s, cache %s" % (last_cut, str(cache)))
        return cache

    def getCutsTotal(self, parentage):
        cutlist = self.getCutsList(parentage)
        total_cut = cutlist[0]
        for cut in cutlist[1:]:
            total_cut = total_cut * cut
        return total_cut

    def process(self, obj, parentage):
        logger.debug("Processing CutNode %s" % self.name)
        r = super(CutNode, self).process(obj, parentage)
        total_cut = self.getCutsTotal(parentage)
        elist_name = "elist__" + self.parentsName(parentage[:-1]).replace("/", "__")
        prev_cache = self.getPreviousCache(parentage)
        self.cache = obj.sample.cacheEntries(elist_name, str(total_cut), cache=prev_cache) 
        logger.debug("%d => %d, %s" % (prev_cache.GetN() if prev_cache else obj.sample.getEventCount(), self.cache.GetN(), elist_name))

class SampleNode(Node):
    def __init__(self, saver, *args, **kwargs):
        super(SampleNode, self).__init__(*args, **kwargs)
        self.sample = Sample.fromFile(self.name)
        self.saver = saver

class WeightNode(Node):
    def __init__(self, weight, *args, **kwargs):
        super(WeightNode, self).__init__(*args, **kwargs)
        self.weight = weight

def hasParent(node, p):
    return node.name in p

def reweigh(node, weights):
    pars = copy.copy(node.parents)
    node.delParents(node.parents)
    for w in weights:
        w.addParents(pars)
        node.addParents([w])
        #w.children += [node]
    return node

eleChan = lambda p: hasParent(channels['ele'], p)
muChan = lambda p: hasParent(channels['mu'], p)

eleSamp = lambda p: "/ele/" in sample.name
muSamp = lambda p: "/mu/" in sample.name

if __name__=="__main__":

    hsaver = ObjectSaver("hists.root")
    sample = SampleNode(hsaver, "step3_latest/mu/mc/iso/nominal/Jul15/T_t_ToLeptons.root", [], [])

    channel = Node("channel", [sample], [])
    channels = dict()
    channels['mu'] = CutNode(
        Cuts.hlt("mu")*Cuts.lepton("mu"),
        "mu", [channel], [], filter_funcs=[muSamp]
    )
    channels['ele'] = CutNode(
        Cuts.hlt("ele")*Cuts.lepton("ele"),
        "ele", [channel], [], filter_funcs=[eleSamp]
    )
    weights_lepton = dict()
    weights_lepton['mu'] = Node("weights_muon", [channels['mu']], [])
    for w in [("id", muon_id), ("iso", muon_iso), ("trigger", muon_trigger)]:
        

    isos = dict()
    isol = []
    for lep in ['mu', 'ele']:
        par = [channels[lep]]
        isos[lep] = dict()
        isos[lep]['iso'] = Node(lep + "_iso", par, [])
        isos[lep]['antiiso'] = CutNode(Cuts.antiiso(lep), lep + "_antiiso", par, [])
        isol.append(isos[lep]['iso'])
        isol.append(isos[lep]['antiiso'])

    jet = Node("jet", isol, [])
    jets = dict()
    for i in [2,3]:
        jets[i] = CutNode(Cuts.n_jets(i), "%dj"%i, [jet], [])

    tag = Node("tag", jet.children, [])
    tags = dict()
    for i in [0,1,2]:
        tags[i] = CutNode(Cuts.n_tags(i), "%dt"%i, [tag], [])


    met = Node("met", tag.children, [])
    mets = dict()

    mets['met'] = CutNode(Cuts.met(), "met_met", [met], [],
        filter_funcs=[eleChan]
    )
    mets['mtw'] = CutNode(Cuts.mt_mu(), "met_mtw", [met], [],
        filter_funcs=[muChan]
    )

    purification = Node("signalenr", met.children, [])
    purifications = dict()
    purifications['cutbased'] = Node("cutbased", [purification], [])
    #purifications['mva'] = Node("mva", [purification], [])

    etalj = Node("etalj", [purifications['cutbased']], [])
    etaljs = dict()
    etaljs['greater__2_5'] = CutNode(Cuts.eta_lj,"etalj__g2_5", [etalj], [])

    mtop = Node("mtop", [etaljs['greater__2_5']], [])
    mtops = dict()
    mtops['SR'] = CutNode(Cuts.top_mass_sig, "mtop_SR", [mtop], [])

    # mvas = dict()
    # for mva_cut in [0, 0.1, 0.2, 0.3]:
    #     cl = str(mva_cut).replace(".", "_")
    #     mvas[cl] = Node(cl, [purifications['mva']], [])

    plot_nodes = mtop.children+etalj.children+met.children+tag.children+jet.children

    weights = [
        Weights.wjets_btag_syst,
        Weights.wjets_yield_syst,
        Weights.wjets_shape_syst,
    ]

    sts = []
    for i in range(len(weights)):
        st = [x[0] for x in weights[:i]]
        for w in weights[i][1:]:
            subs = []
            subs += st
            subs.append(w)
            for w2 in weights[i+1:]:
                subs.append(w2[0])
            sts.append(subs)

    weights_total = []
    for s in sts:
        j = mul(s)
        weights_total.append(j)

    syst_weights = []
    for j in weights_total:

        syst = WeightNode(j, "weight_" + j.name, [], [])
        syst_weights.append(syst)

    final_plot_descs = [
        ("cos_theta", "cos_theta", [20, -1, 1]),
        ("abs_eta_lj", "abs(eta_lj)", [20, 2.5, 5])
    ]
    final_plots = dict()
    for name, func, binning in final_plot_descs:
        hdesc = {
            "name": name,
            "var": func,
            "binning": binning
        }
        final_plots[name] = HistNode(hdesc, name, plot_nodes, [])
        final_plots[name] = reweigh(final_plots[name], syst_weights)

    r = sample.recurseDown(sample)