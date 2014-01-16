#!/usr/bin/env python
#run as ./adder.py mva_name weights.xml infile1.root infile2.root ...
#output will be infile1_mva_mva_name.csv ...

import sys
import ROOT
from ROOT import TMVA
import numpy as np
import time

from xml.dom import minidom

treename = "dataframe"

def main():
    tstart = time.time()
    try:
        mvaname = sys.argv[1]
        weightfile = sys.argv[2]
        infiles = sys.argv[3:]
    except:
        print "adder.py mvaname weightfile.xml infile1.root infile2.root ..."
        return

    mvareader, varbuffers = setup_mva(mvaname, weightfile)

    counters = {"evaluated":0, "processed":0}

    #loop over input file names
    for infn in infiles:
        print "Processing file",infn
        #get the events tree
        inf = ROOT.TFile(infn)
        tree = inf.Get(treename)

        if not tree:
            raise Exception("Could not open TTree '%s' in %s" % (treename, infn))

        ofn = infn.replace(".root", "_mva_%s.csv" % mvaname)

        ofile = open(ofn, "w")
        ofile.write("# filename=%s\n" % infn)
        ofile.write("bdt\n")

        nproc = 0
        for event in tree:
            counters["processed"] += 1

            #make sure the TBranch buffers have a 0 values
            zero_buffers(varbuffers)

            #was any of the variables NA?
            isna = False

            for var in varbuffers.keys():
                v, isna = rv(event, var)
                if isna:
                    if not var in counters.keys():
                        counters[var] = 0
                    counters[var] += 1
                    break #one variable was NA, lets stop
                varbuffers[var][0] = v

            if (isna) or not event.passes:
                x = "NA" #MVA(..., NA, ...) -> NA
            else:
                #print [(x, y[0]) for x,y in varbuffers.items()]
                x = mvareader.EvaluateMVA(mvaname)
                counters["evaluated"] += 1

            ofile.write(str(x) + "\n")
            nproc += 1

        ofile.write("# ntree=%d nproc=%d\n" % (tree.GetEntries(), nproc))
        inf.Close()
        ofile.close()

    print counters

    tend = time.time()
    print "total elapsed time", tend-tstart, " sec, processed events",counters["processed"]



def setup_mva(mvaname, weightfile):
    """
    mvaname: name of the MVA (can be anything)
    weightfile: path to .xml weight file with trained MVA
        Must contain all of them from weightffile.
    """
    mvareader = TMVA.Reader("S")

    dom = minidom.parse(weightfile)

    #read mva variables and spectators from weights.xml
    _mvavars = [str(x.attributes["Label"].value) for x in dom.getElementsByTagName("Variables")[0].childNodes if x.nodeType == 1]
    _specvars = [str(x.attributes["Label"].value) for x in dom.getElementsByTagName("Spectators")[0].childNodes if x.nodeType == 1]

    varbuffers = {}
    for v in _mvavars:
        varbuffers[v] = np.array([0], 'f')
        mvareader.AddVariable(v, varbuffers[v])

    for v in _specvars:
        varbuffers[v] = np.array([0], 'f')
        mvareader.AddSpectator(v, varbuffers[v])

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
    main()
