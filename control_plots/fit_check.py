from rootpy.io import File
from os.path import join
from plots.common.hist_plots import plot_hists_dict
from plots.common.histogram import norm
from plots.common.utils import NestedDict

from plots.common.tdrstyle import tdrstyle
if __name__=="__main__":
    tdrstyle()
    f = File("lqetafit/histos/lqeta.root")

    hists = dict()
    for root, dirs, items in f.walk():
        for i in items:
            spl = i.split("__")
            if len(spl)!=2:
                continue
            print spl
            name = spl[1]
            hists[name] = f.Get(join(root, i))
            hists[name].SetTitle(name)
            norm(hists[name])
    canv1 = plot_hists_dict(hists, x_label="#eta_{lj}")

    hists_syst = NestedDict()
    for root, dirs, items in f.walk():
        for i in items:
            spl = i.split("__")
            if len(spl)!=4:
                continue

            systname = spl[2]
            updown = spl[3]
            name = spl[1]
            name += "_" +systname + "_" + updown
            hists_syst[systname][name] = f.Get(join(root, i))
            hists_syst[systname][name].SetTitle(name)
            norm(hists_syst[systname][name])
    canv2 = plot_hists_dict(hists_syst["muonID"], x_label="#eta_{lj}", legend_pos="top-left")