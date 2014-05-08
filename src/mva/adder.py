#!/usr/bin/env python
#run as ./adder.py mva_name weights.xml infile1.root infile2.root ...
#output will be infile1_mva_mva_name.csv ...

import sys
import ROOT
from ROOT import TMVA
import numpy as np
import time

from xml.dom import minidom
from path import STPOL_DIR

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

        ofile = open(ofn, "w", 1)
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

        if nproc != int(tree.GetEntries()):
            raise Exception("incorrect amount of events processed")
        ofile.write("# ntree=%d nproc=%d\n" % (tree.GetEntries(), nproc))
        print counters
        inf.Close()
        ofile.close()


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
        print "variable",v
    for v in _specvars:
        varbuffers[v] = np.array([0], 'f')
        mvareader.AddSpectator(v, varbuffers[v])
        print "spectator",v

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
    if not hasattr(event, varname):
        raise Exception("variable '%s' not defined" % varname)

    if hasattr(event, varname+"_ISNA"):
        isna = getattr(event, varname+"_ISNA")
    else:
        isna = False

    val = getattr(event, varname)

    return val, isna

def zero_buffers(varbuffers):
    for k, v in varbuffers.items():
        v[0] = 0.0


def mva_loop_lepton_separate(mvaname, infiles, mvas, varmaps):
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

            #make sure the TBranch buffers have a 0 values
            for (k, mva) in mvas.items():
                zero_buffers(mva[1])

            lepton_type, lepton_type_isna = rv(event, "lepton_type")
            isna = False
            isna = isna or lepton_type_isna
            if not isna:
                mvareader, varbuffers = mvas[lepton_type]

                varmap = varmaps[lepton_type]
                for var in varbuffers.keys():
                    if var in varmap.keys():
                        varn = varmap[var]
                    else:
                        varn = var

                    v, _isna = rv(event, varn)
                    isna = isna or _isna
                    if not isna:
                        varbuffers[var][0] = v
                    else:
                        break
                if not isna:
                    x = mvareader.EvaluateMVA(mvaname)
            if isna:
                x = "NA" #MVA(..., NA, ...) -> NA

            ofile.write(str(x) + "\n")
            nproc += 1
        ofile.write("# ntree=%d nproc=%d\n" % (tree.GetEntries(), nproc))
        ofile.close()
        if nproc!=int(tree.GetEntries()):
            raise Exception("incorrect amount of MVA evaluations")
        inf.Close()
if __name__=="__main__":
    main()
