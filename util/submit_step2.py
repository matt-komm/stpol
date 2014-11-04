import sys, os

infile = sys.argv[1]
pars = sys.argv[2]
ofdir = sys.argv[3]

dataname = sys.argv[4]

njob = 1
perjob = 10
lines = map(lambda x: x.strip(), open(infile).readlines())
for n in range(0, len(lines), perjob):
	fs = lines[n:n+perjob]
	sc_ofn = ofdir + "/job_%d.sh"%njob
	of = open(sc_ofn, "w")
	ofname = "/scratch/" + os.environ["USER"] + "/step2/$SLURM_JOBID/step2_output_%d.root"%njob
	of.write("#!/bin/bash\n")
	of.write("set -e\n")
	of.write("echo 'SCRIPT=%s'\n" % sc_ofn)
	of.write("mkdir -p " + os.path.dirname(ofname) + "\n")
	of.write("cmsRun $CMSSW_BASE/src/SingleTopPolarization/Analysis/python/runconfs/step2/step2.py inputFiles=%s outputFile=%s %s\n" % (",".join(fs), ofname, pars))
	of.write("mkdir -p /hdfs/local/%s/stpol/step2/%s\n" % (os.environ["USER"], dataname))
	of.write("rm -f /hdfs/local/%s/stpol/step1/%s/output_%d.root\n" % (os.environ["USER"], dataname, njob))
	of.write("cp %s /hdfs/local/%s/stpol/step2/%s/output_%d.root\n" % (ofname, os.environ["USER"], dataname, njob))
	of.write("rm -Rf " + os.path.dirname(ofname) + "\n")
	of.write("echo \"JOB DONE\"\n")
	of.close()
	os.system("chmod +x %s/job_%d.sh"%(ofdir, njob))
	njob += 1
