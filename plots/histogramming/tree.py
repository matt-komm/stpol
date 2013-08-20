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
from plots.common.utils import NestedDict, PatternDict

import rootpy
from rootpy.io import File

import networkx as nx

import ROOT
logger = logging.getLogger("tree")
#logger.setLevel(logging.DEBUG)
logger.setLevel(logging.INFO)
print "Done loading dependency libraries..."

def is_samp(p, x):
    """
    Take a boolean decision based on the sample filename/path.
    The sample is assumed to be the first node in the parentage (FIXME)
    """
    return ("/%s/" % x) in p[0].name

def is_chan(p, lep):
    """
    Placeholder for now. FIXME: implement a more clever decision
    """
    return is_samp(p, lep)

def is_mc(p):
    return is_samp(p, "mc") or is_samp(p, "mc_syst")


def hist_node(graph, cut, weights, variables):
    """
    Creates a simple CutNode -> WeightNode(s) ->
    HistNode(s) structure from the specified cut, weights and variables.

    Args:
        graph: a NX graph which is the parent of these nodes
        cut: a (cutname, Cut) tuple with the cut to apply
        weights: a list of (weightname, Weight) tuples to apply
        variables: a list of (varname, variable, binning) tuples to project out.

    Returns:
        The top CutNode that was created.
    """
    cut_name, cut = cut
    #weight_name, weight = _weight
    cutnode = CutNode(cut, graph, cut_name, [], [])

    if not isinstance(weights, list):
        weights = [weights]
    
    from weights import reweight

    for var_name, var, binning in variables:
        hist_desc = {
            "var": var,
            "binning": binning
        }
        histnode = HistNode(hist_desc, graph, var_name, [cutnode], [])
        reweight(histnode, [
            WeightNode(w[1], graph, w[0], [], []) for w in weights]
        )
    return cutnode

def sample_nodes(graph, sample_fnames, out, top):
    snodes = []
    for samp in sample_fnames:
        snodes.append(
            SampleNode(
                out,
                graph,
                samp,
                [top], []
            )
        )
    return snodes

class Node(object):
    """
    Represents a node in a directed graph by containing references to its
    parents and children.
    """

    class State:
        def __init__(self):
            self.cache = 0

    def __init__(self, graph, name, parents, children, filter_funcs=[]):
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
        self.graph = graph
        self.graph.add_node(self)

        self.name = name
        self.addParents(parents)
        self.filter_funcs = filter_funcs

        self.state = Node.State()

    def parents(self):
        return self.graph.predecessors(self)

    def children(self):
        return self.graph.successors(self)
        
    def __del__(self):
        pass

    def __repr__(self):
        return "<%s>" % self.name

    def isLeaf(self):
        """
        A leaf is a Node with no children.
        """
        return len(self.children())==0

    def addParents(self, parents):
        """
        Adds this node to the list of children of the parents

        Args:
            parents: a list of Node objects to be added as parents.
        """
        for p in parents:
            self.graph.add_edge(p, self)

    def delParents(self, parents):
        """
        Removes the specified parents from this Node, also removing a reference
        from the parent->child relationship of the parent.

        Args:
            parents: a list of parent Nodes to remove
        """
        for p in parents:
            self.graph.remove_edge(p, self)
        #self.parents = filter(lambda x: x not in parents, self.parents)
        #for p in parents:
        #    p.children = filter(lambda x: x!= self, p.children)

    def process(self, parentage):
        """
        A default implementation of the Node.process method, which
        is called when this Node is traversed using the recurseDown method.
        """
        # logger.info("Parents: " + ",".join([p.name for p in parentage]))
        # logger.info("Self: " + self.name)
        # logger.info("Children: " + ",".join([p.name for p in self.children()]))

        # logger.info("Calling process for %s" % self.name)
        #parentage = parentage[:-1]
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
        return "/".join([p.name for p in pars] + [self.name])

    def getParents(self, parentage, f=None):
        """
        Gets the list of Node instances that are the parents
        of this node in this iteration.

        Args:
            parentage: a list of string with the names of the parents
                in the call order.

        Returns:
            A list of the parent Node instances.

        """
        pars = [p for p in parentage]
        if f:
            pars = filter(f, pars)
        return pars

    def getPrevious(self, parentage, f):
        """
        Gets the previous node in the current call order.

        Args:
+            parentage: a list of strings with the parentage in the call order.

        Keywords:
            cls: an optional class, the instance returned will be the first
                instance in the parent chain of this class.

        Returns:
            an instance of the previous Node with the specified class.
        """
        last = None
        for p in parentage[::-1]:
            if f(p):
                last = p
                break
        return last

    def getPreviousCache(self, parentage):
        last_cut = self.getPrevious(parentage, lambda x: hasattr(x, "cut"))
        logger.debug("Last cut is %s" % last_cut)
        if not last_cut:
            cache = 0
        else:
            cache = last_cut.state.cache
        logger.debug("Last cut is %s, cache %s" % (last_cut, str(cache)))
        return cache

    def recurseDown(self, parentage=[], dryRun=False):
        """
        Recursively processes the children of this node, calling the
        Node.process method on each child. This node and it's children
        are only processed if all of the filter_funcs return True upon
        the parentage.

        Args:
            parentage: the list of names of the preceding nodes.

        Keywords:
            dryRun: a boolean to specify whether Node.process will actually be called.

        Returns:
            a nested list with the output of the Node.process of each node in the graph
        """
        for f in self.filter_funcs:
            if not f(parentage):
                import inspect
                logger.debug("Cutting node %s because of filter function %s, %s" %
                    (self.name, inspect.getsource(f), ".".join([p.name for p in parentage]))
                )
                return
        self.process(parentage)
        parentage = copy.copy(parentage)
        new = copy.copy(self)
        new.state = copy.deepcopy(self.state)
        parentage.append(new)
        #import pdb; pdb.set_trace()
        logger.debug("%s: %s" % (self.name, map(str, parentage)))
        return [c.recurseDown(parentage) for c in self.children()]

class HistNode(Node):
    """
    A Node that takes the passed object, assumes it's a SampleNode and draws a histogram
    corresponding to the present event selection. Any preceding WeightNodes are multiplied
    and the corresponding per-event weight is applied on the histogram.
    """
    logger = logging.getLogger("HistNode")
    logger.setLevel(logging.INFO)

    def __init__(self, hist_desc, *args, **kwargs):
        """
        Creates a HistNode with the histogram description dictionary.

        Args:
            hist_desc: a dictionary which must contain 'var' and 'binning' as keys.
        """
        super(HistNode, self).__init__(*args, **kwargs)
        self.hist_desc = hist_desc

    def process(self, parentage):
        """
        Draws the histogram corresponding to the present cut and optionally the weighting
        strategy.

        Args:
            parentage: the names of the call stack
        Returns:
            a tuple (Hist, Node.process()) with the projected histogram Hist and the parent Node class
            process output.
        """

        r = Node.process(self, parentage)

        # sys.stdout.write("+")
        # sys.stdout.flush()

        #Use the cache of the previous CutNode in the call stack.
        cache = self.getPreviousCache(parentage)

        #Get the total cut string from the call stack.
        cut = self.getPrevious(parentage, lambda x: hasattr(x, "getCutsTotal")).\
            getCutsTotal(parentage)

        #Get the total weight
        weights = self.getParents(parentage, lambda x: hasattr(x, "weight"))
        wtot = mul([w.weight for w in weights])

        if not "var" in self.hist_desc.keys() or not "binning" in self.hist_desc.keys():
            raise KeyError("Incorrect hist desc: %s" % str(self.hist_desc))

        #Get the sample node
        snodes = self.getParents(parentage, lambda x: hasattr(x, "sample"))
        if not len(snodes)==1:
            raise Exception("More than one parent was a SampleNode, undefined behaviour (probably human error).")
        snode = snodes[0]

        hi = snode.sample.drawHistogram(self.hist_desc["var"], str(cut), weight=wtot.weight_str, binning=self.hist_desc["binning"], entrylist=cache)
        hdir = self.parentsName(parentage)

        #Scale MC histograms to 1 inverse picobarn
        if snode.sample.isMC:
            hi.Scale(snode.sample.lumiScaleFactor(1))

        line_to_show = [
            "->".join([p.name for p in parentage]+[self.name]),
            hi.GetEntries(),
            cache.GetN(),
            "%.2f" % hi.Integral()
        ]
        self.logger.info(
            ", ".join(map(lambda x: str(x), line_to_show))
        )

        hi.SetName(self.name)
        snode.saver.save(hdir, hi)

        return (hi, r)

def get_parent_sample(node, parentage):
    snodes = node.getParents(parentage, lambda x: hasattr(x, "sample"))
    if not len(snodes)==1:
        raise Exception("More than one parent was a SampleNode")
    snode = snodes[0]
    return snode

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

    def __del__(self):
        if self.tfile:
            self.tfile.Write()
            self.tfile.Close()
class CutNode(Node):
    def __init__(self, cut, *args, **kwargs):
        super(CutNode, self).__init__(*args, **kwargs)
        self.cut = cut
        #self.cache = 0

    def getCutsList(self, parentage):
        cutlist = [
            p.cut for p in parentage
            if hasattr(p, "cut")]
        return cutlist + [self.cut]

    def getCutsTotal(self, parentage):
        cutlist = self.getCutsList(parentage)
        return reduce(lambda x,y: x*y, cutlist, Cuts.no_cut)

    def process(self, parentage):
        r = super(CutNode, self).process(parentage)

        total_cut = self.getCutsTotal(parentage)
        elist_name = "elist__" + self.parentsName(
            parentage
        ).replace("/", "__")

        prev_cache = self.getPreviousCache(parentage)
        snode = get_parent_sample(self, parentage)

        self.state.cache = snode.sample.cacheEntries(elist_name, str(total_cut), cache=prev_cache)
        
        ncur = -1 if not self.state.cache else self.state.cache.GetN()
        nprev = -1 if not prev_cache else prev_cache.GetN()
        
        logger.info("Processed cut %s%s => %d -> %d" % (len(parentage)*".", self.name, nprev, ncur))
        return (self.state.cache.GetN(), r)

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

class DictSaver(PatternDict):
    def save(self, path, obj):
        self[path] = obj

if __name__=="__main__":
    print "Constructing analysis tree..."

    parser = argparse.ArgumentParser(
        description='Produces a hierarchy of histograms corresponding to cuts and weights.'
    )

    parser.add_argument('outfile', action='store',
        help="The output file name with histograms."
    )

    parser.add_argument('infiles', nargs='+',
        help="The input file names with step3 TTrees."
    )

    args = parser.parse_args()

    graph = nx.DiGraph()

    #Create the sink to a file
    hsaver = ObjectSaver(args.outfile)

    #Load the samples
    sample_nodes = [
        SampleNode(hsaver, graph, inf, [], []) for inf in args.infiles
    ]

    #Different lepton channels
    channel = Node(graph, "channel", sample_nodes, [])
    channels = dict()

    # sample --> channels['mu'], channels['ele']
    channels['mu'] = CutNode(
        Cuts.hlt("mu")*Cuts.lepton("mu"),
        graph, "mu", [channel], [], filter_funcs=[lambda x: is_samp(x, 'mu')]
    )
    channels['ele'] = CutNode(
        Cuts.hlt("ele")*Cuts.lepton("ele"),
        graph,
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
            graph, lep + "__iso", par, [],
            filter_funcs=[lambda x: "/iso/" in x[0].name]
        )
        isol.append(isos[lep]['iso'])

        #Antiiso with variations in the isolation cut
        for aiso_syst in ["nominal", "up", "down"]:
            #dR with variations
            for dr_syst in ["nominal", "up", "down"]:
                cn = 'antiiso_' + aiso_syst + '_dR_' + dr_syst
                isos[lep][cn] = CutNode(
                    #Apply any additional anti-iso cuts (like dR) along with antiiso variations.
                    Cuts.antiiso(lep, aiso_syst) * Cuts.deltaR_QCD(dr_syst),
                    graph, lep + "__" + cn, par, [],
                    filter_funcs=[is_samp("antiiso"), is_samp("data")]
                )
                isol.append(isos[lep][cn])

    # [iso, antiiso] --> jet --> [jets2-3]
    jet = Node(graph, "jet", isol, [])
    jets = dict()
    for i in [2,3]:
        jets[i] = CutNode(Cuts.n_jets(i), graph, "%dj"%i, [jet], [])

    tag = Node(graph, "tag", jet.children(), [])
    tags = dict()
    for i in [0,1,2]:
        tags[i] = CutNode(Cuts.n_tags(i), graph, "%dt"%i, [tag], [])


    #The primary MET/MTW cut node
    met = Node(graph, "met", tag.children(), [])

    mets = dict()

    #No MET cut requirement
    mets['off'] = CutNode(Cuts.no_cut, graph, "met__off", [met], [],
    )

    for met_syst in ["nominal", "up", "down"]:
        mets['met_' + met_syst] = CutNode(
            Cuts.met(met_syst),
            graph, "met__met_" + met_syst,
            [met], [],
            filter_funcs=[lambda x: is_chan(x, 'ele')]
        )
        mets['mtw_' + met_syst] = CutNode(
            Cuts.mt_mu(met_syst),
            graph, "met__mtw_" + met_syst, [met], [],
            filter_funcs=[lambda x: is_chan(x, 'mu')]
        )

    # purifications ---> cutbased, MVA
    purification = Node(graph, "signalenr", met.children(), [])
    purifications = dict()
    purifications['cutbased'] = Node(graph, "cutbased", [purification], [])
    purifications['mva'] = Node(graph, "mva", [purification], [])

    # cutbased ---> Mtop ---> SR
    mtop = Node(graph, "mtop", [purifications['cutbased']], [])
    mtops = dict()
    mtops['SR'] = CutNode(Cuts.top_mass_sig, graph, "mtop__SR", [mtop], [])

    # Mtop children ---> etalj ---> |etalj|>2.5
    etalj = Node(graph, "etalj", mtop.children(), [])
    etaljs = dict()
    etaljs['greater__2_5'] = CutNode(Cuts.eta_lj,
        graph, "etalj__g2_5", [etalj], []
    )

    # MVA ---> MVA ele, MVA mu
    mvas = NestedDict()

    for lepton in ['mu', 'ele']:
        for name, mva_cut in Cuts.mva_wps['bdt'][lepton].items():
            cval = str(mva_cut).replace(".", "_")
            mva_name = 'mva__%s__%s__%s' % (lepton, name, cval)
            mvas[lepton][cval] = CutNode(
                Cut("%s >= %f" % (Cuts.mva_vars[lepton], mva_cut)),
                graph, mva_name, [purifications['mva']], [],
                filter_funcs=[lambda _x,_lepton=lepton: is_chan(_x, _lepton)]
            )

    #After which cuts do you want the reweighed plots?
    plot_nodes = etalj.children() + purifications['mva'].children()

    from histo_descs import create_plots
    create_plots(graph, plot_nodes)

    print "Done constructing analysis tree..."
    print "Starting projection..."

    try:
        nx.write_dot(graph, args.outfile.replace(".root", "_gviz.dot"))
    except Exception as e:
        logger.warning("Couldn't write .dot file for visual representation of analysis: %s" % str(e))

    #Make everything
    t0 = time.clock()
    for sn in sample_nodes:
        sn.recurseDown()
    t1 = time.clock()
    dt = t1-t0
    if dt<1.0:
        dt = 1.0
    out.tfile.Close()
    #print "Projected out %d histograms in %.f seconds, %.2f/sec" % (HistNode.nHistograms, dt, float(HistNode.nHistograms)/dt)
