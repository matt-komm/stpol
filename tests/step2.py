#!/usr/bin/env python
from SingleTopPolarization.Analysis.test_files import testfiles
import unittest
from unittest import TestCase
from subprocess import check_call
import os

stpol_dir = os.environ.get("STPOL_DIR")

def cmsrun(*args):
    return check_call(["cmsRun"] + list(args))

class TestStep2(TestCase):
    andir = os.path.join(stpol_dir, "CMSSW_5_3_11/src/SingleTopPolarization/Analysis/python")
    ofdir = os.path.join(stpol_dir, "out/testing")

    def setUp(self):
        pass

    def test_step2(self):
        nev = 100
        cmsrun(
            self.andir + "/runconfs/step2/step2.py",
            "inputFiles=%s" % testfiles["step1"]["signal"],
            "outputFile=%s/test_step2.root" % self.ofdir,
            "maxEvents=%d" % nev
        )
        ofile = self.ofdir + "/test_step2_numEvent%d.root" % nev
        assert(os.path.exists(ofile))

if __name__=="__main__":
    unittest.main()

