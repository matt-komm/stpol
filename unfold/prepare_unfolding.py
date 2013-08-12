from ROOT import TH1, TH2, TFile
#from binnings import *
from plots.common.utils import get_file_list, PhysicsProcess, merge_hists, mkdir_p, setErrors
from plots.common.sample import Sample
from plots.common.cross_sections import lumi_iso
import numpy
import math
from plots.common.make_systematics_histos import generate_out_dir, generate_systematics, make_systematics_histos
from unfold.utils import asymmetry_weight
from os.path import join
import os
from plots.common.cuts import *
import argparse
#from StringIO import StringIO
from rootpy.io import root_open
import shutil
import logging

logging.basicConfig(level=logging.INFO)

MAXBIN = 10000

var_min = -1
var_max = 1
var_x = "true_cos_theta"
var_y = "cos_theta"

def merge_anomalous(proc, coupling):
    return PhysicsProcess.get_merge_dict(PhysicsProcess.get_proc_dict(proc, coupling))

def get_signal_samples(coupling, step3='/'.join([os.environ["STPOL_DIR"], "step3_latest"]), proc="mu"):
    samples={}
    # Load in the data
    if coupling == "powheg":
        datadir = '/'.join([step3, proc, "mc", "iso", "nominal", "Jul15"])
    else:
        datadir = "/".join(("/home", "andres", "single_top", "stpol", "out", "step3_anomalous", proc, "syst_07_28", "iso", "SYST"))
        #datadir = '/'.join([step3, proc, "mc_syst", "iso", "SYST", "Jul15"])
    flist=get_file_list(merge_anomalous(proc, coupling), datadir, False)
    #Load signal samples in the isolated directory
    for f in flist:
        #print f, coupling, f.endswith("Nu_t-channel.root"), f.endswith("ToLeptons.root")
        if f.endswith("ToLeptons.root") or (coupling == "comphep" and f.endswith("Nu_t-channel.root")) or ("anomWtb" in coupling and coupling in f):
            samples[f] = Sample.fromFile(datadir+'/'+f, tree_name='Events')
    if coupling == "powheg":
        assert len(samples) == 2
    else:
        assert len(samples) == 3
    return samples

def get_signal_histo(var, weight, step3='/'.join([os.environ["STPOL_DIR"], "step3_latest"]), cuts="1", proc="mu", coupling="powheg", asymmetry=None):
    lumi = lumi_iso[proc]
    plot_range = [MAXBIN, var_min, var_max]
    hists_mc = {}
    samples = get_signal_samples(coupling, step3, proc)
    if asymmetry is not None:
        weight = asymmetry_weight(asymmetry, weight)
    for name, sample in samples.items():
        if sample.isMC:
            hist = sample.drawHistogram(var, cuts, weight=weight, plot_range=plot_range)
            hist.Scale(sample.lumiScaleFactor(lumi))
            hists_mc[sample.name] = hist
    merged_hists = merge_hists(hists_mc, merge_anomalous(proc, coupling)).values()
    assert len(merged_hists) == 1
    setErrors(merged_hists[0])
    return merged_hists[0]


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
    return (numpy.array(binning_gen), numpy.array(binning_rec))


def no_rebin(cuts, weight, bins_x, bins_y, indir, proc = "mu", mva_cut = None, coupling = "powheg", asymmetry=None):
    #print proc, "cos_theta", mva_cut, coupling, tag
    outdir = '/'.join([os.environ["STPOL_DIR"], "unfold", "histos", generate_out_dir(proc, "cos_theta", mva_cut, coupling, asymmetry)])
    mkdir_p(outdir)
    fo = root_open(outdir+"/rebinned.root","recreate")
    
    TH1.SetDefaultSumw2(True)
    TH2.SetDefaultSumw2(True)
    lumi = lumi_iso[proc]
    #plot_range = [100,-1,1]
    hists_presel = {}
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
        hist_presel = sample.drawHistogram(var_x, cuts_presel, weight=presel_weight, plot_range=bins_x)
        hist_presel.Scale(sample.lumiScaleFactor(lumi))
        hists_presel[sample.name] = hist_presel
    
    merged_gen_presel = merge_hists(hists_presel, merge_anomalous(proc, coupling)).values()[0]#hists_presel["T_t_ToLeptons"]#

    assert len(merge_hists(hists_presel, merge_anomalous(proc, coupling)).values()) == 1
    setErrors(merged_gen_presel)
    hists_gen= {}
    hists_rec= {}
    
    for name, sample in samples.items():
        hist_gen = sample.drawHistogram(var_x, cuts, weight=weight, plot_range=bins_x)
        hist_gen.Scale(sample.lumiScaleFactor(lumi))
        hists_gen[sample.name] = hist_gen
        
        hist_rec = sample.drawHistogram(var_y, cuts, weight=weight, plot_range=bins_y)
        hist_rec.Scale(sample.lumiScaleFactor(lumi))
        
        hists_rec[sample.name] = hist_rec
    
    merged_gen = merge_hists(hists_gen, merge_anomalous(proc, coupling)).values()[0] #hists_gen["T_t_ToLeptons"]
    merged_rec = merge_hists(hists_rec, merge_anomalous(proc, coupling)).values()[0]#hists_rec["T_t_ToLeptons"]#
    
    print merged_gen.GetEntries(), merged_gen.Integral()
    print merged_rec.GetEntries(), merged_rec.Integral()
    setErrors(merged_gen)
    setErrors(merged_rec)

    merged_gen.SetNameTitle("hgen", "hgen")
    merged_rec.SetNameTitle("hrec", "hrec")
    
    heff = merged_gen.Clone("efficiency")
    heff.SetTitle("efficiency")
    heff.Divide(merged_gen_presel)
    
    fo.cd()
    merged_gen_presel.SetNameTitle("hgen_presel", "hgen_presel")
    merged_gen_presel.Write()

    merged_gen.Write()
    merged_rec.Write()
    heff.Write()



    lumi = lumi_iso[proc]
    #hists_rec = {}  
    #hists_gen = {}
    matrices = {}
    #samples = get_signal_samples(coupling, indir, proc)
    if asymmetry is not None:
        weight = asymmetry_weight(asymmetry, weight)
    for name, sample in samples.items():
        #hist_rec = sample.drawHistogram(var_y, cuts, weight=weight, plot_range=bins_y)
        #hist_rec.Scale(sample.lumiScaleFactor(lumi))
        #hists_rec[sample.name] = hist_rec
        #hist_gen = sample.drawHistogram(var_x, cuts, weight=weight, plot_range=bins_x)
        #hist_gen.Scale(sample.lumiScaleFactor(lumi))
        #hists_gen[sample.name] = hist_gen
        matrix = sample.drawHistogram2D(var_x, var_y, cuts, weight=weight, plot_range_x=bins_x, plot_range_y=bins_y)
        matrix.Scale(sample.lumiScaleFactor(lumi))
        matrices[sample.name] = matrix

    merged_matrix = merge_hists(matrices, merge_anomalous(proc, coupling)).values()[0]
    matrixWithEff = merged_matrix.Clone("matrixEff")
    (bin_x, a, b) = bins_x
    #fill underflows    
    for i in range(1,bin_x+1):
        matrixWithEff.SetBinContent(i,0,merged_gen_presel.GetBinContent(i)*(1-heff.GetBinContent(i)))
    
    #assert len(merged_rec) == 1
    #assert len(merged_gen) == 1
    setErrors(merged_rec)
    setErrors(merged_gen)
    #The should be nothing in overflow bins, if it happens there is, make some changes
    assert merged_gen.GetBinContent(0) == 0.0
    assert merged_gen.GetBinContent(bins_x[0]+1) == 0.0
    assert merged_rec.GetBinContent(0) == 0.0
    assert merged_rec.GetBinContent(bins_y[0]+1) == 0.0

    fo.cd()
	# write histos
    #merged_rec[0].SetName(var_y+"_rebin")
    #merged_gen[0].SetName(var_x+"_rebin")
    merged_matrix.SetName("matrix")
    #merged_rec[0].Write()
    #merged_gen[0].Write()
    merged_matrix.Write()
    matrixWithEff.Write() 
    fo.Close()

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

def efficiency_norebin(cuts, weight, binning_x, indir, proc="mu", mva_cut = None, coupling="powheg", asymmetry=None):
    outdir = '/'.join([os.environ["STPOL_DIR"], "unfold", "histos", generate_out_dir(proc, "cos_theta", mva_cut, coupling, asymmetry)])
    fo = TFile(outdir+"/efficiency.root","RECREATE")
    fo.cd()
    
    

def efficiency(cuts, weight, binning_x, indir, proc="mu", mva_cut = None, coupling="powheg", asymmetry=None):
    outdir = '/'.join([os.environ["STPOL_DIR"], "unfold", "histos", generate_out_dir(proc, "cos_theta", mva_cut, coupling, asymmetry)])
    fo = TFile(outdir+"/efficiency.root","RECREATE")
    fo.cd()
    
    ROOT.TH1.SetDefaultSumw2(True)
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

def make_histos(binning, cut_str, cut_str_antiiso, indir, channel, mva_cut, coupling, asymmetry):
    systematics = generate_systematics(channel, coupling)
    var = "cos_theta"
    subdir = generate_out_dir(channel, var, mva_cut, coupling, asymmetry)
    outdir = '/'.join([os.environ["STPOL_DIR"], "unfold", "histos", "input", subdir])
    make_systematics_histos(var, cut_str, cut_str_antiiso, systematics, outdir, indir, channel, coupling, binning=binning, asymmetry=asymmetry)
    shutil.move('/'.join([os.environ["STPOL_DIR"], "unfold", "histos", "input", subdir])+"/lqeta.root", '/'.join([os.environ["STPOL_DIR"], "unfold", "histos", subdir])+"/data.root")

def make_histos_norebin(binning, cut_str, cut_str_antiiso, indir, channel, mva_cut, coupling, asymmetry):
    systematics = generate_systematics(channel, coupling)
    var = "cos_theta"
    subdir = generate_out_dir(channel, var, mva_cut, coupling, asymmetry)
    outdir = '/'.join([os.environ["STPOL_DIR"], "unfold", "histos", "input", subdir])
    make_systematics_histos(var, cut_str, cut_str_antiiso, systematics, outdir, indir, channel, coupling, plot_range=binning, asymmetry=asymmetry)
    shutil.move('/'.join([os.environ["STPOL_DIR"], "unfold", "histos", "input", subdir])+"/lqeta.root", '/'.join([os.environ["STPOL_DIR"], "unfold", "histos", subdir])+"/data.root")


def load_binning(infile):
    f = open(infile)
    #print f.read()
    (bin_list_gen, bin_list_rec) =  f.read().replace("\n","").replace("]", "").replace("[", "").split(";")
    bin_list_gen = numpy.genfromtxt(StringIO(bin_list_gen))
    bin_list_rec = numpy.genfromtxt(StringIO(bin_list_rec))
    return (bin_list_gen, bin_list_rec)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Makes systematics histograms for final fit')
    parser.add_argument('--channel', dest='channel', choices=["mu", "ele"], required=True, help="The lepton channel used")
    parser.add_argument('--path', dest='path', default="$STPOL_DIR/step3_latest/", required=True)
    parser.add_argument('--mva', dest='mva', action='store_true', default=False, help="Use MVA cut, not eta")
    parser.add_argument('--mva_var', dest='mva_var', default="mva_BDT", help="MVA variable name")
    parser.add_argument('--mva_cut', dest='mva_cut', type=float, default=-1, help="MVA cut value")
    parser.add_argument('--coupling', dest='coupling', choices=["powheg", "comphep", "anomWtb-0100", "anomWtb-unphys"], default="powheg", help="Coupling used for signal sample")
    parser.add_argument('--binning', dest='binning', help="File from which to load a pre-calculated binning")
    parser.add_argument('--asymmetry', dest='asymmetry', help="Asymmetry to reweight generated distribution to", default=None)
    args = parser.parse_args()

    indir = args.path    

    #indir = '/'.join([os.environ["STPOL_DIR"], "step3_latest"])
    if(args.mva):
        cut_str = str(Cuts.mva_iso(args.channel, args.mva_cut, args.mva_var))
        cut_str_antiiso = str(Cuts.mva_antiiso(args.channel, args.mva_cut, args.mva_var))
    else:
        cut_str = str(Cuts.final_iso(args.channel))
        cut_str_antiiso = str(Cuts.final_antiiso(args.channel))
    weight = str(Weights.total_weight(args.channel))
    
    """bins_gen = 7
    bins_rec = bins_gen * 2
    zerobin_gen = 2
    zerobin_rec = 4
    if args.binning and len(args.binning) > 0:
        (bin_list_gen, bin_list_rec) = load_binning(args.binning)
    else:
        (bin_list_gen, bin_list_rec) = findbinning(bins_gen, cut_str, weight, indir, args.channel, args.coupling, zerobin_gen, zerobin_rec, args.asymmetry)
    #bin_list_gen = numpy.array([-1.,    -0.2632, 0.0,   0.19,    0.3528,  0.5062,  0.6652,  1.    ])
    #bin_list_rec = numpy.array([-1.,     -0.4496, -0.2254, -0.069,   0.0,   0.1478,  0.2346,  0.3174,  0.3956,   0.4738,  0.545,   0.6112,  0.6866,  0.7714,  1.    ])
    system.exit(1)
    binning_file = open('binnings/'+generate_out_dir(args.channel, "cos_theta", args.mva_cut, args.coupling, args.asymmetry)+'.txt', 'w')
    binning_file.write(str(bin_list_gen)+';\n')
    binning_file.write(str(bin_list_rec))
    binning_file.close()
    
    print "found binning: ", bin_list_gen, ";", bin_list_rec
    """
    #Ignore the binning stuff for now...maybe still needed later. Just same sized bins now
    bins_rec = [16, -1, 1]
    bins_gen = [8, -1, 1]
    #rebin(cut_str, weight, bins_gen, bin_list_gen, bins_rec, bin_list_rec, indir, args.channel, args.mva_cut, args.coupling, args.asymmetry)
    no_rebin(cut_str, weight, bins_gen, bins_rec, indir, args.channel, args.mva_cut, args.coupling, args.asymmetry)
    #efficiency(cut_str, weight, bin_list_gen, indir, args.channel, args.mva_cut, args.coupling, args.asymmetry)
    #efficiency_norebin(cut_str, weight, bins_gen, indir, args.channel, args.mva_cut, args.coupling, args.asymmetry)
    #make_histos(bin_list_rec, cut_str, cut_str_antiiso, indir, args.channel, args.mva_cut, args.coupling, args.asymmetry)
    make_histos_norebin(bins_rec, cut_str, cut_str_antiiso, indir, args.channel, args.mva_cut, args.coupling, args.asymmetry)
    print "finished"
