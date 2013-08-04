import logging
logging.basicConfig(level=logging.INFO)
from plots.common.sample import Sample
from plots.common.cuts import Cuts
import sys
import ROOT
import os
logger = logging.getLogger("make_histo")

hist1 = {
    #'name': 'cos_theta_final_cutbased_2j1t',
    'var': 'cos_theta',
    'plot_range': [100, -1, 1],
    'cut_name': "1.0"
    'cut': str(Cuts.hlt("mu")*Cuts.lepton("mu")*Cuts.final(2,1)),
    'weight': "1.0"
    'cached_cut': False,
}

hists = {
    'hist1': hist1
}

def make_histo(fname, hdict):
    name = hdict['name']
    var = hdict['var']
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
    make_histo(sys.argv[1], hist1)
