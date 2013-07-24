import subprocess
import glob
import os
from SingleTopPolarization.Analysis.sample_types import *
from plots.common.sample import *
from rootpy.extern.progressbar import *
import sys

widgets = [Percentage(), ' ', Bar(marker=RotatingMarker()), ' ', ETA()]

if __name__=="__main__":
    rootpy.log.basic_config_colorized()

    basedir = os.environ["STPOL_DIR"]
    cmd = "%s/bin/WJets_reweighting" % basedir
    sampdir = sys.argv[1]
    filedir = "/".join([basedir, sampdir])

    tot_files = []
    for root, path, files in os.walk(filedir):
        for fi in files:
            fi = root + "/" + fi
            if not fi.endswith(".root"):
                continue
            tot_files.append(fi)

    pbar = ProgressBar(
        widgets=["Calculating W+jets weights %s:" % filedir] + widgets,
        maxval=len(tot_files)
    ).start()

    log = open("WJets_reclassify.log", "w")

    n_file = 0
    for fi in tot_files:
        args = []
        sn = get_sample_name(fi)

        args += ["--isWJets=%s" % str(is_wjets(sn))]
        subprocess.check_call([cmd, "--infile=%s" % fi] + args, stdout=log)
        n_file += 1
        pbar.update(n_file)
    log.close()
    print "Reclassified %d files" % n_file
