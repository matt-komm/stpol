from plots.common.sample import Sample
from plots.common.cuts import Cuts
import sys

if __name__=="__main__":

    for fi in sys.argv[1:]:
        print fi
        samp = Sample.fromFile(fi)

        for lep in ["mu"]:
            print lep
            cut = None
            for cutname, _cut in [
                ("hlt", Cuts.hlt(lep)),
                ("lep", Cuts.single_lepton(lep)),
                ("2J", Cuts.n_jets(2)),
                ("1T", Cuts.n_tags(1)),
                ("MET/MtW", Cuts.metmt(lep)),
                ("rms", Cuts.rms_lj),
                ("Mtop", Cuts.top_mass_sig),
                ("etalj", Cuts.eta_lj)
                ]:
                if not cut:
                    cut = _cut
                else:
                    cut *= _cut
                hi = samp.drawHistogram("eta_lj", str(cut), plot_range=[50, -5, 5])
                hi.Scale(samp.lumiScaleFactor(20000))
                print cutname
                print hi.GetEntries(), hi.Integral()
            for cutname, _cut in [
                ("HLT", Cuts.hlt(lep)),
                ("lep", Cuts.single_lepton(lep)),
                ("2J", Cuts.n_jets(2)),
                ("1T", Cuts.n_tags(1)),
                ("MVA", Cuts.mva_wp(lep))
                ]:
                if not cut:
                    cut = _cut
                else:
                    cut *= _cut
                hi = samp.drawHistogram("eta_lj", str(cut), plot_range=[50, -5, 5])
                hi.Scale(samp.lumiScaleFactor(20000))
                print cutname
                print hi.GetEntries(), hi.Integral()
