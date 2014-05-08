from rootpy.io import File
from os.path import join
from plots.common.hist_plots import plot_hists_dict
from plots.common.histogram import norm
from plots.common.utils import NestedDict
from fit import *
import argparse
from plots.common.tdrstyle import tdrstyle

"""
$STPOL_DIR/final_fit/compare_template_shapes.py compares the shapes of templates with different systematics and prints out the KS values for non-compatible systematics.
The systematics which match in shape with the nominal should not be used for the fit as the fit might not converge. The are absorbed in the rate uncertainties.
"""
if __name__=="__main__":
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--path', dest='path', default="/hdfs/local/stpol/fit_histograms/07_08_2013/")
    args = parser.parse_args()
    
    for fit in Fit.all_fits:
        print "Processing histograms for fit on", fit.name
        f = File(args.path+fit.name+".root")

        #canv1 = plot_hists_dict(hists, x_label=label, legend_pos="top-right", max_bin_mult=1.2)
        
        systematics = ["Res", "__En", "UnclusteredEn", "ttbar_matching", "ttbar_scale", "leptonID", "leptonTrigger", "wjets_flat", "wjets_shape", "btaggingBC", "btaggingL", "tchan_scale", "wjets_scale", "wjets_matching"]

        if fit.name.startswith("mu"):
            systematics.append("leptonIso")
        
        for syst in systematics:
            nominals = {}
            print syst
            hists = dict()
            for root, dirs, items in f.walk():
                for i in items:
                    spl = i.split("__")
                    if len(spl)==2 or syst in i:
                        if len(spl)==2:
                            nominals[spl[1]] = spl[1]                        
                        #print spl
                        name = spl[1]
                        if len(spl)>2:
                            name += "_"+spl[2]+spl[3]
                        hists[name] = f.Get(join(root, i))
                        #print hists[name]
                        hists[name].SetTitle(name)
                        #norm(hists[name])
            #label = "#eta_{lj}"
            #canv1 = plot_hists_dict(hists, x_label=label, legend_pos="top-right", max_bin_mult=0.5)
            shape_difference = False
            for h in hists:
                for n in nominals:
                    if hists[nominals[n]].GetName() in hists[h].GetName() and not hists[nominals[n]].GetName() == hists[h].GetName():
                        ks_value = hists[h].KolmogorovTest(hists[nominals[n]])
                        h_syst_integral = hists[h].Integral()
                        h_nomi_integral = hists[nominals[n]].Integral()
                        rel_diff = (h_syst_integral - h_nomi_integral) / h_nomi_integral 
                        if ks_value < 0.9:
                            print hists[h].GetName(), "vs", hists[nominals[n]].GetName(), "KS: ", ks_value
                            shape_difference = True
            if shape_difference == False:
                print "Found no shape differences for systematic", syst
