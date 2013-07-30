from plots.common.sample import Sample
from plots.common.cuts import Cuts
import sys

if __name__=="__main__":

    for fi in sys.argv[1:]:
        print fi
        samp = Sample.fromFile(fi)

        for lep in ["mu", "ele"]:
            print lep
            cut = None
            for _cut in [
                Cuts.hlt(lep), Cuts.single_lepton(lep), Cuts.n_jets(2),
                Cuts.n_tags(1), Cuts.metmt(lep), Cuts.rms_lj, Cuts.top_mass_sig, Cuts.eta_lj
                ]:
                if not cut:
                    cut = _cut
                else:
                    cut *= _cut
                hi = samp.drawHistogram("eta_lj", str(cut), plot_range=[50, -5, 5])
                hi.Scale(samp.lumiScaleFactor(20000))
                print hi.GetEntries(), hi.Integral()