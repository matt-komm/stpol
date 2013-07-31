#!/usr/bin/env python
#Author: joosep.pata@cern.ch
import os
import argparse
import sys
from crabXml import Task

prefix="file:/hdfs/cms"

if __name__=="__main__":
    parser = argparse.ArgumentParser(
        description='Prepares the step2 file lists from the input RReport.xml files supplied over stdin.'
    )
    parser.add_argument("-i", "--indir", default=None, type=str, required=False,
       help="""
       The input directory to scan recursively for RReport.xml files generated with
        '$crab -USER.xml_report RReport.xml -status -c crab_directory'
        and which end up in crab_directory/share/RReport.xml.
        If omitted, wait for input file names over stdin.
        """
    )

    args = parser.parse_args()

    #Get the input files
    inp = []
    if args.indir:
        for root, dirs, files in os.walk(args.indir):
            for fi in files:
                if fi.endswith("RReport.xml"):
                    inp += ["/".join([root, fi])]
    else:
        print "No input directory specified, waiting for file list over stdin..."
        inp = filter(lambda x: x.endswith("RReport.xml"),
            map(lambda x: x.strip(), sys.stdin.readlines())
        )

    for fi in inp:
        if not fi.endswith("RReport.xml"):
            print "ERROR: wrong input line %s % fi"
            continue
        #print "Processing report file %s" % fi

        try:
            t = Task(fi)
        except ValueError:
            continue

        ofpath = "/".join(fi.replace("crabs", "filelists").split("/")[:-3])
        try:
            os.makedirs(ofpath)
        except:
            pass
        outfile = open(ofpath + "/" + t.name+".txt", "w")

        for job in t.jobs:
            if job.isCompleted() and job.lfn:
                outfile.write(prefix+job.lfn + "\n")
            else:
                print "Error with %s " % str(job)
        print "Saved output to file %s" % outfile.name
        outfile.close()
