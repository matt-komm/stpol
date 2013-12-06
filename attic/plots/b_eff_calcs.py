import ROOT
import project_histos
from project_histos import Cuts
import logging
import numpy
import pdb

def getBTaggingEff(sample, flavour, cut):
    if flavour not in ["b", "c", "l"]:
        raise ValueError("Flavour must be b, c or l")

    colA = sample.getColumn("true_%s_tagged_count" % flavour, cut)
    colB = sample.getColumn("true_%s_count" % flavour, cut)
    print min(colA), min(colB), max(colA), max(colB)

    pdb.set_trace()
    N_tagged = numpy.sum(colA)
    N = numpy.sum(colB)

    print N_tagged, N
    return N_tagged/N

if __name__=="__main__":

    ##sample_dir = "/scratch/joosep/out_step3_05_07_14_19/iso/mc/"
    sample_dir = "out_step3_May8/"
    samples = []
    #samples.append(project_histos.Sample.fromFile(sample_dir + "TTJets_FullLept.root"))
    samples.append(project_histos.Sample.fromFile(sample_dir + "TTJets_MassiveBinDECAY.root"))
    #samples.append(project_histos.Sample.fromFile(sample_dir + "TTJets_SemiLept.root"))
    #samples.append(project_histos.Sample.fromFile(sample_dir + "T_t.root"))
    #samples.append(project_histos.Sample.fromFile(sample_dir + "WJets_inclusive.root"))
    logging.info("Doing b-tagging efficiency calculations")
    cuts = [Cuts.mu * Cuts.n_jets(2) * Cuts.eta_lj * Cuts.mt_mu * Cuts.top_mass_sig]
#    cuts = [Cuts.mu]
#    cuts.append("n_jets==2 && !(top_mass>130 && top_mass<220) && mt_mu>50")
#    cuts.append("n_jets==3 && !(top_mass>130 && top_mass<220) && mt_mu>50")
    for cut in cuts:
        for sample in samples:
            for flavour in ["b", "c", "l"]:
                entries = sample.getEntries(str(cut))
                total = sample.getTotalEventCount()
                eff = getBTaggingEff(sample, flavour, str(cut))
                print "%s | %s | %.3E/%.3E | %.6f" % (sample, flavour, entries, total, eff)
