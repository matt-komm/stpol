#!/usr/bin/env python
#run as python adder.py out.csv weights.xml infile1.root infile2.root ...

import sys
import ROOT
from ROOT import TMVA
import numpy as np
import time

#TODO: read from file
mvaname = "BDTxx"

#col1: mva name in TMVA.Reader
#col2: name in ROOT TTree
mvavars = [
    ("top_mass", "top_mass"),
    ("eta_lj", "ljet_eta"),
    ("C", "centrality"),
    ("met", "met"),
    ("mt_mu", "mtw"),
    ("mass_bj", "bjet_mass"),
    ("mass_lj", "ljet_mass"),
    ("mu_pt", "lepton_pt"),
    ("pt_bj", "bjet_pt")
]

def setup_mva(mvaname, weightfile, mvavars):
    """
    mvaname: name of the MVA (can be anything)
    weightfile: path to .xml weight file with trained MVA
    mvavars: list of (mvaname, treename) of variables.
        Must contain all of them from weightffile.
    """
    mvareader = TMVA.Reader()

    varlist = [x[0] for x in mvavars]

    varbuffers = {}
    for v in varlist:
        varbuffers[v] = np.array([0], 'f')
        mvareader.AddVariable(v, varbuffers[v])

    mvareader.BookMVA(mvaname, weightfile)

    return mvareader, varbuffers

def setup_infiles(infiles):
    chain = ROOT.TChain("dataframe")
   
    for inf in infiles:
        if not inf.endswith(".root"):
            print "unknown input file format", inf
            continue
        chain.AddFile(inf)
    print "loaded files with",chain.GetEntries(), "events"
    #print "branches:", ", ".join([b.GetTitle() for b in chain.GetListOfBranches()])

    return chain

def rv(event, varname):
    """
    Reads a variable from a TTree, handling the case when data is NA.
    
    event: a TTree that supports event.varname => value access
    varname: a variable name that is present in the TTree.

    returns value, isna
    """
    if hasattr(event, varname+"ISNA"):
        isna = getattr(event, varname+"_ISNA")
    else:
        isna = False

    if hasattr(event, varname):
        val = getattr(event, varname)
    else:
        val = 0.0
        isna = True
    return val, isna

def zero_buffers(varbuffers):
    for k, v in varbuffers.items():
        v[0] = 0.0

if __name__=="__main__":

    tstart = time.time()

    outfile = sys.argv[1]
    weightfile = sys.argv[2]
    infiles = sys.argv[3:]

    mvareader, varbuffers = setup_mva(mvaname, weightfile, mvavars)

    counters = {"evaluated":0}

    inf = setup_infiles(infiles)

    ofile = open(outfile, "w")
    ofile.write('"%s"\n' % mvaname)

    for event in inf:

        zero_buffers(varbuffers)

        #read variables
        isna = False
        for var_mva, var_tree in mvavars:
            v, isna = rv(event, var_tree)
            if isna:
                if not var_tree in counters.keys():
                    counters[var_tree] = 0
                counters[var_tree] += 1
                break
            varbuffers[var_mva][0] = v

        if isna:
            x = -float("inf")
        else:
            x = mvareader.EvaluateMVA(mvaname)
            counters["evaluated"] += 1

        ofile.write(str(x) + "\n")
        #print x

    ofile.close()
    print counters

    tend = time.time()
    print "total elapsed time", tend-tstart, " sec, processed events",inf.GetEntries()


