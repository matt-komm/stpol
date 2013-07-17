import subprocess
import glob
import os
if __name__=="__main__":

	basedir = os.environ["STPOL_DIR"]
	cmd = "%s/bin/WJets_reweighting" % basedir

	files = glob.glob("%s/data/out_step3_joosep_11_07_19_44/mu/iso/nominal/W*Jets*.root" % basedir)
	print files
	for fi in files:
		subprocess.check_call([cmd, fi])