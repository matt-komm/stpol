from subprocess import check_call
import os
import shutil
import logging
import sys
logger = logging.getLogger("tests")

def test_cmssw(config, infile, outfile, ofdir, extra_args=[]):
    try:
        os.makedirs(ofdir)
    except:
        logger.info("Removing %s" % ofdir)
        shutil.rmtree(ofdir)
        os.makedirs(ofdir)

    logfile = open(ofdir + "/" + "log.txt", "w")
    ofname = ofdir + "/" + outfile
    cmd = [
        "cmsRun",
        config, "inputFiles=%s" % infile, "outputFile=%s" % ofname
    ] + extra_args
    print " ".join(cmd)
    check_call(cmd, stdout=logfile, stderr=sys.stdout)

def test_step3(infile, outfile, ofdir, extra_args=[]):
    if infile.endswith(".txt"):
        infile = open(infile).readlines()
        if len(infile)>0:
            infile = infile[0]
        else:
            raise Exception("File is empty")
        if infile.startswith("file:"):
            infile = infile[5:]
        infile = infile.strip()
    if not os.path.exists(infile) or not infile.endswith(".root"):
        raise ValueError("Input file is incorrect: %s" % infile)

    try:
        os.makedirs(ofdir)
    except:
        logger.info("Removing %s" % ofdir)
        shutil.rmtree(ofdir)
        os.makedirs(ofdir)

    logfile = open(ofdir + "/" + "log.txt", "w")
    ofname = ofdir + "/" + outfile
    infiles = ofdir + "/" + "in.txt"
    fi = open(infiles, "w")
    fi.write(infile)
    fi.close()
    fi = open(infiles)

    exe = os.environ["CMSSW_BASE"] + "/bin/" + os.environ["SCRAM_ARCH"] + "/Step3_EventLoop"
    cfg = os.environ["CMSSW_BASE"] + "/src/SingleTopPolarization/Analysis/python/runconfs/step3/base_nocuts.py"
    check_call([
        exe,
        cfg, "--outputFile=%s" % ofname
    ] + extra_args, stdin=fi, stdout=logfile, stderr=sys.stdout)
    logfile.close()

if __name__=="__main__":
    logging.basicConfig(level=logging.INFO)

    bd = os.environ["CMSSW_BASE"]
    rcd = "src/SingleTopPolarization/Analysis/python/runconfs"

    print "step1"
    test_cmssw(
        join(bd, rcd, "step1/step1.py")
        "file:/hdfs/cms/store/user/joosep/TTJets_SemiLeptMGDecays_8TeV-madgraph/Jul8_51f69b/e6cee8f160cb239f414a74aa40d88ea9/output_noSkim_1_2_1X6.root",
        "test.root",
        "test/ttbar/step2",
        extra_args=["subChannel=TTbar"]
    )

    print "step2"
    test_cmssw(
        "/home/joosep/singletop/stpol/CMSSW_5_3_11/src/SingleTopPolarization/Analysis/python/runconfs/step2/step2.py",
        "file:/hdfs/cms/store/user/joosep/TTJets_SemiLeptMGDecays_8TeV-madgraph/Jul8_51f69b/e6cee8f160cb239f414a74aa40d88ea9/output_noSkim_1_2_1X6.root",
        "test.root",
        "test/ttbar/step2",
        extra_args=["subChannel=TTbar"]
    )

    print "step3 ttbar"
    test_step3(
        "test/ttbar/step2/test.root",
        "test.root",
        "test/ttbar/step3",
        extra_args=["--doControlVars", "--isMC"]
    )

    print "step3 data"
    test_step3(
        "filelists/83a02e9_Jul22/step2/data/iso/Jul15/SingleMu1.txt",
        "test.root",
        "test/data/step3",
        extra_args=["--doControlVars"]
    )
