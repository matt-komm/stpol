from optparse import OptionParser
import ROOT
from ROOT import *
import math
import numpy
import random
import os
import sys


if __name__=="__main__":
    parser=OptionParser()
    (options, args)=parser.parse_args()
    if len(args)<3:
        print "usage: python TMmerger.py [in1] [in2] [..] [out]"
        sys.exit(-1)
        
    inFiles=[]
    
    for i in range(len(args)-1):
        inputFile = ROOT.TFile(args[i],"r")
        inFiles.append({"file":inputFile,"keys":[key.GetName() for key in inputFile.GetListOfKeys()]})
        print args[i],
        
    outFile = ROOT.TFile(args[-1],"recreate")
    print " -> ",args[-1]
    
    commonKeys=inFiles[0]["keys"]
    for i in range(1,len(inFiles)):
        commonKeys = list(set(commonKeys).intersection(set(inFiles[i]["keys"])))
    for key in commonKeys:
        mergedObj=None
        for inputFile in inFiles:
            obj = inputFile["file"].Get(key)
            obj.SetDirectory(0)
            if type(obj)==type(ROOT.TH1D()):
                if mergedObj==None:
                    mergedObj=ROOT.TH1D(obj)
                else:
                    mergedObj.Add(obj)
            if type(obj)==type(ROOT.TH2D()):
                if mergedObj==None:
                    mergedObj=ROOT.TH2D(obj)
                else:
                    mergedObj.Add(obj)
        if (mergedObj!=None):
            mergedObj.SetDirectory(outFile)
            mergedObj.Write()
    
    
    outFile.Close()
    for i in range(len(args)-1):
        inFiles[i]["file"].Close()
    
