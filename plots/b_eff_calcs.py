import ROOT
import project_histos
from project_histos import Cuts
import logging
import numpy

def getBTaggingEff(sample, flavour, cut):
    if flavour not in ["b", "c", "l"]:
        raise ValueError("Flavour must be b, c or l")

    N_tagged = numpy.sum(sample.getColumn("true_%s_tagged_count" % flavour, cut))
    N = numpy.sum(sample.getColumn("true_%s_count" % flavour, cut))
    print N_tagged,N
    return N_tagged/N

if __name__=="__main__":

    sample_dir = "/Users/joosep/Documents/stpol/data/out_step3_05_02_13_55/iso/mc/"
    samples = []
    samples.append(project_histos.Sample.fromFile(sample_dir + "TTJets_FullLept.root"))
    samples.append(project_histos.Sample.fromFile(sample_dir + "TTJets_MassiveBinDECAY.root"))
    samples.append(project_histos.Sample.fromFile(sample_dir + "TTJets_SemiLept.root"))
    samples.append(project_histos.Sample.fromFile(sample_dir + "T_t.root"))
    #samples.append(project_histos.Sample.fromFile(sample_dir + "WJets_inclusive.root"))
    logging.info("Doing b-tagging efficiency calculations")
    cuts = [Cuts.final]
#    cuts.append("n_jets==2 && !(top_mass>130 && top_mass<220) && mt_mu>50")
#    cuts.append("n_jets==3 && !(top_mass>130 && top_mass<220) && mt_mu>50")
    for cut in cuts:
        print cut
        for sample in samples:
            for flavour in ["b", "c", "l"]:
                entries = sample.getEntries(str(cut))
                total = sample.getTotalEventCount()
                eff = getBTaggingEff(sample, flavour, str(cut))
                print "%s | %s | %.3E/%.3E | %.3E" % (sample, flavour, entries, total, eff)
