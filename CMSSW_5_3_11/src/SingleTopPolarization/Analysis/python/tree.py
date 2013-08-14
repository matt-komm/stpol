#!/usr/bin/env python
"""
Applies operations on a TFile systematically by defining the operations as a
directed graph and evaluating all root-to-leaf paths.
"""
print "Loading dependency libraries..."
import itertools, copy, argparse, logging, time, sys
logging.basicConfig(level=logging.WARNING)

from plots.common.sample import Sample
from plots.common.cuts import Cuts, Weights, mul, Cut
from plots.common.utils import NestedDict

import rootpy
from rootpy.io import File

import networkx as nx

import ROOT
logger = logging.getLogger("tree")
#logger.setLevel(logging.DEBUG)
print "Done loading dependency libraries..."


"""
A per-module dict with the name and instance of every Node that was instantiated.
TODO: this is a rather bad solution, make a separate Graph class which contains the
nodes instead.
"""
gNodes = dict()
gNhistograms = 0
gGraph = nx.Graph()


def variateOneWeight(weights):
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
    sts = []
    for i in range(len(weights)):
        st = [x[0] for x in weights[:i]]
        for w in weights[i][1:]:
            subs = []
            subs += st
            subs.append(w)
            for w2 in weights[i+1:]:
                subs.append(w2[0])
            sts.append((w.name, subs))
    return sts

def hist_node(hist_desc, _cut, _weight):
    """
    Creates a simple CutNode -> WeightNode -> HistNode structure from the specified
    histogram description, cut and weight.

    Args:
        hist_desc: A dict with the histogram description, keys/values as in tree.HistNode.
        _cut: A (name, cut) tuple with the cut to apply. 
        _weight: A (name, weight) with the weight to apply.

    Returns:
        The top CutNode that was created.
    """
    cut_name, cut = _cut
    weight_name, weight = _weight
    cutnode = tree.CutNode(cut, cut_name, [], [])
    weightnode = tree.WeightNode(weight, weight_name, [cutnode], [])
    histnode = tree.HistNode(hist_desc, hist_desc["name"], [weightnode], [])
    return cutnode

def sample_nodes(sample_fnames, out, top):
    snodes = []
    for samp in sample_fnames:
        snodes.append(
            tree.SampleNode(
                out,
                samp,
                [top], []
            )
        )
    return snodes

class Node(object):
    """
    Represents a node in a directed graph by containing references to it's
    parents and children.
    A Node object is stateless, the state of processing is contained
    within the Node.process method.
    """
    def __init__(self, name, parents, children, filter_funcs=[]):
        """
        Construct a node with a given name and optionally parents and children.

        Args:
            name: a string specifying the unique name of this node
            parents: a list of Node objects that are the parents of this Node.
                This node is added to the list of children of the parents automatically.
            children: a list of nodes with the children for this Node.

        Keywords:
            filter_funcs: a list of lambda functions taking the list of parent names
                in the current processing chain and returning a boolean which decides if
                this node and it's children will be processed.
        """
        self.name = name
        gGraph.add_node(name)
        self.parents = parents
        for p in parents:
            p.children.append(self)
            gGraph.add_edge(self.name, p.name)
        self.children = children
        self.filter_funcs = filter_funcs

        #FIXME: global state
        gNodes[name] = self

    def __del__(self):
        pass

    def __repr__(self):
        return "<%s>" % self.name

    def isLeaf(self):
        """
        A leaf is a Node with no children.
        """
        return len(self.children)==0

    def addParents(self, parents):
        """
        Adds this node to the list of children of the parents

        Args:
            parents: a list of Node objects to be added as parents.
        """
        self.parents += parents
        for p in parents:
            p.children.append(self)

    def delParents(self, parents):
        """
        Removes the specified parents from this Node, also removing a reference
        from the parent->child relationship of the parent.

        Args:
            parents: a list of parent Nodes to remove
        """
        self.parents = filter(lambda x: x not in parents, self.parents)
        for p in parents:
            p.children = filter(lambda x: x!= self, p.children)

    def process(self, obj, parentage):
        """
        A default implementation of the Node.process method, which
        is called when this Node is traversed using the recurseDown method.
        """
        parentage = parentage[:-1]
        if self.isLeaf():
            logger.debug(self.parentsName(parentage))
        return self.name

    def parentsName(self, parentage, upto=0):
        """
        Returns a structured representation of the parents
        of this node in the present iteration.

        Args:
            parentage: a list with the names of the parents in this iteration.

        Keywords:
            upto: Return up to N parents from the head

        Returns:
            A string representing the parentage
        """
        if upto:
            pars = parentage[:upto]
        else:
            pars = parentage
        return "/".join(pars + [self.name])

    def getParents(self, parentage, cls=None):
        """
        Gets the list of Node instances that are the parents
        of this node in this iteration.

        Args:
            parentage: a list of string with the names of the parents
                in the call order.

        Keywords:
            cls: an optional class/type by which the parent list will be filtered.

        Returns:
            A list of the parent Node instances.
        """
        pars = [gNodes[p] for p in parentage]
        if cls:
            pars = filter(lambda x: isinstance(x, cls), pars)
        return pars

    def getPrevious(self, parentage, cls):
        """
        Gets the previous node in the current call order.

        Args:
            parentage: a list of strings with the parentage in the call order.

        Keywords:
            cls: an optional class, the instance returned will be the first
                instance in the parent chain of this class.

        Returns:
            an instance of the previous Node with the specified class.
        """
        last = None
        for p in parentage[::-1]:
            par = gNodes[p]
            if isinstance(par, cls):
                last = par
                break
        return last

    def recurseDown(self, obj, parentage=[], dryRun=False):
        """
        Recursively processes the children of this node, calling the
        Node.process method on each child. This node and it's children
        are only processed if all of the filter_funcs return True upon
        the parentage.

        Args:
            obj: an instance of an object that is passed down the recurse tree.
            parentage: the list of names of the preceding nodes.

        Keywords:
            dryRun: a boolean to specify whether Node.process will actually be called.

        Returns:
            a nested list with the output of the Node.process of each node in the graph
        """
        for f in self.filter_funcs:
            if not f(parentage):
                return
        parentage = copy.deepcopy(parentage)
        parentage.append(self.name)
        return [self.process(obj, parentage) if not dryRun else self.name, [c.recurseDown(obj, parentage) for c in self.children]]

class HistNode(Node):
    """
    A Node that takes the passed object, assumes it's a SampleNode and draws a histogram
    corresponding to the present event selection. Any preceding WeightNodes are multiplied
    and the corresponding per-event weight is applied on the histogram.
    """
    def __init__(self, hist_desc, *args, **kwargs):
        """
        Creates a HistNode with the histogram description dictionary.

        Args:
            hist_desc: a dictionary which must contain 'var' and 'binning' as keys.
        """
        super(HistNode, self).__init__(*args, **kwargs)
        self.hist_desc = hist_desc

    def process(self, obj, parentage):
        global gNhistograms
        """
        Draws the histogram corresponding to the present cut and optionally the weighting
        strategy.

        Args:
            obj: assumed to be a SampleNode whose underlying Sample will
                be ued for projection.
            parentage: the names of the call stack
        Returns:
            a tuple (Hist, Node.process()) with the projected histogram Hist and the parent Node class
            process output.
        """
        r = Node.process(self, obj, parentage)

        #Use the cache of the previous CutNode in the call stack.
        last_cut = self.getPrevious(parentage, CutNode)
        cache = 0#last_cut.cache
        #FIXME: The cache carries state information, which cannot be stored with the node

        if cache and "W1Jets" in cache.GetName() and "W3Jets" in obj.sample.name:
            import pdb
            pdb.set_trace()

        #Get the total cut string from the call stack.
        cut = last_cut.getCutsTotal(parentage)

        #Get the total weight
        weights = self.getParents(parentage, WeightNode)
        wtot = mul([w.weight for w in weights])

        if not "var" in self.hist_desc.keys() or not "binning" in self.hist_desc.keys():
            raise KeyError("Incorrect hist desc: %s" % str(self.hist_desc))

        if not hasattr(obj, "sample") or not hasattr(obj.sample, "drawHistogram"):
            raise TypeError("call object 'obj' must have a sample with a drawHistogram method.")

        hi = obj.sample.drawHistogram(self.hist_desc["var"], str(cut), weight=wtot.weight_str, binning=self.hist_desc["binning"], entrylist=cache)
        if obj.sample.isMC:
            hi.Scale(obj.sample.lumiScaleFactor(1))
        hdir = self.parentsName(parentage[:-1])

        logger.debug("%d %s %s" % (hi.GetEntries(), self.name, self.parentsName(parentage)))

        #Save the histogram using the Saver that was passed down.
        hi.SetName(self.name)
        obj.saver.save(hdir, hi)

        gNhistograms += 1
        return (hi, r)

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
        logger.info("Processing cut %s%s" % (len(parentage)*".", self.name))
        r = super(CutNode, self).process(obj, parentage)
        total_cut = self.getCutsTotal(parentage)
        elist_name = "elist__" + self.parentsName(parentage[:-1]).replace("/", "__")
        prev_cache = self.getPreviousCache(parentage)
        self.cache = obj.sample.cacheEntries(elist_name, str(total_cut), cache=prev_cache)
        logger.debug("%d => %d, %s" % (prev_cache.GetN() if prev_cache else obj.sample.getEventCount(), self.cache.GetN(), elist_name))
        return (self.cache.GetN(), r)

class SampleNode(Node):
    def __init__(self, saver, *args, **kwargs):
        super(SampleNode, self).__init__(*args, **kwargs)
        self.sample = Sample.fromFile(self.name)
        self.saver = saver

    def process(self, *args):
        logger.info("Processing sample %s" % self.sample)
        return super(SampleNode, self).process(*args)

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

def is_chan(p, lep):
    """
    There must be a parent which is the corresponding lepton cut node.
    """
    return hasParent(gNodes[lep], p)

def is_samp(p, lep):
    """
    The first parent must be a sample and contain the lepton.
    """
    return ("/%s/" % lep) in p[0]

if __name__=="__main__":
    print "Constructing analysis tree..."

    parser = argparse.ArgumentParser(
        description='Produces a hierarchy of histograms corresponding to cuts and weights.'
    )

    parser.add_argument('infile', action='store',
        help="The input file name with step3 TTrees."
    )

    parser.add_argument('outfile', action='store',
        help="The output file name with histograms."
    )
    args = parser.parse_args()


    #Create the sink to a file
    hsaver = ObjectSaver(args.outfile)

    #Load the sample, which is the root of the tree
    sample = SampleNode(hsaver, args.infile, [], [])

    #Different lepton channels
    channel = Node("channel", [sample], [])
    channels = dict()

    # sample --> channels['mu'], channels['ele']
    channels['mu'] = CutNode(
        Cuts.hlt("mu")*Cuts.lepton("mu"),
        "mu", [channel], [], filter_funcs=[lambda x: is_samp(x, 'mu')]
    )
    channels['ele'] = CutNode(
        Cuts.hlt("ele")*Cuts.lepton("ele"),
        "ele", [channel], [], filter_funcs=[lambda x: is_samp(x, 'ele')]
    )

    # muons: channels['mu'] --> [iso, antiiso]
    # electrons: channels['ele'] --> [iso, antiiso]
    isos = dict()
    isol = []
    for lep, par in [
        ('mu', [channels['mu']]),
        ('ele', [channels['ele']])
        ]:

        isos[lep] = dict()
        isos[lep]['iso'] = CutNode(
            Cut("1.0"), #At present no special cuts have to be applied on the ISO region
            lep + "__iso", par, [],
            filter_funcs=[lambda x: "/iso/" in x[0]]
        )
        isos[lep]['antiiso'] = CutNode(
            Cuts.antiiso(lep), #Apply any additional anti-iso cuts (like dR)
            lep + "__antiiso", par, [],
            filter_funcs=[lambda x: "/antiiso/" in x[0]]
        )
        isol.append(isos[lep]['iso'])
        isol.append(isos[lep]['antiiso'])

    # [iso, antiiso] --> jet --> [jets2-3]
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

    mets['met'] = CutNode(Cuts.met(), "met__met", [met], [],
        filter_funcs=[lambda x: is_chan(x, 'ele')]
    )
    mets['mtw'] = CutNode(Cuts.mt_mu(), "met__mtw", [met], [],
        filter_funcs=[lambda x: is_chan(x, 'mu')]
    )

    # purifications ---> cutbased, MVA
    purification = Node("signalenr", met.children, [])
    purifications = dict()
    purifications['cutbased'] = Node("cutbased", [purification], [])
    purifications['mva'] = Node("mva", [purification], [])

    # cutbased ---> Mtop ---> SR
    mtop = Node("mtop", [purifications['cutbased']], [])
    mtops = dict()
    mtops['SR'] = CutNode(Cuts.top_mass_sig, "mtop__SR", [mtop], [])

    # Mtop children ---> etalj ---> |etalj|>2.5
    etalj = Node("etalj", mtop.children, [])
    etaljs = dict()
    etaljs['greater__2_5'] = CutNode(Cuts.eta_lj,"etalj__g2_5", [etalj], [])

    # MVA ---> MVA ele, MVA mu
    mvas = NestedDict()

    for lepton in ['mu', 'ele']:
        for name, mva_cut in Cuts.mva_wps['bdt'][lepton].items():
            cval = str(mva_cut).replace(".", "_")
            mva_name = 'mva__%s__%s__%s' % (lepton, name, cval)
            mvas[lepton][cval] = CutNode(
                Cut("%s >= %f" % (Cuts.mva_vars[lepton], mva_cut)),
                mva_name, [purifications['mva']], [],
                filter_funcs=[lambda x,lepton=lepton: is_chan(x, lepton)]
            )

    #After which cuts do you want the reweighed plots?
    plot_nodes = etalj.children + purifications['mva'].children

    #Separate lepton weights for mu/ele
    weights_lepton = dict()
    weights_lepton['mu'] = Weights.muon_sel.items()
    weights_lepton['ele'] = Weights.electron_sel.items()

    #Other weights are the same
    weights = [
        ("btag", Weights.wjets_btag_syst),
        ("wjets_yield", Weights.wjets_yield_syst),
        ("wjets_shape", Weights.wjets_shape_syst),
    ]

    #Now make all the weight combinations for mu/ele, variating one weight
    weights_total = dict()
    syst_weights = []
    for lepton, w in weights_lepton.items():
        weights_var_by_one = variateOneWeight([x[1] for x in (weights+w)])
        #The unvariated weight is taken as the list of the 0th elements of the weight tuples
        weights_var_by_one.append(
            ("nominal", [x[1][0] for x in (weights+w)])
        )

        wtot = []
        for wn, s in weights_var_by_one:
            j = mul(s) #Multiply together the list of weights
            wtot.append((wn, j))

        for name, j in wtot:
            syst = WeightNode(
                j, "weight__" + name + "__" + lepton,
                [], [],
                filter_funcs=[
                    lambda x,lepton=lepton: is_chan(x, lepton), #Apply the weights separately for the lepton channels
                    lambda x: "/mc/" in x[0] #Apply only in MC
                ] + ([lambda x: "/nominal/" in x[0]] if name != "nominal" else []) #And variate only if we're using the nominal samples.
            )
            syst_weights.append(syst)

    #Which distributions do you want to plot
    final_plot_descs = dict()
    final_plot_descs['all'] = [
        ("cos_theta", "cos_theta", [60, -1, 1]),
        ("true_cos_theta", "true_cos_theta", [60, -1, 1]),
        ("abs_eta_lj", "abs(eta_lj)", [60, 2.5, 5]),
        #("eta_lj", "eta_lj", [40, -5, 5]),
    ]

    #Lepton channels need to be separated out
    final_plot_descs['mu'] = [
        (Cuts.mva_vars['mu'], Cuts.mva_vars['mu'], [60, -1, 1]),
    ]
    final_plot_descs['ele'] = [
        (Cuts.mva_vars['ele'], Cuts.mva_vars['ele'], [60, -1, 1]),
    ]

    #define a LUT for type <-> filtering function
    final_plot_lambdas = {
        'mu': lambda x: is_chan(x, 'mu'),
        'ele': lambda x: is_chan(x, 'ele')
    }

    #Add all the nodes for the final plots with all the possible reweighting combinations
    final_plots = dict()
    def hdesc(name, func, binning):
        hdesc = {
            "name": name,
            "var": func,
            "binning": binning
        }
        return hdesc

    for t, descs in final_plot_descs.items():
        for name, func, binning in descs:
            hd = hdesc(name, func, binning)

            #Make only the required plots par channel
            lambdas = []
            if t in final_plot_lambdas.keys():
                lambdas.append(final_plot_lambdas[t])

            final_plots[name] = HistNode(hd, name, plot_nodes, [], filter_funcs=lambdas)
            final_plots[name] = reweigh(final_plots[name], syst_weights)

    print "Done constructing analysis tree..."

    print gGraph.nodes()
    import matplotlib.pyplot as plt
    nx.draw(gGraph)
    plt.show()
    print "Starting projection..."    
    #Make everything
    t0 = time.clock()
    #r = sample.recurseDown(sample)
    t1 = time.clock()
    dt = t1-t0
    print "Projected out %d histograms in %.f seconds, %.2f/sec" % (gNhistograms, dt, float(gNhistograms)/dt)
