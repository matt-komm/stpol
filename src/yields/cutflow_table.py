# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

from plots.common.utils import PhysicsProcess, get_file_list, NestedDict
from plots.common.sample import Sample
from plots.common.cuts import Cuts, Weights
from plots.common.cross_sections import lumis
import sys
from plots.common.utils import escape, NestedDict, OrderedDict
from rootpy.plotting import Hist
import tabulate
from plots.common.utils import merge_hists
from control_plots.an_plots import scale_factors
from plots.syst_band import rescale_to_fit
import copy, os
import cPickle as pickle
import ConfigParser

def make_dir(ofname):
    base = os.path.dirname(ofname)
    if not os.path.exists(base):
        os.makedirs(base)

order = [
    'diboson', 'WJets', 'DYJets', 'TTJets',
    'tWchan', 'schan', 'qcd', 'tchan', 'mc', 'data'
]

if __name__=="__main__":

    config = ConfigParser.SafeConfigParser()
    config.read(sys.argv[1])

    channel = config.get('Base', 'channel')
    dbase = config.get('Base', 'datadir')
    output_file = "results/yield_tables/cutflow_%s" % channel
    make_dir(output_file)
    lumi = lumis["343e0a9_Aug22"]["iso"][channel]

    md = PhysicsProcess.get_merge_dict(PhysicsProcess.get_proc_dict(channel))
    if channel=="mu":
        md['qcd'] = ['QCDMu']
    elif channel=="ele":
        md['qcd'] = ['QCD.*']
    md['data'] = md.pop('data')

    fnames = dict()
    fnames["mc"] = get_file_list(md, dbase + "/mc/iso/nominal/Jul15")
    fnames["mc"] += get_file_list(md, dbase + "/mc/iso/nominal/Jul15_qcd")
    fnames["data"] = get_file_list(md, dbase + "/data/iso/*/")
    fnames["data_aiso"] = get_file_list({'qcd':['Single.*']}, dbase + "/data/antiiso/*/")

    if channel=="mu" and len(fnames['mc'])!= 17:
        raise ValueError("Incomplete MC sample set")

    print "Loading samples"
    files = [Sample.fromFile(fn) for fn in fnames["mc"] + fnames["data"]]
    files_antiiso = [Sample.fromFile(fn) for fn in fnames["data_aiso"]]

    print "Loaded %d files" % (len(files) + len(files_antiiso))
    for sample in files:
        print sample.name, sample.getEventCount()

    def cutsequence(channel, cut="mva"):
        base = [Cuts.hlt(channel)*Cuts.lepton(channel), Cuts.metmt(channel), Cuts.n_jets(2), Cuts.rms_lj, Cuts.n_tags(1)]
        if cut == "mva":
            base += [Cuts.mva_wp(channel)]
        return base

    # <codecell>

    def cutflow(channel, cuts, cutnames):
        samp_hists = NestedDict()
        for s in files:
            print "Processing sample %s" % s.name
            cut = Cuts.no_cut
            cache = 0
            for new_cut, name in zip(cuts, cutnames):
                cut = cut * new_cut
                cache = s.cacheEntries("cache_%s" % name, str(cut), cache)
                hist = s.drawHistogram(
                    "cos_theta", str(cut),
                    weight=str(Weights.total_weight(channel)),
                    binning=[20, -1, 1], entrylist=cache
                )
                if s.isMC:
                    hist.Scale(s.lumiScaleFactor(lumi))
                hist.SetName(name)
                samp_hists[name][s.name] = hist
        cut = Cuts.no_cut
        for new_cut, name in zip(cuts, cutnames):
            cut = cut * new_cut
            samp_hists[name]["data_qcd"] = None
            for s in files_antiiso:
                h = s.drawHistogram("cos_theta", str(cut*Cuts.antiiso(channel)*Cuts.deltaR_QCD()), binning=[20, -1, 1])
                if not samp_hists[name]["data_qcd"]:
                    samp_hists[name]["data_qcd"] = h
                else:
                    samp_hists[name]["data_qcd"] += h
        return samp_hists.as_dict()

    # <codecell>

    cs = cutsequence(channel)
    cutnames = ["hlt+lep", "met", "jet", "jet_rms", "tag", "mva"]

    # <codecell>

    hi = cutflow(channel, cs, cutnames)

    # <codecell>

    # <codecell>

    mhists = OrderedDict()
    def calc_mc(hd):
        return reduce(lambda x,y: x+y, [h for k,h in hd.items() if k not in ["data", "mc", "data_qcd"]])

    for cutname, hists in hi.items():
        mhists[cutname] = merge_hists(hists, md)
        mhists[cutname]['mc'] = calc_mc(mhists[cutname])#reduce(lambda x,y: x+y, [h for h in mhists[cutname].values() if h.GetName()!="data"])
        #mhists[cutname]['data'] = mhists[cutname].pop('data')
    mhists['mva']['qcd'] = hi['tag']['data_qcd']
    mhists['bdt_fit'] = copy.deepcopy(mhists['mva'])
    for sample, hist in mhists['bdt_fit'].items():
        rescale_to_fit(sample, hist, scale_factors(channel, "2j1t_mva_loose"))
    mhists['bdt_fit']['mc'] = calc_mc(mhists['bdt_fit'])

    table = []
    for cutname, hists in mhists.items():
        row = [cutname]
        for process in order:
            h = hists[process]
            row.append(h.Integral())
        table.append(row)

    for l in map(len, table):
        if l!= 11:
            raise Exception("Malformed table, something was missing")

    pickle.dump(table, open(output_file+".pickle", "wb"))

    pretty_table = tabulate.tabulate(table, headers=order, numalign="right", floatfmt=".0f", tablefmt="rst")
    of = open(output_file + ".txt", "w")
    of.write(pretty_table)
    of.close()

    print pretty_table

