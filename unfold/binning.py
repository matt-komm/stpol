from efficiency import get_signal_histo, get_signal_samples, var_x, var_y, var_min, var_max, MAXBIN, merge_anomalous
#from prepare_unfolding import 
import math
import numpy
import os
from plots.common.make_systematics_histos import generate_out_dir
from plots.common.utils import mkdir_p, get_file_list, PhysicsProcess, merge_hists, setErrors
from ROOT import TH1, TH2, TFile
from plots.common.cross_sections import lumi_iso
from plots.common.sample import Sample
from plots.common.cuts import *
from plots.common.make_systematics_histos import generate_out_dir, generate_systematics, make_systematics_histos
import shutil

"""
File with rebinning stuff needed to have a special binning.
Not in use currently.
"""


def getbinning(histo, coupling, bins, zerobin=None):
    totint = histo.Integral(0, MAXBIN)
    evbin = totint/bins
    edges = [0.]*(bins+1)
    edges[0] = var_min
    iedge = 1

    prevbin = 0
    zero_set = False
    for k in range(1,MAXBIN+1):
        integral = histo.Integral(prevbin+1, k)
        if(integral>=evbin):
            newedge = histo.GetXaxis().GetBinUpEdge(k)
            #print "edge", newedge, math.fabs(newedge)<0.1
            # Set bin edge to 0 in order to calculate the asymmetry
            #if(math.fabs(newedge)<0.06):
            #    newedge = 0
            if zerobin is not None:
                if math.fabs(newedge)<0.07 and zero_set == False:
                    print "Changing bin %d from %.3f to 0." % (iedge, newedge)
                    newedge = 0.0
                    zero_set = True
                elif newedge>=0.07 and zero_set==False:
                    print "Changing bin %d from %.3f to 0." % (iedge, newedge)
                    newedge = 0.0
                    zero_set = True
                """if coupling in ["powheg", "comphep"] and k==zerobin:
                    print "Changing bin %d from %.3f to 0." % (zerobin, edges[zerobin])
                    newedge = 0.0
                elif math.fabs(newedge)<0.08 and zero_set == False:   #anomalous couplings
                    print "Changing bin %d from %.3f to 0." % (zerobin, edges[zerobin])
                    newedge = 0.0
                    zero_set = True
                elif newedge>=0.08 and zero_set==False:
                    print "Changing bin %d from %.3f to 0." % (zerobin, edges[zerobin])
                    newedge = 0.0
                    zero_set = True"""
            edges[iedge] = newedge
            iedge += 1
            prevbin = k
    
    lastedge = histo.GetXaxis().GetBinUpEdge(MAXBIN)
    edges[bins] = lastedge
    #Set bin #zerobin to zero if parameter set
    return edges

def findbinning(bins_generated, cuts, weight, indir, channel, coupling,  zerobin_gen=None, zerobin_rec=None, asymmetry=None):
    histo_gen = get_signal_histo(var_x, weight, cuts=cuts, step3=indir, coupling=coupling, proc=channel, asymmetry=asymmetry)
    histo_rec = get_signal_histo(var_y, weight, cuts=cuts, step3=indir, coupling=coupling, proc=channel, asymmetry=asymmetry)

    # generated
    binning_gen = getbinning(histo_gen, coupling, bins_generated, zerobin_gen)
    # reconstructed
    binning_rec = getbinning(histo_rec, coupling, bins_generated*2, zerobin_rec)
    return (binning_gen, binning_rec)

def rebin(cuts, weight, bins_x, bin_list_x, bins_y, bin_list_y, indir, proc = "mu", mva_cut = None, coupling = "powheg", asymmetry=None):
    #print proc, "cos_theta", mva_cut, coupling, tag
    outdir = '/'.join([os.environ["STPOL_DIR"], "unfold", "histos", generate_out_dir(proc, "cos_theta", mva_cut, coupling, asymmetry)])
    mkdir_p(outdir)
    fo = TFile(outdir+"/rebinned.root","RECREATE")
    
    # histograms
    #binning_x=(bins_x, numpy.array(bin_list_x))
    #binning_y=(bins_y, numpy.array(bin_list_y))
    binning_x=bin_list_x
    binning_y=bin_list_y
    lumi = lumi_iso[proc]
    hists_rec = {}  
    hists_gen = {}
    matrices = {}
    samples = get_signal_samples(coupling, indir, proc)
    if asymmetry is not None:
        weight = asymmetry_weight(asymmetry, weight)
    for name, sample in samples.items():
        hist_rec = sample.drawHistogram(var_y, cuts, weight=weight, binning=binning_y)
        hist_rec.Scale(sample.lumiScaleFactor(lumi))
        hists_rec[sample.name] = hist_rec
        hist_gen = sample.drawHistogram(var_x, cuts, weight=weight, binning=binning_x)
        hist_gen.Scale(sample.lumiScaleFactor(lumi))
        hists_gen[sample.name] = hist_gen
        matrix = sample.drawHistogram2D(var_x, var_y, cuts, weight=weight, binning_x=binning_x, binning_y=binning_y)
        matrix.Scale(sample.lumiScaleFactor(lumi))
        matrices[sample.name] = matrix

    merged_rec = merge_hists(hists_rec, merge_anomalous(proc, coupling)).values()
    merged_gen = merge_hists(hists_gen, merge_anomalous(proc, coupling)).values()
    merged_matrix = merge_hists(matrices, merge_anomalous(proc, coupling)).values()
    assert len(merged_rec) == 1
    assert len(merged_gen) == 1
    setErrors(merged_rec[0])
    setErrors(merged_gen[0])
    #TODO 2D setErrors(merged_matrix)
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

def efficiency_rebinned(cuts, weight, binning_x, indir, proc="mu", mva_cut = None, coupling="powheg", asymmetry=None):
    outdir = '/'.join([os.environ["STPOL_DIR"], "unfold", "histos", generate_out_dir(proc, "cos_theta", mva_cut, coupling, asymmetry)])
    fo = TFile(outdir+"/efficiency.root","RECREATE")
    fo.cd()
    
    TH1.SetDefaultSumw2(True)
    lumi = lumi_iso[proc]
    plot_range = [100,-1,1]
    hists_presel = {}
    hists_presel_rebin = {}
    samples = get_signal_samples(coupling, indir, proc)
    if proc == "mu":
        cuts_presel = "abs(true_lepton_pdgId)==13"
    elif proc == "ele":
        cuts_presel = "abs(true_lepton_pdgId)==11"
    scales = {}
    presel_weight = "1"
    if asymmetry is not None:
        presel_weight = asymmetry_weight(asymmetry, presel_weight)
        weight = asymmetry_weight(asymmetry, weight)
    for name, sample in samples.items():
        hist_presel = sample.drawHistogram(var_x, cuts_presel, weight=presel_weight, plot_range=plot_range)
        hist_presel.Scale(sample.lumiScaleFactor(lumi))
        hists_presel[sample.name] = hist_presel
        hist_presel_rebin = sample.drawHistogram(var_x, cuts_presel, weight=presel_weight, binning=binning_x)
        hist_presel_rebin.Scale(sample.lumiScaleFactor(lumi))
        #scales[sample.name]= sample.unfoldingLumiScaleFactor(lumi)
        hists_presel_rebin[sample.name] = hist_presel_rebin
    
    merged_gen_presel = merge_hists(hists_presel, merge_anomalous(proc, coupling)).values()[0]#hists_presel["T_t_ToLeptons"]#
    merged_gen_presel_rebin = merge_hists(hists_presel_rebin, merge_anomalous(proc, coupling)).values()[0]#hists_presel_rebin["T_t_ToLeptons"]
    #total_scale = scales["T_t_ToLeptons"] + scales["Tbar_t_ToLeptons"]
    #merged_gen_presel.Scale(total_scale/merged_gen_presel.Integral())
    #merged_gen_presel_rebin.Scale(total_scale/merged_gen_presel_rebin.Integral())

    assert len(merge_hists(hists_presel, merge_anomalous(proc, coupling)).values()) == 1
    assert len(merge_hists(hists_presel_rebin, merge_anomalous(proc, coupling)).values()) == 1
    setErrors(merged_gen_presel)
    setErrors(merged_gen_presel_rebin)
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
    
    merged_gen = merge_hists(hists_gen, merge_anomalous(proc, coupling)).values()[0] #hists_gen["T_t_ToLeptons"]
    merged_gen_rebin = merge_hists(hists_gen_rebin, merge_anomalous(proc, coupling)).values()[0]#hists_gen_rebin["T_t_ToLeptons"]
    merged_rec = merge_hists(hists_rec, merge_anomalous(proc, coupling)).values()[0]#hists_rec["T_t_ToLeptons"]#
    
    print merged_gen.GetEntries(), merged_gen.Integral()
    print merged_gen_rebin.GetEntries(), merged_gen_rebin.Integral()
    print merged_rec.GetEntries(), merged_rec.Integral()
    setErrors(merged_gen)
    setErrors(merged_gen_rebin)
    setErrors(merged_rec)

    merged_gen.SetNameTitle("hgen", "hgen")
    merged_gen_rebin.SetNameTitle("hgen_rebin", "hgen_rebin")
    merged_rec.SetNameTitle("hrec", "hrec")
    
    heff = merged_gen_rebin.Clone("efficiency")
    heff.SetTitle("efficiency")
    heff.Divide(merged_gen_presel_rebin)
    
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


def load_binning(infile):
    f = open(infile)
    #print f.read()
    (bin_list_gen, bin_list_rec) =  f.read().replace("\n","").replace("]", "").replace("[", "").split(";")
    bin_list_gen = numpy.genfromtxt(StringIO(bin_list_gen))
    bin_list_rec = numpy.genfromtxt(StringIO(bin_list_rec))
    return (bin_list_gen, bin_list_rec)


def make_histos_rebinned(binning, cut_str, cut_str_antiiso, indir, channel, mva_cut, coupling, asymmetry):
    systematics = generate_systematics(channel, coupling)
    var = "cos_theta"
    subdir = generate_out_dir(channel, var, mva_cut, coupling, asymmetry)
    outdir = '/'.join([os.environ["STPOL_DIR"], "unfold", "histos", "input", subdir])
    print "BNNG", binning
    #system.exit(1)
    make_systematics_histos(var, cut_str, cut_str_antiiso, systematics, outdir, indir, channel, coupling, binning=binning, asymmetry=asymmetry)
    shutil.move('/'.join([os.environ["STPOL_DIR"], "unfold", "histos", "input", subdir])+"/lqeta.root", '/'.join([os.environ["STPOL_DIR"], "unfold", "histos", subdir])+"/data.root")
