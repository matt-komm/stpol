import ROOT
import os
from plots.common.sample import Sample
from plots.common.histogram import Histogram
from plots.common.utils import mkdir_p
import logging
import subprocess
import shutil

if __name__=="__main__":
    #Draw the histograms of eta_lj in the final selection sans the eta cut

    logging.basicConfig(level="INFO")
    datadir = "/".join((os.environ["STPOL_DIR"], "step3_latest", "mu", "iso", "nominal"))
    samples = Sample.fromDirectory(datadir, out_type="dict")

    samples["SingleMu_aiso"] = Sample.fromFile("/".join((os.environ["STPOL_DIR"], "step3_latest", "mu", "antiiso", "nominal", "SingleMu.root")))
    sampnames = (
        ("tchan", ["T_t_ToLeptons", "Tbar_t_ToLeptons"]),
        ("top", ["T_tW", "Tbar_tW", "T_s", "Tbar_s", "TTJets_FullLept", "TTJets_SemiLept"]),
        ("DATA", ["SingleMu"]),
        ("qcd", ["SingleMu_aiso"]),
    )
    
    lumi=19000 #FIXME
    cut_str = "n_jets==2 && n_tags==1 && top_mass>130 && top_mass<220"
    weight_str = "1.0"
    outdir = "histos"
    shutil.rmtree(outdir)
    mkdir_p(outdir)
    

    outhists = {}
    for sn, samps in sampnames:
        hists = []
        for sampn in samps:
            samp = samples[sampn]
            
            outfile = ROOT.TFile(outdir + "/%s.root" % sampn, "RECREATE")
            
            #Create histogram with sample metadata
            hist = samp.drawHistogram("eta_lj", cut_str, weight=weight_str, plot_range=[20, -5, 5])
            
            if sn not in ["DATA", "qcd"]:
                hist.Scale(samp.lumiScaleFactor(lumi))
            
            outfile.cd() #Must cd after histogram creation
            
            #Write histogram to file
            logging.info("Writing histogram %s to file %s" % (hist.hist.GetName(), outfile.GetPath()))
            
            hname = "%s__%s" % ("eta_lj", sn)
            hist.hist.SetName(hname)
            hist.update(file=outfile)
            hist.hist.Write()
            outfile.Write()
            
            outfile.Close()

    #Add the relevant histograms together
    subprocess.check_call("hadd -f {0}/lqeta.root {0}/*.root".format(outdir), shell=True)