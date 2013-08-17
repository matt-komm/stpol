from plots.common.cuts import Weights, mul
from tree import (
    WeightNode, is_chan, is_mc
)
import logging, copy
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def reweight(node, weights):
    """
    Takes a Node and a list of WeightNodes and adds this Node
    as a child of all the WeightNodes. The heritage is reordered and
    all previous parents of 'node' are disconnected and reconnected
    to the weight nodes.

    Args:
        node: a Node object to reweight
        weights: a list of WeightNodes

    Returns:
        the input node
    """
    logger.debug("Reweighting node %s" % node)
    parents = node.parents()
    #1. Get the parents of the node to be reweighted
    pars = copy.copy(parents)

    #2. Remove any current parents from the reweighted node
    node.delParents(parents)

    for w in weights:

        logger.debug("Adding parents to weight node %s" % w)
        #Add the previous parents from 1. as the parents of the WeightNode
        w.addParents(pars)

        #Add this WeightNode as the parent of the input node 
        node.addParents([w])
    return node


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

#Separate lepton weights for mu/ele
weights_lepton = dict()
weights_lepton['mu'] = Weights.muon_sel.items()
weights_lepton['ele'] = Weights.electron_sel.items()

#Other weights are the same for both channels
weights_syst = [
    ("btag", Weights.btag_syst),
    ("wjets_yield", Weights.wjets_yield_syst),
    ("wjets_shape", Weights.wjets_shape_syst),
    ("pu", Weights.pu_syst),
]

#Now make all the weight combinations for mu/ele, variating one weight
weights_total = dict()
def syst_weights(graph):
    _syst_weights = []
    for lepton, w in weights_lepton.items():
        weights_var_by_one = variateOneWeight([x[1] for x in (weights_syst+w)])

        # The unvariated weight is taken as the list of the 0th elements of the
        # weight tuples
        weights_var_by_one.append(
            ("nominal", [x[1][0] for x in (weights_syst+w)])
        )

        wtot = []
        for wn, s in weights_var_by_one:
            j = mul(s) #Multiply together the list of weights
            wtot.append((wn, j))

        for name, j in wtot:
            filter_funcs=[
                #Apply the weights separately for the lepton channels
                lambda _x,_lepton=lepton: is_chan(_x, _lepton),
                
                #Apply only in MC
                is_mc
            ]

            #Apply systematic weights only in case of nominal samples
            if name != "nominal":
                filter_funcs += [
                    #Check if the parent was a nominal sample
                    lambda _x: "/nominal/" in _x[0].name
                ]

            syst = WeightNode(
                j, graph, "weight__" + name + "__" + lepton,
                [], [], filter_funcs=filter_funcs
            )
            logger.debug("Appending weight %s" % syst.name)
            _syst_weights.append(syst)


        #Always produce the unweighted plot
        unw = WeightNode(
            Weights.no_weight, graph, "weight__unweighted",
            [], []
        )
        _syst_weights.append(unw)
    return _syst_weights