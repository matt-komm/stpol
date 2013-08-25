import os
from plots.common.sample import Sample
from plots.common.utils import mkdir_p
from plots.common.cross_sections import lumi_iso, lumi_antiiso
import logging
import subprocess
import shutil
from load_samples import load_samples, load_nominal_mc_samples, create_histogram_for_fit, get_qcd_scale_factor
from plots.common.cuts import *
from rootpy.io import File, root_open
import math
import sys

def generate_out_dir(channel, var, mva_cut="-1", coupling="powheg", asymmetry=None, mtmetcut=None, extra=None):
    dirname = channel + "__" +var
    if float(mva_cut) > -1:    
        mva = "__mva_"+str(mva_cut)
        mva = mva.replace(".","_")
        dirname += mva
    if coupling != "powheg":
        dirname += "__" + coupling
    if asymmetry is not None:
        dirname += "__asymm_" + str(asymmetry)
    if mtmetcut is not None:
        dirname += "__mtmet_" + str(mtmetcut)
    if extra is not None:
        dirname += "__" + str(extra)
    return dirname



def make_systematics_histos(var, cuts, cuts_antiiso, systematics, outdir="/".join([os.environ["STPOL_DIR"], "lqetafit", "histos"]), indir="/".join([os.environ["STPOL_DIR"], "step3_latest"]), channel="mu", coupling="powheg", binning=None, plot_range=None, asymmetry=None, mtmetcut=None):
    #logging.basicConfig(level="INFO")
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)
    logging.debug('This message should appear on the console')
    try:
        shutil.rmtree(outdir)
    except OSError:
        logging.warning("Couldn't remove directory %s" % outdir)
    
    mkdir_p(outdir)
    for main_syst, sub_systs in systematics.items():
        systname = main_syst
        if systname == "partial":
            for sub_syst, updown in sub_systs.items():
                for (k, v) in updown.items():
                    ss = {}
                    ss[k] = v
                    make_histos_for_syst(var, sub_syst, ss, cuts, cuts_antiiso, outdir, indir, channel, coupling=coupling, binning=binning, plot_range=plot_range, asymmetry=asymmetry, mtmetcut=mtmetcut)
        elif systname != "nominal":
            for sub_syst, path in sub_systs.items():
                ss = {}
                ss[sub_syst] = path
                make_histos_for_syst(var, systname, ss, cuts, cuts_antiiso, outdir, indir, channel, coupling=coupling, binning=binning, plot_range=plot_range, asymmetry=asymmetry, mtmetcut=mtmetcut)
        else:
            make_histos_for_syst(var, systname, sub_systs, cuts, cuts_antiiso, outdir, indir, channel, coupling=coupling, binning=binning, plot_range=plot_range, asymmetry=asymmetry, mtmetcut=mtmetcut)
    
    #hadd_histos(outdir)

    #Order is important here
    add_histos_vary_components(outdir, var, channel, "mva" in cuts, mtmetcut)
    add_histos(outdir, var, channel, "mva" in cuts, mtmetcut)
    
def make_histos_for_syst(var, main_syst, sub_systs, cuts, cuts_antiiso, outdir, indir, channel, coupling, binning=None, plot_range=None, asymmetry=None, mtmetcut=None):
        if sub_systs.keys()[0] in ["up", "down"] and main_syst in ["Res", "En", "UnclusteredEn"]:
            ss_type=sub_systs[sub_systs.keys()[0]]
        elif sub_systs.keys()[0] in ["up", "down"]:
            ss_type=main_syst + "__" + sub_systs.keys()[0]
        else:
            ss_type=main_syst
        (samples, sampnames) = load_samples(ss_type, channel, indir, coupling)
        
        outhists = {}
        for sn, samps in sampnames:
            hists = []
            for sampn in samps:
                for sys, sys_types in sub_systs.items():
                    if sys == "nominal":
                        weight_str = sys_types
                        hname = "%s__%s" % (var, sn)
                        write_histogram(var, hname, weight_str, samples, sn, sampn, cuts, cuts_antiiso, outdir, channel, coupling, binning=binning, plot_range=plot_range, asymmetry=asymmetry, mtmetcut=mtmetcut)
                    elif sn in ["DATA"] and sys != "nominal":
                        #No systematics if data
                        continue
                    elif main_syst in ["Res", "En", "UnclusteredEn"]:
                        if coupling != "powheg": #these systs not available for comphep (currently?)
                            continue
                        hname = "%s__%s__%s__%s" % (var, sn, main_syst, sys)
                        write_histogram(var, hname, Weights.total_weight(channel), samples, sn, sampn, cuts, cuts_antiiso, outdir, channel, coupling, binning=binning, plot_range=plot_range, asymmetry=asymmetry, mtmetcut=mtmetcut)
                    elif main_syst=="nominal":
                        for st_name, st in sys_types.items():
                            weight_str = st
                            hname = "%s__%s__%s__%s" % (var, sn, sys, st_name)
                            write_histogram(var, hname, weight_str, samples, sn, sampn, cuts, cuts_antiiso, outdir, channel, coupling, binning=binning, plot_range=plot_range, asymmetry=asymmetry, mtmetcut=mtmetcut)
                    else: #main_syst=="partial"
                        hname = "%s__%s__%s" % (var, sn, ss_type)
                        write_histogram(var, hname, Weights.total_weight(channel), samples, sn, sampn, cuts, cuts_antiiso, outdir, channel,  coupling, binning=binning, plot_range=plot_range, asymmetry=asymmetry, mtmetcut=mtmetcut)


def write_histogram(var, hname, weight, samples, sn, sampn, cuts, cuts_antiiso, outdir, channel, coupling, binning=None, plot_range=None, asymmetry=None, mtmetcut=None):
    weight_str = weight
    samp = samples[sampn]
    outfile = File(outdir + "/%s_%s.root" % (sampn,hname), "RECREATE")
    if sn=="DATA":
        weight_str = "1"
    if var == "eta_lj":
        var = "abs("+var+")"
    qcd_extra = None
    
    #This is a really ugly way of adding the QCD shape variation, but works. Restructure the whole thing in the future
    if "iso__down" in hname:
        if var == "abs(eta_lj)":
            cuts_antiiso = str(Cuts.eta_fit_antiiso_down(channel))
            qcd_extra = str(Cuts.eta_fit_antiiso(channel)) #hack for now
        else:
            for x in str(cuts_antiiso).split("&&"):
                if "mva" in x:
                    cut = x
                else:
                    cut = "1"
            cut = cut.replace("(","").replace(")","")
            cuts_antiiso = str(Cuts.mva_antiiso_down(channel, mva_var=var)) + " && ("+cut+")"
            qcd_extra = str(Cuts.mva_antiiso(channel, mva_var=var)) + " && ("+cut+")" #hack for now
    elif "iso__up" in hname:
        if var == "abs(eta_lj)":
            cuts_antiiso = str(Cuts.eta_fit_antiiso_up(channel))
            qcd_extra = str(Cuts.eta_fit_antiiso(channel)) #hack for now
        else:
            for x in str(cuts_antiiso).split("&&"):
                if "mva" in x:
                    cut = x
                else:
                    cut = "1"
            cut = cut.replace("(","").replace(")","")
            cuts_antiiso = str(Cuts.mva_antiiso_up(channel, mva_var=var)) + " && ("+cut+")"
            qcd_extra = str(Cuts.mva_antiiso(channel, mva_var=var)) + " && ("+cut+")" #hack for now
    hist = create_histogram_for_fit(sn, samp, weight_str, cuts, cuts_antiiso, channel, coupling, var, binning=binning, plot_range=plot_range, asymmetry=asymmetry, qcd_extra=qcd_extra, mtmetcut=mtmetcut)
    outfile.cd() #Must cd after histogram creation

    #Write histogram to file
    logging.info("Writing histogram %s to file %s" % (hist.GetName(), outfile.GetPath()))
    logging.info("%i entries, %.2f events" % (hist.GetEntries(), hist.Integral()))
    (a,b) = hist.GetName().split("_")[0], hist.GetName().split("_")[1]
    print "YIELD", a+"_"+b, hist.Integral()
    hist.SetName(hname)
    hist.SetDirectory(outfile)
    outfile.Write()
    outfile.Close()
    samples = None
    #return (hist.GetName(), hist.Integral())

def hadd_histos(outdir):
    #Add the relevant histograms together
    outfile = generate_file_name(False)
    subprocess.check_call(("hadd -f {0}/"+outfile+" {0}/*.root").format(outdir), shell=True)

def add_histos(outdir, var, channel, mva, mtmetcut):
    from os import listdir
    from os.path import isfile, join
    
    
    onlyfiles = [ f for f in listdir(outdir) if isfile(join(outdir,f)) ]
    hists = dict()
    hists_data = []
    hists_qcd = []
    for fname in onlyfiles:
        f = root_open(outdir+"/"+fname)
        for root, dirs, items in f.walk():
            for name in items:
                h = f.Get(join(root, name))
                h.SetDirectory(0) 
                """if fname.endswith("DATA.root"):
                    hists_data.append(h)
                    continue
                elif fname.startswith("Single"):
                    hists_qcd.append(h)
                    continue"""
                if not name in hists:
                    hists[name] = []
                #if h.GetEntries()>0:
                #    print fname, "factor", h.Integral()/math.sqrt(h.GetEntries())
                #for bin in range(1, h.GetNbinsX()+1):
                #    print bin, h.GetBinContent(bin), h.GetBinError(bin)
                hists[name].append(h)
                #hists[name].SetTitle(name)
        f.Close()
    hists_qcdvar = add_qcd_yield_unc(outdir, var, channel, mva, mtmetcut)
    print "QCDVAR:", hists_qcdvar
    hists.update(hists_qcdvar)

    """hist_data = hists_data[0]
    for i in range(1, len(hists_data)):
        hist_data.Add(hists_data[i])
    print "hists qcd", hists_qcd
    hist_qcd = hists_qcd[0]
    print "data", "factor", hist_data.Integral()/math.sqrt(hist_data.GetEntries())
    for i in range(1, len(hists_qcd)):
        print "add", i
        hist_qcd.Add(hists_qcd[i])
    print "QCD", "factor", hist_qcd.Integral()/math.sqrt(hist_qcd.GetEntries())

    for bin in range(1, hist_data.GetNbinsX()+1):
        hist_data.SetBinError(bin, math.sqrt(hist_data.GetBinContent(bin)))
        hist_qcd.SetBinError(bin, math.sqrt(hist_qcd.GetBinContent(bin)))

        print bin, hist_qcd.GetBinContent(bin), hist_qcd.GetBinError(bin)
    hist_qcd.Scale(get_qcd_scale_factor(var, channel, mva, mtmetcut))
    for bin in range(1, hist_data.GetNbinsX()+1):
        print bin, hist_qcd.GetBinContent(bin), hist_qcd.GetBinError(bin)
    hists[hist_data.GetName()] = [hist_data]
    print hists
    print hist_qcd.GetName()
    if hist_qcd.GetName() not in hists:
        hists[hist_qcd.GetName()] = []
    hists[hist_qcd.GetName()].append(hist_qcd)
    print "QCD hists", hists[hist_qcd.GetName()]"""
    outfile = File(outdir+"/"+generate_file_name(False), "recreate")

    write_histos_to_file(hists, outdir)

def write_histos_to_file(hists, outdir, syst=""):
    filename = outdir+"/"+generate_file_name(False, syst)
    if len(syst)>0:
        filename = filename.replace("/lqeta","")
    #filename += ".root"
    outfile = File(filename, "recreate")
    print "writing to file", filename
    for category in hists:
        factor = 1.0    
        total_hist=hists[category][0].Clone()
        total_hist.Reset("ICE")
        #total_hist.Sumw2()
        total_hist.SetNameTitle(category,category)
        outfile.cd()
        #print category
        for bin in range(1, total_hist.GetNbinsX()+1):
            zero_error = 0.
            zero_integral = 0.
            nonzero_error = 0.
            bin_sum = 0.
            max_zero_error = 0.
            for hist in hists[category]:
                #print "hist", hist.GetBinContent(bin), hist.GetBinError(bin)**2
                if hist.GetEntries()>0:
                    #factor = hist.Integral()/(math.sqrt(hist.GetEntries()) * total_hist.GetNbinsX()) 
                    #print "fact", factor,hist.Integral(), hist.GetEntries()
                    min_nonzero_error = sys.float_info.max
                    for bin1 in range(1, hist.GetNbinsX()+1):
                        if hist.GetBinContent(bin1) > 0 and hist.GetBinError(bin1) < min_nonzero_error:
                            min_nonzero_error = hist.GetBinError(bin1)
                    #print "error", min_nonzero_error
                else:
                    min_nonzero_error = 0.
                if hist.GetBinContent(bin) < 0.00001:
                    #zero_error += factor**2 * hist.Integral()
                    zero_error += min_nonzero_error**2
                    zero_integral += hist.Integral()
                else:
                    bin_sum += hist.GetBinContent(bin)
                    nonzero_error += hist.GetBinError(bin)**2
                #print "...hist", hist.GetBinContent(bin), hist.GetBinError(bin)**2
            total_hist.SetBinContent(bin, bin_sum)
            if zero_integral > 0:
                #total_error = math.sqrt(nonzero_error + zero_error / zero_integral)
                total_error = math.sqrt(nonzero_error + zero_error)
            else:
                total_error = math.sqrt(nonzero_error)
            total_hist.SetBinError(bin, total_error)
            #print category, "bin", bin, "content", bin_sum, "error", total_error
            #print category, "bin", bin, "weight", total_error**2/bin_sum
        total_hist.Write()
    """for category in hists:       #Imitate hadd
        #factor = 1.0    
        total_hist=hists[category][0].Clone()
        total_hist.Reset("ICE")
        print "cat", category
        total_hist.SetNameTitle(category,category)
        total_hist.Sumw2()
        outfile.cd()
        for hist in hists[category]:
            print "hist", hist, hist.GetName()
            factor = 1.0
            if hist.GetEntries()>0:
                factor = hist.Integral()/hist.GetEntries()

            for bin in range(1, total_hist.GetNbinsX()+1):
                if hist.GetBinError(bin) < factor:
                    hist.SetBinError(bin, factor)
                #total_hist.SetBinContent(bin, total_hist.GetBinContent(bin) + hist.GetBinContent(bin))
                #total_hist.SetBinError(bin, total_hist.GetBinError(bin) + hist.GetBinError(bin))
            total_hist.Add(hist)
        total_hist.Write()"""
    outfile.Write()
    outfile.Close()


def add_qcd_yield_unc(outdir, var, channel, mva, mtmetcut):
    from os import listdir
    from os.path import isfile, join
    
    
    onlyfiles = [ f for f in listdir(outdir) if isfile(join(outdir,f)) ]
    hists = dict()
    integrals = dict()
    
    for fname in onlyfiles:
        print "filename", fname
        f = File(outdir+"/"+fname)
        for root, dirs, items in f.walk():
            for name in items:
                h = f.Get(join(root, name))
                h.SetDirectory(0)
                """if fname.endswith("DATA.root"):
                    hists_data.append(h)
                    continue
                elif fname.startswith("Single"):
                    hists_qcd.append(h)
                    continue"""
                if not name in hists:
                    hists[name] = []
                    integrals[name] = 0.
                hists[name].append((fname, h))
                integrals[name] += h.Integral()
                #hists[name].SetTitle(name)
        f.Close()
    variations = [("other", "QCD__down"), ("other", "QCD__up")]
    hists_var = {}
    for (var_component, var) in variations:
        print var
        for name in hists:
            if name.endswith(var_component):            
                new_integral = 0
                integral = integrals[name]
                integral_orig = integral
                print "start", integral, integral_orig
                if not name+"__"+var in hists_var:
                    hists_var[name+"__"+var] = []
                for (fname,hist_orig) in hists[name]:
                    if check_starts(var, fname):
                        hist = hist_orig.Clone()
                        integral_orig = integral_orig - hist.Integral()
                        if var.endswith("down"):
                            scale = 0.5
                            if var.startswith("QCD"):
                                scale = 0.0001  #to not have all bins completely empty
                        elif var.endswith("up"):
                            scale = 1.5
                            if var.startswith("QCD"):
                                scale = 2.0
                        hist.Scale(scale)
                        integral = integral - hist.Integral()
                        print fname, hist.Integral()
                        print "sub", integral, integral_orig                
                        new_integral += hist.Integral()
                        hist.SetNameTitle(hist.GetName()+"__"+var, hist.GetTitle()+"__"+var)
                        hists_var[name+"__"+var].append(hist)
                for (fname, hist_orig) in hists[name]:
                    if not check_starts(var, fname):
                        hist = hist_orig.Clone()
                        print "SF", integral/integral_orig
                        hist.Scale(integral/integral_orig)
                        print fname, hist.Integral()
                        new_integral += hist.Integral()
                        hist.SetNameTitle(hist.GetName()+"__"+var, hist.GetTitle()+"__"+var)
                        hists_var[name+"__"+var].append(hist)
                #for (fname,hist) in hists[name]:
                    
                print "new int", new_integral
                #for (fname,hist) in hists[name]:
                #    print fname, hist.Integral()
            elif not name.endswith("DATA"):
                if not name+"__"+var in hists_var:
                    hists_var[name+"__"+var] = []
                for (fname, hist_orig) in hists[name]:
                    hist = hist_orig.Clone()
                    hist.SetNameTitle(hist.GetName()+"__"+var, hist.GetTitle()+"__"+var)
                    hists_var[name+"__"+var].append(hist)
    return hists_var
    #write_histos_to_file(hists_var, outdir.replace("input",""), var)


def add_histos_vary_components(outdir, var, channel, mva, mtmetcut):
    from os import listdir
    from os.path import isfile, join
    
    
    onlyfiles = [ f for f in listdir(outdir) if isfile(join(outdir,f)) ]
    hists = dict()
    integrals = dict()
    
    hists_data = []
    hists_qcd = []
    for fname in onlyfiles:
        print "filename", fname
        f = File(outdir+"/"+fname)
        for root, dirs, items in f.walk():
            for name in items:
                h = f.Get(join(root, name))
                h.SetDirectory(0)
                """if fname.endswith("DATA.root"):
                    hists_data.append(h)
                    continue
                elif fname.startswith("Single"):
                    hists_qcd.append(h)
                    continue"""
                if not name in hists:
                    hists[name] = []
                    integrals[name] = 0.
                #if h.GetEntries()>0:
                #    print fname, "factor", h.Integral()/math.sqrt(h.GetEntries())
                #for bin in range(1, h.GetNbinsX()+1):
                #    print bin, h.GetBinContent(bin), h.GetBinError(bin)
                hists[name].append((fname, h))
                integrals[name] += h.Integral()
                #hists[name].SetTitle(name)
        f.Close()
    for name in hists:
        print name, integrals[name]
        #print hists[name]
        for (fname,hist) in hists[name]:
            print fname, hist.Integral()

    variations = [("other", "QCD_down"), ("other", "QCD_up")
        , ("other", "s_chan_down"), ("other", "s_chan_up")
        , ("other", "tW_chan_up"), ("other", "tW_chan_down")
        , ("wzjets", "Dibosons_up"), ("wzjets", "Dibosons_down")
        , ("wzjets", "DYJets_up"), ("wzjets", "DYJets_down")
        ]
    for (var_component, var) in variations:
        hists_var = {}
        print var
        for name in hists:
            if name.endswith(var_component):            
                new_integral = 0
                integral = integrals[name]
                integral_orig = integral
                print "start", integral, integral_orig
                if not name in hists_var:
                    hists_var[name] = []
                for (fname,hist_orig) in hists[name]:
                    if check_starts(var, fname):
                        hist = hist_orig.Clone()
                        integral_orig = integral_orig - hist.Integral()
                        if var.endswith("down"):
                            scale = 0.5
                            if var.startswith("QCD"):
                                scale = 0.0001  #to not have all bins completely empty
                        elif var.endswith("up"):
                            scale = 1.5
                            if var.startswith("QCD"):
                                scale = 2.0
                        hist.Scale(scale)
                        integral = integral - hist.Integral()
                        print fname, hist.Integral()
                        print "sub", integral, integral_orig                
                        new_integral += hist.Integral()
                        hists_var[name].append(hist)
                for (fname, hist_orig) in hists[name]:
                    if not check_starts(var, fname):
                        hist = hist_orig.Clone()
                        print "SF", integral/integral_orig
                        hist.Scale(integral/integral_orig)
                        print fname, hist.Integral()
                        new_integral += hist.Integral()
                        hists_var[name].append(hist)
                #for (fname,hist) in hists[name]:
                    
                print "new int", new_integral
                #for (fname,hist) in hists[name]:
                #    print fname, hist.Integral()
            else:
                if not name in hists_var:
                    hists_var[name] = []
                for (fname, hist_orig) in hists[name]:
                    hists_var[name].append(hist_orig)
        write_histos_to_file(hists_var, outdir.replace("input",""), var)


def check_starts(var, fname):
    if var.startswith("DYJets") and fname.startswith("DYJets"):
        return True
    if var.startswith("Dibosons") and (fname.startswith("WW") or fname.startswith("WZ") or fname.startswith("ZZ")):
        return True
    if var.startswith("QCD") and fname.startswith("Single"):
        return True
    if var.startswith("s_chan") and (fname.startswith("T_s") or fname.startswith("Tbar_s")):
        return True
    if var.startswith("tW_chan") and (fname.startswith("T_tW") or fname.startswith("Tbar_tW")):
        return True
    return False

def generate_file_name(sherpa, syst=""):
    name = "lqeta"
    if len(syst)>0:
        name+="_"+syst
    name += ".root"
    return name

def generate_systematics(channel, coupling):
    systematics = {}
    systematics["nominal"]={}
    systematics["nominal"]["nominal"] = str(Weights.total_weight(channel))
    systs_infile = ["pileup", "top_pt", "btaggingBC", "btaggingL", "leptonID", "leptonTrigger", "wjets_flat", "wjets_shape"]
    if channel == "mu":
        systs_infile.append("leptonIso")
    for sys in systs_infile:
        systematics["nominal"][sys] = {}
    if coupling == "powheg":
        systs_infile_file=["En", "Res", "UnclusteredEn"]
        for sys in systs_infile_file:
           systematics[sys] = {}
    
    #TODO: Add PDF-s
    systematics["nominal"]["pileup"]["up"] = str(Weights.pu("up")*Weights.top_pt[0]*Weights.b_weight()*Weights.lepton_weight(channel) * Weights.wjets_madgraph_shape_weight() * Weights.wjets_madgraph_flat_weight())
    systematics["nominal"]["pileup"]["down"] = str(Weights.pu("down")*Weights.top_pt[0]*Weights.b_weight()*Weights.lepton_weight(channel) * Weights.wjets_madgraph_shape_weight() * Weights.wjets_madgraph_flat_weight())
    systematics["nominal"]["top_pt"]["up"] = str(Weights.pu()*Weights.top_pt[1]*Weights.b_weight()*Weights.lepton_weight(channel) * Weights.wjets_madgraph_shape_weight() * Weights.wjets_madgraph_flat_weight())
    systematics["nominal"]["top_pt"]["down"] = str(Weights.pu()*Weights.top_pt[2]*Weights.b_weight()*Weights.lepton_weight(channel) * Weights.wjets_madgraph_shape_weight() * Weights.wjets_madgraph_flat_weight())
    systematics["nominal"]["btaggingBC"]["up"] = str(Weights.pu()*Weights.top_pt[0]*Weights.b_weight("BC", "up")*Weights.lepton_weight(channel) * Weights.wjets_madgraph_shape_weight() * Weights.wjets_madgraph_flat_weight())
    systematics["nominal"]["btaggingBC"]["down"] = str(Weights.pu()*Weights.top_pt[0]*Weights.b_weight("BC", "down")*Weights.lepton_weight(channel) * Weights.wjets_madgraph_shape_weight() * Weights.wjets_madgraph_flat_weight())
    systematics["nominal"]["btaggingL"]["up"] = str(Weights.pu()*Weights.top_pt[0]*Weights.b_weight("L", "up")*Weights.lepton_weight(channel) * Weights.wjets_madgraph_shape_weight() * Weights.wjets_madgraph_flat_weight())
    systematics["nominal"]["btaggingL"]["down"] = str(Weights.pu()*Weights.top_pt[0]*Weights.b_weight("L", "down")*Weights.lepton_weight(channel) * Weights.wjets_madgraph_shape_weight() * Weights.wjets_madgraph_flat_weight())
    systematics["nominal"]["wjets_flat"]["up"] = str(Weights.pu()*Weights.top_pt[0]*Weights.b_weight()*Weights.lepton_weight(channel) * Weights.wjets_madgraph_shape_weight() * Weights.wjets_madgraph_flat_weight("wjets_up"))
    systematics["nominal"]["wjets_flat"]["down"] = str(Weights.pu()*Weights.top_pt[0]*Weights.b_weight()*Weights.lepton_weight(channel) * Weights.wjets_madgraph_shape_weight() * Weights.wjets_madgraph_flat_weight("wjets_down"))
    systematics["nominal"]["wjets_shape"]["up"] = str(Weights.pu()*Weights.top_pt[0]*Weights.b_weight()*Weights.lepton_weight(channel) * Weights.wjets_madgraph_shape_weight("wjets_up") * Weights.wjets_madgraph_flat_weight())
    systematics["nominal"]["wjets_shape"]["down"] = str(Weights.pu()*Weights.top_pt[0]*Weights.b_weight()*Weights.lepton_weight(channel) * Weights.wjets_madgraph_shape_weight("wjets_down") * Weights.wjets_madgraph_flat_weight())
    systematics["nominal"]["leptonID"]["up"] = str(Weights.pu()*Weights.top_pt[0]*Weights.b_weight()*Weights.lepton_weight(channel, "ID", "up") * Weights.wjets_madgraph_shape_weight() * Weights.wjets_madgraph_flat_weight())
    systematics["nominal"]["leptonID"]["down"] =  str(Weights.pu()*Weights.top_pt[0]*Weights.b_weight()*Weights.lepton_weight(channel, "ID", "down") * Weights.wjets_madgraph_shape_weight() * Weights.wjets_madgraph_flat_weight())
    if channel == "mu":
        systematics["nominal"]["leptonIso"]["up"] = str(Weights.pu()*Weights.top_pt[0]*Weights.b_weight()*Weights.lepton_weight(channel, "Iso", "up") * Weights.wjets_madgraph_shape_weight() * Weights.wjets_madgraph_flat_weight())
        systematics["nominal"]["leptonIso"]["down"] = str(Weights.pu()*Weights.top_pt[0]*Weights.b_weight()*Weights.lepton_weight(channel, "Iso", "down") * Weights.wjets_madgraph_shape_weight() * Weights.wjets_madgraph_flat_weight())
    systematics["nominal"]["leptonTrigger"]["up"] = str(Weights.pu()*Weights.top_pt[0]*Weights.b_weight()*Weights.lepton_weight(channel, "Trigger", "up") * Weights.wjets_madgraph_shape_weight() * Weights.wjets_madgraph_flat_weight())
    systematics["nominal"]["leptonTrigger"]["down"] = str(Weights.pu()*Weights.top_pt[0]*Weights.b_weight()*Weights.lepton_weight(channel, "Trigger", "down") * Weights.wjets_madgraph_shape_weight() * Weights.wjets_madgraph_flat_weight())
    
    
    systematics["partial"] = {}
    systematics["partial"]["mass"] = {}
    systematics["partial"]["mass"]["down"] = {}
    systematics["partial"]["mass"]["up"] = {}
    systematics["partial"]["tchan_scale"] = {}
    systematics["partial"]["tchan_scale"]["down"] = {}
    systematics["partial"]["tchan_scale"]["up"] = {}
    systematics["partial"]["ttbar_scale"] = {}
    systematics["partial"]["ttbar_scale"]["down"] = {}
    systematics["partial"]["ttbar_scale"]["up"] = {}
    systematics["partial"]["ttbar_matching"] = {}
    systematics["partial"]["ttbar_matching"]["down"] = {}
    systematics["partial"]["ttbar_matching"]["up"] = {}
    #TODO: W+jets scale/matching not processed
    #systematics["partial"]["wjets_scale"] = {}
    #systematics["partial"]["wjets_scale"]["down"] = {}
    #systematics["partial"]["wjets_scale"]["up"] = {}
    systematics["partial"]["wjets_matching"] = {}
    #systematics["partial"]["wjets_matching"]["down"] = {}
    #systematics["partial"]["wjets_matching"]["up"] = {}
    systematics["partial"]["iso"] = {}
    systematics["partial"]["iso"]["down"] = {}
    systematics["partial"]["iso"]["up"] = {}
    
    if coupling == "powheg":
        systematics["Res"]["down"]="ResDown"
        systematics["Res"]["up"]="ResUp"
        systematics["En"]["down"]="EnDown"
        systematics["En"]["up"]="EnUp"
        systematics["UnclusteredEn"]["down"]="UnclusteredEnDown"
        systematics["UnclusteredEn"]["up"]="UnclusteredEnUp"
    return systematics
