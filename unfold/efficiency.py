import os
from plots.common.make_systematics_histos import generate_out_dir#, generate_systematics, make_systematics_histos
from plots.common.utils import mkdir_p, get_file_list, PhysicsProcess, merge_hists#, setErrors
from rootpy.io import root_open
from ROOT import TH1, TH2
from plots.common.cross_sections import lumi_iso
from plots.common.sample import Sample
from plots.common.cuts import *
from plots.common.load_samples import get_sample_names
import shutil

var_min = -1
var_max = 1
var_x = "true_cos_theta"
var_y = "cos_theta"
MAXBIN = 10000

def merge_anomalous(proc, systematic, coupling):
    if coupling != "comphep" and not coupling.startswith("anom"):
        if "tchan_scale" in systematic or "mass" in systematic:
            coupling = systematic
        else:
            coupling = "nominal"
    return PhysicsProcess.get_merge_dict(PhysicsProcess.get_proc_dict(proc, coupling))

def get_signal_samples(coupling, step3='/'.join([os.environ["STPOL_DIR"], "step3_latest"]), proc="mu", systematic="nominal"):
    samples={}
    sample_names = get_sample_names(proc, systematic, coupling)["tchan"]
    # Load in the data
    if coupling == "powheg":
        if systematic in ["En__down", "En__up", "Res__down", "Res__up", "UnclusteredEn__down", "UnclusteredEn__up"]:
            st_pieces = systematic.split("__")
            syst_dir = st_pieces[0]+st_pieces[1].capitalize()
            datadir = '/'.join([step3, proc, "mc", "iso", syst_dir, "Jul15"])
        elif systematic in ["tchan_scale__down", "tchan_scale__up", "mass__up", "mass__down"]:
            datadir = '/'.join([step3, proc, "mc_syst", "iso", "SYST", "Jul15"])        
            #if systematic == "mass__up":
            #    datadir2 = '/'.join([step3, proc, "mc", "iso", "nominal", "Jul15"])
        else:            
            datadir = '/'.join([step3, proc, "mc", "iso", "nominal", "Jul15"])
        
    else:
        datadir = '/'.join([step3, proc, "mc_syst", "iso", "SYST", "Jul15"])    
    flist=get_file_list(merge_anomalous(proc, systematic, coupling), datadir, False)
    #if systematic == "mass__up":
    #    flist.extend(get_file_list(merge_anomalous(proc, systematic, coupling), datadir2, False))
    
    for f in flist:
        if f.replace(".root", "") in sample_names or (coupling == "comphep" and f.endswith("Nu_t-channel.root")) or ("anomWtb" in coupling and coupling in f):
            samples[f] = Sample.fromFile(datadir+'/'+f, tree_name='Events')
    if coupling == "powheg":
        assert len(samples) == 2
    else:
        assert len(samples) == 3
    return samples

def get_signal_histo(var, weight, step3='/'.join([os.environ["STPOL_DIR"], "step3_latest"]), cuts="1", proc="mu", coupling="powheg", asymmetry=None, systematic="nominal"):
    lumi = lumi_iso[proc]
    plot_range = [MAXBIN, var_min, var_max]
    hists_mc = {}
    samples = get_signal_samples(coupling, step3, proc, systematic)
    if asymmetry is not None:
        weight = str(Weight(str(weight)) * Weights.asymmetry_weight(asymmetry))
    for name, sample in samples.items():
        if sample.isMC:
            hist = sample.drawHistogram(var, cuts, weight=weight, plot_range=plot_range)
            hist.Scale(sample.lumiScaleFactor(lumi))
            hists_mc[sample.name] = hist
    merged_hists = merge_hists(hists_mc, merge_anomalous(proc, systematic, coupling)).values()
    assert len(merged_hists) == 1
    #setErrors(merged_hists[0])
    return merged_hists[0]


def efficiency(cuts, weight, bins_x, bins_y, indir, proc = "mu", mva_cut = None, coupling = "powheg", asymmetry=None, extra=None, systematic="nominal"):
    outdir = '/'.join([os.environ["STPOL_DIR"], "unfold", "histos", generate_out_dir(proc, "cos_theta", mva_cut, coupling, asymmetry, extra=extra)])
    try:
        shutil.rmtree(outdir)
    except OSError:
        logging.warning("Couldn't remove directory %s" % outdir)
    mkdir_p(outdir)
        
    fo = root_open(outdir+"/rebinned_"+systematic+".root","recreate")
    
    TH1.SetDefaultSumw2(True)
    TH2.SetDefaultSumw2(True)
    lumi = lumi_iso[proc]
    hists_presel = {}
    samples = get_signal_samples(coupling, indir, proc, systematic)
    cuts_presel = str(Cuts.true_lepton(proc))
    presel_weight = "1"
    if asymmetry is not None:        
        presel_weight = str(Weights.asymmetry_weight(asymmetry))
        weight = str(Weight(str(weight)) * Weights.asymmetry_weight(asymmetry))
    for name, sample in samples.items():
        hist_presel = sample.drawHistogram(var_x, cuts_presel, weight=presel_weight, plot_range=bins_x)
        hist_presel.Scale(sample.lumiScaleFactor(lumi))
        hists_presel[sample.name] = hist_presel
        
    merged_gen_presel = merge_hists(hists_presel, merge_anomalous(proc, systematic, coupling)).values()[0]#hists_presel["T_t_ToLeptons"]#

    assert len(merge_hists(hists_presel, merge_anomalous(proc, systematic, coupling)).values()) == 1
    #setErrors(merged_gen_presel)
    hists_gen = {}
    hists_rec = {}
        
    for name, sample in samples.items():
        hist_gen = sample.drawHistogram(var_x, cuts, weight=weight, plot_range=bins_x)
        hist_gen.Scale(sample.lumiScaleFactor(lumi))
        hists_gen[sample.name] = hist_gen
            
        hist_rec = sample.drawHistogram(var_y, cuts, weight=weight, plot_range=bins_y)
        hist_rec.Scale(sample.lumiScaleFactor(lumi))
            
        hists_rec[sample.name] = hist_rec
        
    merged_gen = merge_hists(hists_gen, merge_anomalous(proc, systematic, coupling)).values()[0] #hists_gen["T_t_ToLeptons"]
    merged_rec = merge_hists(hists_rec, merge_anomalous(proc, systematic, coupling)).values()[0]#hists_rec["T_t_ToLeptons"]#
        
    #print merged_gen.GetEntries(), merged_gen.Integral()
    #print merged_rec.GetEntries(), merged_rec.Integral()
    #setErrors(merged_gen)
    #setErrors(merged_rec)

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


    #Create transfer matrix
    lumi = lumi_iso[proc]
    matrices = {}
    if asymmetry is not None:
        weight = str(Weight(str(weight)) * Weights.asymmetry_weight(asymmetry))
    for name, sample in samples.items():
        matrix = sample.drawHistogram2D(var_x, var_y, cuts, weight=weight, binning_x=bins_x, binning_y=bins_y)
        matrix.Scale(sample.lumiScaleFactor(lumi))
        matrices[sample.name] = matrix

    merged_matrix = merge_hists(matrices, merge_anomalous(proc, systematic, coupling)).values()[0]
    matrixWithEff = merged_matrix.Clone("matrixEff")
    (bin_x, a, b) = bins_x
    #fill underflows    
    for i in range(1,bin_x+1):
        matrixWithEff.SetBinContent(i,0,merged_gen_presel.GetBinContent(i)*(1-heff.GetBinContent(i)))
        
    #assert len(merged_rec) == 1
    #assert len(merged_gen) == 1
    #setErrors(merged_rec)
    #setErrors(merged_gen)
    #The should be nothing in overflow bins, if it happens there is, make some changes
    assert merged_gen.GetBinContent(0) == 0.0
    assert merged_gen.GetBinContent(bins_x[0]+1) == 0.0
    assert merged_rec.GetBinContent(0) == 0.0
    assert merged_rec.GetBinContent(bins_y[0]+1) == 0.0
    fo.cd()
  	# write histos
    merged_matrix.SetName("matrix")
    merged_matrix.Write()
    matrixWithEff.Write()
    fo.Close()
