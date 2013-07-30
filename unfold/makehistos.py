import os
import logging
import ROOT
from plots.common.sample import Sample
import numpy
from plots.common.utils import mkdir_p

binning_gen = numpy.array([-1, -0.4674, -0.2558, -0.1028, 0.0, 0.116, 0.2126, 0.2956, 0.379, 0.4568, 0.5302, 0.6038, 0.6822, 0.7694, 1], dtype="d")
binning_reco = numpy.array([-1, -0.2778, 0.0, 0.176, 0.3414, 0.4964, 0.6572, 1], dtype="d")

def makehisto(sample, varname, cut, weight, binning, lumi=None, **kwargs):

    process = kwargs.get("process", sample.name)
    ofile = kwargs.get("ofile", sample.name)

    mkdir_p("/".join(ofile.split("/")[:-1]))
    fo = ROOT.TFile(ofile, "RECREATE")

    if not sample.isMC:
        logging.debug("Not weighting sample %s" % sample.name)
        weight = "1.0"

    hist = sample.drawHistogram(varname, cut, binning=[len(binning)-1, binning], weight=weight)

    if sample.isMC and lumi:
        hist.Scale(sample.lumiScaleFactor(lumi))
    hname = varname + "__" + process

    fo.cd()
    hist.SetName(hname)
    hist.SetTitle(hname)
    hist.SetDirectory(fo)
    hist.Write()
    logging.info("Writing histogram %s to file %s" % (hist.GetName(), fo.GetPath()))
    fo.Write()
    fo.Close()

    return hist

def rebinned(var_reco, binning_reco, var_gen, binning_gen, cut, weight, lumi, sample_T_t, sample_Tbar_t, ofname):

    mkdir_p("/".join(ofname.split("/")[:-1]))
    fo = ROOT.TFile(ofname, "RECREATE")
    fo.cd()
    hgen = ROOT.TH1F(var_gen + "_rebin", var_gen + " rebinned", len(binning_gen)-1, binning_gen)
    hreco = ROOT.TH1F(var_reco + "_rebin", var_reco + " rebinned", len(binning_reco)-1, binning_reco)
    hgenreco = ROOT.TH2F("matrix", "matrix", len(binning_gen)-1, binning_gen, len(binning_reco)-1, binning_reco)
    for h in [hgen, hreco, hgenreco]:
        h.Sumw2()

    sample_T_t.tree.Draw("%s >> %s"%(var_gen, hgen.GetName()), "%s*%s*(%s)" % (sample_T_t.lumiScaleFactor(lumi), weight, cut))
    sample_Tbar_t.tree.Draw("%s >> +%s"%(var_gen, hgen.GetName()), "%s*%s*(%s)" % (sample_Tbar_t.lumiScaleFactor(lumi), weight, cut))
    sample_T_t.tree.Draw("%s >> %s"%(var_reco, hreco.GetName()), "%s*%s*(%s)" % (sample_T_t.lumiScaleFactor(lumi), weight, cut))
    sample_Tbar_t.tree.Draw("%s >> +%s"%(var_reco, hreco.GetName()), "%s*%s*(%s)" % (sample_Tbar_t.lumiScaleFactor(lumi), weight, cut))
    sample_T_t.tree.Draw("%s:%s >> %s"%(var_gen, var_reco, hgenreco.GetName()), "%s*%s*(%s)" % (sample_T_t.lumiScaleFactor(lumi), weight, cut))
    sample_Tbar_t.tree.Draw("%s:%s >> +%s"%(var_gen, var_reco, hgenreco.GetName()), "%s*%s*(%s)" % (sample_Tbar_t.lumiScaleFactor(lumi), weight, cut))

    for h in [hgen, hreco, hgenreco]:
        h.Write()
    fo.Close()

def efficiency(fn_presel, fn_postsel, ofname):
    logging.info("Calculating selection efficiency")
    fi_presel = ROOT.TFile(fn_presel)
    hgen_presel = fi_presel.Get(var_gen + "_rebin")
    fi_postsel = ROOT.TFile(fn_postsel)
    hgen_postsel = fi_postsel.Get(var_gen + "_rebin")

    mkdir_p("histos")
    fi = ROOT.TFile(ofname, "RECREATE")
    fi.cd()
    
    heff = hgen_postsel.Clone("efficiency")
    heff.SetTitle("Selection efficiency")
    heff.Divide(hgen_presel)
    heff.Write()
    fi.Close()
    fi_presel.Close()
    fi_postsel.Close()

if __name__=="__main__":
    logging.basicConfig(level=logging.INFO)

#Load the data
    #These paths should stay relatively fixed and constant across analysts
    basedir = os.environ["STPOL_DIR"] + "/step3_latest/mu/"
    datadir_iso = basedir+"/iso/nominal/"
    datadir_aiso = basedir+"/antiiso/nominal/"
    samples = {}
    samples = Sample.fromDirectory(datadir_iso, out_type="dict")
    samples["SingleMu_aiso"] = Sample.fromFile(datadir_aiso + "SingleMu.root")
    logging.debug("Loaded samples %s" % str(samples))

#Define the plotting variables
    var_reco = "cos_theta"
    var_gen = "true_cos_theta"
    cut = "n_jets==2"
    weight = "1.0"
    lumi=19700 #FIXME

#1. Draw the rebinned signal hists
    logging.info("Projecting the rebinned histograms for signal before selection")
    fn_presel = "histos/rebinned_presel.root"
    rebinned(var_reco, binning_reco, var_gen, binning_gen, "1.0", weight, lumi, samples["T_t_ToLeptons"], samples["Tbar_t_ToLeptons"], fn_presel)

    logging.info("Projecting the rebinned histograms for signal after selection")
    fn_postsel = "histos/rebinned.root"
    rebinned(var_reco, binning_reco, var_gen, binning_gen, cut, weight, lumi, samples["T_t_ToLeptons"], samples["Tbar_t_ToLeptons"], fn_postsel)

#2. Draw the input hists (sig+bkg)
    logging.info("Projecting the input histograms for signal, background and data")
    args = (var_reco, cut, weight, binning_reco, lumi)
    hdir = "histos/input/"
    #TODO: add background samples
    #tchan (T_t, Tbar_t)
    #top (T*_s,tW, TTbar)
    #wzjets (W*Jets_exclusive, *Jets)
    #qcd (data anti-iso)
    #DATA (data iso)
    
    makehisto(samples["T_t_ToLeptons"], *args, process="tchan", ofile=hdir+"tchan_t.root")
    makehisto(samples["Tbar_t_ToLeptons"], *args, process="tchan", ofile=hdir+"tchan_tbar.root")
    makehisto(samples["SingleMu"], *args, process="DATA", ofile=hdir+"DATA_SingleMu.root")
    makehisto(samples["SingleMu_aiso"], *args, process="qcd", ofile=hdir+"qcd.root")

#3. TODO: Calculate the selection efficiency (efficiency.C) => histos/efficiency.root
#The selection efficiency is hgen_rebin/hgen_presel_rebin
    efficiency(fn_presel, fn_postsel, "histos/efficiency.root")

#4. TODO: Sum the input histograms from step 2 (hadd) => histos/data.root

#5. TODO: Create the pseudo-data histograms (pseudodata.C) => histos/pseudo_data.root

#6. Unfold

#pseudo_data.root -> var_rec histogram
