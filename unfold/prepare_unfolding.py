import ROOT
from binnings import *
from plots.common.utils import merge_cmds, merge_hists, get_file_list
from plots.common.sample import Sample
from plots.common.cross_sections import lumi_iso
import numpy
import math
from plots.common.make_systematics_histos import *
import os.path
from plots.common.utils import mkdir_p

MAXBIN = 10000
cuts =  "n_jets==2 && n_tags==1 && top_mass>130 && top_mass<220 && rms_lj<0.025 && mt_mu>50"
weight = "pu_weight*b_weight_nominal*muon_IDWeight*muon_IsoWeight*muon_TriggerWeight*wjets_mg_flavour_flat_weight*wjets_mg_flavour_shape_weight"

def get_signal_samples(proc="mu", step3='/'.join([os.environ["STPOL_DIR"], "step3_latest"])):
    samples={}
    # Load in the data
    datadir = '/'.join([step3, proc, "mc", "iso", "nominal", "Jul15"])
    flist=get_file_list(merge_cmds, datadir, False)
    #Load signal samples in the isolated directory
    for f in flist:
        if f.endswith("ToLeptons.root"):
            samples[f] = Sample.fromFile(datadir+'/'+f, tree_name='Events')
    #assert len(samples) == 2
    return samples

def get_signal_histo(var, step3='/'.join([os.environ["STPOL_DIR"], "step3_latest"]), cuts="1", proc="mu"):
    lumi = lumi_iso[proc]
    plot_range = [MAXBIN, var_min, var_max]
    hists_mc = {}
    samples = get_signal_samples(proc, step3)
    for name, sample in samples.items():
        if sample.isMC:
            hist = sample.drawHistogram(var, cuts, weight=weight, plot_range=plot_range)
            hist.Scale(sample.lumiScaleFactor(lumi))
            hists_mc[sample.name] = hist
    merged_hists = merge_hists(hists_mc, merge_cmds).values()
    assert len(merged_hists) == 1
    return merged_hists[0]


def getbinning(histo, bins):
    totint = histo.Integral(0, MAXBIN)
    evbin = totint/bins

    print "Events: ", totint
    print "Events per bin: ", evbin

    edges = [0.]*(bins+1)
    edges[0] = var_min
    iedge = 1

    prevbin = 0
    for k in range(1,MAXBIN+1):
        integral = histo.Integral(prevbin+1, k)
        #print "int",integral,evbin
        if(integral>=evbin):
            newedge = histo.GetXaxis().GetBinUpEdge(k)
            #print "edge", newedge, math.fabs(newedge)<0.1
            # Set bin edge to 0 in order to calculate the asymmetry
            if(math.fabs(newedge)<0.1):
                newedge = 0

            edges[iedge] = newedge
            iedge+=1
            prevbin = k
    
    lastedge = histo.GetXaxis().GetBinUpEdge(MAXBIN)
    edges[bins] = lastedge
    return edges

def findbinning(bins_generated):
    histo_gen = get_signal_histo(var_x)
    histo_rec = get_signal_histo(var_y)

    # generated
    binning_gen = getbinning(histo_gen, bins_generated)
    # reconstructed
    binning_rec = getbinning(histo_rec, bins_generated*2)
    return (numpy.array(binning_gen), numpy.array(binning_rec))


def rebin(bins_x, bin_list_x, bins_y, bin_list_y, proc = "mu"):
    mkdir_p('/'.join([os.environ["STPOL_DIR"], "unfold", "histos"]))
    fo = ROOT.TFile('/'.join([os.environ["STPOL_DIR"], "unfold", "histos"])+"/rebinned.root","RECREATE")
    
    # histograms
    #binning_x=(bins_x, numpy.array(bin_list_x))
    #binning_y=(bins_y, numpy.array(bin_list_y))
    binning_x=bin_list_x
    binning_y=bin_list_y
    lumi = lumi_iso[proc]

    hists_rec = {}
    hists_gen = {}
    matrices = {}
    samples = get_signal_samples()
    for name, sample in samples.items():
        hist_rec = sample.drawHistogram(var_y, cuts, weight=weight, binning=binning_y)
        hist_rec.Scale(sample.lumiScaleFactor(lumi))
        hists_rec[sample.name] = hist_rec
        hist_gen = sample.drawHistogram(var_x, cuts, weight=weight, binning=binning_x)
        hist_gen.Scale(sample.lumiScaleFactor(lumi))
        hists_gen[sample.name] = hist_gen
        matrix = sample.drawHistogram2D(var_x, var_y, cuts, weight=weight, binning_x=binning_x, binning_y=binning_y)
        matrices[sample.name] = matrix

    merged_rec = merge_hists(hists_rec, merge_cmds).values()
    merged_gen = merge_hists(hists_gen, merge_cmds).values()
    merged_matrix = merge_hists(matrices, merge_cmds).values()
    assert len(merged_rec) == 1
    assert len(merged_gen) == 1
    #The should be nothing in overflow bins, if it happens there is, make some changes
    assert merged_gen[0].GetBinContent(0) == 0.0
    assert merged_gen[0].GetBinContent(bins_x+1) == 0.0
    assert merged_rec[0].GetBinContent(0) == 0.0
    assert merged_rec[0].GetBinContent(bins_y+1) == 0.0

    fo.cd()
	# write histos
    merged_rec[0].SetName(var_y+"_rebin")
    merged_gen[0].SetName(var_x+"_rebin")
    merged_matrix[0].SetName("matrix")
    merged_rec[0].Write()
    merged_gen[0].Write()
    merged_matrix[0].Write()
    fo.Close()

def efficiency(cuts, binning_x, proc="mu"):
    fo = ROOT.TFile('/'.join([os.environ["STPOL_DIR"], "unfold", "histos"])+"/efficiency.root","RECREATE")
    fo.cd()
    
    lumi = lumi_iso[proc]
    plot_range = [100,-1,1]
    hists_presel = {}
    hists_presel_rebin = {}
    samples = get_signal_samples()
    cuts = "abs(true_lepton_pdgId)==13"
    for name, sample in samples.items():
        hist_presel = sample.drawHistogram(var_x, cuts, weight="1", plot_range=plot_range)
        hist_presel.Scale(sample.lumiScaleFactor(lumi))
        hists_presel[sample.name] = hist_presel
        
        hist_presel_rebin = sample.drawHistogram(var_x, cuts, weight="1", binning=binning_x)
        hist_presel_rebin.Scale(sample.lumiScaleFactor(lumi))
        hists_presel_rebin[sample.name] = hist_presel_rebin
        
    merged_gen_presel = merge_hists(hists_presel, merge_cmds).values()[0]
    merged_gen_presel_rebin = merge_hists(hists_presel_rebin, merge_cmds).values()[0]
    
    assert len(merge_hists(hists_presel, merge_cmds).values()) == 1
    assert len(merge_hists(hists_presel_rebin, merge_cmds).values()) == 1
    
    print merged_gen_presel_rebin.Integral()
	
    hists_gen= {}
    hists_gen_rebin = {}
    hists_rec= {}
    
    for name, sample in samples.items():
        hist_gen = sample.drawHistogram(var_x, cuts, weight=weight, plot_range=plot_range)
        hist_gen.Scale(sample.lumiScaleFactor(lumi))
        hists_gen[sample.name] = hist_gen

        hist_gen_rebin = sample.drawHistogram(var_x, cuts, weight=weight, binning=binning_x)
        hist_gen_rebin.Scale(sample.lumiScaleFactor(lumi))
        hists_gen_rebin[sample.name] = hist_gen_rebin
        
        hist_rec = sample.drawHistogram(var_y, cuts, weight=weight, plot_range=plot_range)
        hist_rec.Scale(sample.lumiScaleFactor(lumi))
        hists_rec[sample.name] = hist_rec
        
    merged_gen = merge_hists(hists_gen, merge_cmds).values()[0]
    merged_gen_rebin = merge_hists(hists_gen_rebin, merge_cmds).values()[0]
    merged_rec = merge_hists(hists_rec, merge_cmds).values()[0]
    
    merged_gen.SetNameTitle("hgen", "hgen")
    merged_gen_rebin.SetNameTitle("hgen_rebin", "hgen_rebin")
    merged_rec.SetNameTitle("hrec", "hrec")
    
    heff = merged_gen_rebin.Clone("efficiency")
    heff.SetTitle("efficiency")
    print heff.Integral()
    heff.Divide(merged_gen_presel_rebin)
    print heff.Integral()

    fo.cd()
    
    merged_gen_presel.SetNameTitle("hgen_presel", "hgen_presel")
    merged_gen_presel.Write()
    merged_gen_presel_rebin.SetNameTitle("hgen_presel_rebin", "hgen_presel_rebin")
    merged_gen_presel_rebin.Write()

    merged_gen.Write()
    merged_gen_rebin.Write()
    merged_rec.Write()
    heff.Write()

    fo.Close()

def make_histos(binning):
    cut_str = "n_jets==2 && n_tags==1 && top_mass>130 && top_mass<220 && rms_lj<0.025 && mt_mu>50 && abs(eta_lj)>2.5"
    cut_str_antiiso = cut_str+" && mu_iso>0.3 && mu_iso<0.5 && deltaR_lj>0.3 && deltaR_bj>0.3"
    systematics = generate_systematics()
    var = "cos_theta"
    outdir = '/'.join([os.environ["STPOL_DIR"], "unfold", "histos", "input"])
    make_systematics_histos(var, cut_str, cut_str_antiiso, systematics, outdir, binning=binning)
    shutil.move('/'.join([os.environ["STPOL_DIR"], "unfold", "histos", "input"])+"/lqeta.root", '/'.join([os.environ["STPOL_DIR"], "unfold", "histos"])+"/data.root")

if __name__ == "__main__":
    bins_gen = 7
    bins_rec = bins_gen * 2
    (bin_list_gen, bin_list_rec) = findbinning(bins_gen)
    print "found binning: ", bin_list_gen, ";", bin_list_rec
    rebin(bins_gen, bin_list_gen, bins_rec, bin_list_rec)
    efficiency(cuts, bin_list_gen, proc="mu")
    make_histos(bin_list_rec)
