import subprocess
import glob
import os
from SingleTopPolarization.Analysis.sample_types import *
from plots.common.sample import *

if __name__=="__main__":

    basedir = os.environ["STPOL_DIR"]
    cmd = "%s/bin/WJets_reweighting" % basedir

    for root, path, files in os.walk(basedir + "/step3_latest"):
        for fi in files:
            fi = root + "/" + fi
            if not fi.endswith(".root"):
                continue
            args = []
            sn = get_sample_name(fi)

            args += ["--isWJets=%s" % str(is_wjets(sn))]
            print args
            subprocess.check_call([cmd, "--infile=%s" % fi] + args)
