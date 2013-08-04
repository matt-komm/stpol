import logging
logging.basicConfig(level=logging.INFO)
from plots.common.sample import Sample
from plots.common.cuts import Cuts
import sys
import ROOT
import os
import copy
logger = logging.getLogger("make_histo")

cp = copy.deepcopy
hist1 = {
    #'name': 'cos_theta_final_cutbased_2j1t',
    'var': 'cos_theta',
    'plot_range': [100, -1, 1],
    'cut_name': "final_2j1t_cutbased",
    'cut': str(Cuts.hlt("mu")*Cuts.lepton("mu")*Cuts.final(2,1)),
    'weight_name': "nominal",
    'weight': "1.0",
    'cached_cut': False,
}

weight_scenarios = {
    "pu": ("pu_weight", "pu_weight_up", "pu_weight_down"),
    "btag": ("", "pu_weight_up", "pu_weight_down"),
}


hists = {
    'hist1': hist1,
}

def make_histo(fname, hdict):
    var = hdict['var']
    name = "__".join([var, hdict['cut_name'], hdict['weight_name']])
    plot_range = hdict['plot_range']
    cut = hdict['cut']
    weight = hdict['weight']
    ofname = os.path.join("histos/test", fname)
    try:
        os.makedirs(os.path.join(*ofname.split("/")[:-1]))
    except OSError as e:
        pass
    s = Sample.fromFile(fname)
    hist = s.drawHistogram(var, cut, weight=str(weight), plot_range=plot_range)
    if s.isMC:
        try:
            hist.Scale(s.lumiScaleFactor(1))
        except KeyError:
            logger.warning("Couldn't find the cross-section for %s, probably that's OK")
    hist.SetName(name)
    hist.SetTitle(name)
    ofi = ROOT.TFile(ofname, "UPDATE")
    ofi.cd()
    hist.SetDirectory(ofi)
    hist.Write("", ROOT.TObject.kOverwrite)
    #ofi.Write()
    ofi.Close()
    logger.info("Saved histogram %s to file %s" % (name, ofname))

if __name__=='__main__':
    for hn, h in hists.items():
        make_histo(sys.argv[1], h)
