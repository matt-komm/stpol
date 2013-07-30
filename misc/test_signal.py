from plots.common.sample import Sample
from plots.common.cuts import Cuts
import sys

if __name__=="__main__":
    if len(sys.argv)!=2:
        print "Usage: %s /path/to/mu/iso/nominal/T_t_ToLeptons.root" % sys.argv[1]
        sys.exit(0)

    s = Sample.fromFile(sys.argv[1])
    cut = Cuts.final(2,1)
    nentries = s.tree.Draw("cos_theta", str(cut))
    print "Nentries=",nentries
