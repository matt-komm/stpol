import subprocess
import glob
import os
if __name__=="__main__":

	basedir = os.environ["STPOL_DIR"]
	cmd = "%s/bin/WJets_reweighting" % basedir

	files = glob.glob("%s/step3_latest/mu/iso/nominal/W*Jets*.root" % basedir)
	print files
	for fi in files:
		subprocess.check_call([cmd, fi])
