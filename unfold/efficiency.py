import os
from plots.common.make_systematics_histos import generate_out_dir, calculate_PDF_uncertainties#, generate_systematics, make_systematics_histos
from plots.common.utils import mkdir_p, get_file_list, PhysicsProcess, merge_hists#, setErrors
from rootpy.io import root_open
from ROOT import TH1, TH2
from plots.common.cross_sections import lumi_iso
from plots.common.sample import Sample
from plots.common.cuts import *
from plots.common.load_samples import get_sample_names, change_to_mc_nominal, get_path
import shutil
import rootpy

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
    datadir2 = None
    if coupling == "powheg":
        if systematic in ["En__down", "En__up", "Res__down", "Res__up", "UnclusteredEn__down", "UnclusteredEn__up"]:
            st_pieces = systematic.split("__")
            syst_dir = st_pieces[0]+st_pieces[1].capitalize()
            datadir = '/'.join([step3, proc, "mc", "iso", syst_dir, "Jul15"])
        elif systematic in ["tchan_scale__down", "tchan_scale__up", "mass__up", "mass__down"]:
            #datadir = '/'.join([step3, proc, "mc_syst", "iso", "SYST", "Jul15"]) 
            datadir = "/".join(("/home/andres/single_top/stpol/Sep4_syst_a554579/", proc, "mc_syst", "iso", "SYST", "Jul15"))
            datadir2 = "/".join(("/home/andres/single_top/stpol/Sep4_syst_a554579/", proc, "mc_syst", "iso", "SYST", "Sep4"))
               
            #if systematic == "mass__up":
            
        else:            
            datadir = '/'.join([step3, proc, "mc", "iso", "nominal", "Jul15"])
        
    else:
        datadir = '/'.join([step3, proc, "mc_syst", "iso", "SYST", "Jul15"])    
    flist=get_file_list(merge_anomalous(proc, systematic, coupling), datadir, False)
    if datadir2 is not None:
        flist.extend(get_file_list(merge_anomalous(proc, systematic, coupling), datadir2, False))
    for f in flist:
        if f.replace(".root", "") in sample_names or (coupling == "comphep" and f.endswith("Nu_t-channel.root")) or ("anomWtb" in coupling and coupling in f):
            try:
                samples[f] = Sample.fromFile(datadir+'/'+f, tree_name='Events')
            except rootpy.ROOTError:
                samples[f] = Sample.fromFile(datadir2+'/'+f, tree_name='Events')
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


def efficiency(cuts, weight, bins_x, bins_y, indir, proc = "mu", mva_cut = None, coupling = "powheg", asymmetry=None, extra=None, systematic="nominal", outdir="."):
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
            
        hist_rec = sample.drawHistogram(var_y, cuts, weight=weight, plot_range=bins_y)
        hist_rec.Scale(sample.lumiScaleFactor(lumi))
                     
        hists_gen[sample.name] = hist_gen
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


def get_pdf_stuff(samples, cuts, weight, bins_x, bins_y, indir, proc = "mu", mva_cut = None, coupling = "powheg", asymmetry=None, extra=None, systematic="nominal", outdir="."):
    nPDFSet_size = 44
    
    hists_pdf_std = {}
    hists_pdf_up = {}
    hists_pdf_down = {}
    weight_str = str(Weight(weight) * Weights.pdf_refweight)
    for name, sample in samples.items():
        hname_up = "%s__%s__pdf__up" % (var_y, name)
        hname_down = "%s__%s__pdf__down" % (var_y, name)
        hist_std = sample.drawHistogram(var_y, cuts, weight=weight_str, plot_range=bins_y)
        hist_plus = hist_std.Clone(hname_up)
        hist_minus = hist_std.Clone(hname_down)
        weighted_histos = []    
        for i in range(nPDFSet_size):
            print "pdf nr = ", i
            #weight_pdf = str(weight * Weights.pdf_refweight * Weight("pdf_weights_CT10["+str(i)+"]"))
            #weight_pdf = str(Weight(weight) * Weights.pdf_refweight * Weight("pdf_weights_MSTW2008nlo68cl["+str(i)+"]"))
            weight_pdf = str(Weight(weight) * Weights.pdf_refweight * Weight("pdf_weights_cteq66["+str(i)+"]"))
            hist = sample.drawHistogram(var_y, cuts, weight=weight_pdf, plot_range=bins_y)
            hist.SetDirectory(0)
            weighted_histos.append(hist)
        calculate_PDF_uncertainties(hist_std, weighted_histos, hist_plus, hist_minus, False)
        hists_pdf_std[sample.name] = hist_std
        hists_pdf_up[sample.name] = hist_plus
        hists_pdf_down[sample.name] = hist_minus
        #hists_pdf_weig[sample.name] = hist_std
    return (hists_pdf_up, hists_pdf_down)

def efficiency_pdf(cuts, weight, bins_x, bins_y, indir, proc = "mu", mva_cut = None, coupling = "powheg", asymmetry=None, extra=None, systematic="nominal", outdir="."):
    #outfile = File(outdir + "/%s_%s.root" % (sampn,hname), "RECREATE")
    
    TH1.SetDefaultSumw2(True)
    TH2.SetDefaultSumw2(True)
    lumi = lumi_iso[proc]
    hists_presel = {}
    samples = get_signal_samples(coupling, indir, proc, systematic)
    (hists_pdf_up, hists_pdf_down) = get_pdf_stuff(samples, cuts, weight, bins_x, bins_y, indir, proc, mva_cut, coupling, asymmetry, extra, systematic, outdir)
    for systematic in ["pdf__up", "pdf__down"]:
        fo = root_open(outdir+"/rebinned_"+systematic+".root","recreate")
        cuts_presel = str(Cuts.true_lepton(proc))
        presel_weight = "1"
        #weight = Weight(weight) * Weights.pdf_refweight
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
                
            hist_rec = sample.drawHistogram(var_y, cuts, weight=weight, plot_range=bins_y)
            hist_rec.Scale(sample.lumiScaleFactor(lumi))

            for bin in range(1, hist_rec.GetNbinsX()+1):
                if systematic == "pdf__up":
                    hist_rec.SetBinContent(bin, hist_rec.GetBinContent(bin) * (1 + hists_pdf_up[sample.name].GetBinContent(bin)))
                    hist_gen.SetBinContent(bin, hist_gen.GetBinContent(bin) * (1 + hists_pdf_up[sample.name].GetBinContent(bin)))
                elif systematic == "pdf__down":
                    hist_rec.SetBinContent(bin, hist_rec.GetBinContent(bin) * (1 - hists_pdf_down[sample.name].GetBinContent(bin)))
                    hist_gen.SetBinContent(bin, hist_gen.GetBinContent(bin) * (1 - hists_pdf_down[sample.name].GetBinContent(bin)))
            hists_gen[sample.name] = hist_gen
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

            for binx in range(1, matrix.GetNbinsX()+1):
                for biny in range(1, matrix.GetNbinsY()+1):
                    if systematic == "pdf__up":
                        matrix.SetBinContent(binx, biny, matrix.GetBinContent(binx, biny) * (1 + hists_pdf_up[sample.name].GetBinContent(biny)))
                    elif systematic == "pdf__down":
                        matrix.SetBinContent(binx, biny, matrix.GetBinContent(binx, biny) * (1 - hists_pdf_down[sample.name].GetBinContent(biny)))


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
