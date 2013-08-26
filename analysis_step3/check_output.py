#!/usr/bin/env python
import os
import re
import argparse

if __name__=="__main__":
    parser = argparse.ArgumentParser(
        description='Checks the status of step3 processing'
    )
    parser.add_argument(
        "indir", type=str, default="out/step3",
        help="the input directory for the step3 trees and slurmfiles"
    )
    args = parser.parse_args()
    indir = args.indir
    if not os.path.exists(indir):
        raise ValueError("Input directory %s does not exist!")

    total = dict()
    total["all"] = 0
    total["done"] = 0
    total["failed"] = 0
    total["running"] = 0
    for root, dirs, files in os.walk(indir):
        if not len(filter(lambda x: x=="job", files))==1:
            continue
        tasks = filter(lambda x: x.startswith("task"), files)
        xfiles = filter(lambda x: re.match("x[0-9]*", x), files)
        slurmfiles = filter(lambda x: x.endswith(".out"), files)

        pat_done = re.compile("^step3 exit code: 0\n$")
        pat_failed = re.compile(".*CANCELLED.*|^step3 exit code: [^0].*")
        donefiles = []
        failedfiles = []
        for fi in slurmfiles:
            f = open("/".join([root, fi]))
            for line in f.readlines():
                if pat_done.match(line):
                    donefiles += [fi]
                    break
                if pat_failed.match(line):
                    failedfiles += [fi]
                    break
            f.close()
        if len(donefiles)!=len(slurmfiles):
            stat = "running"
        elif len(slurmfiles)>0:
            stat = "done"
        else:
            stat = "submitting"
        runningfiles = list(set(slurmfiles).difference(set(donefiles)).difference(set(failedfiles)))
        total["all"] += len(slurmfiles)
        total["done"] += len(donefiles)
        total["failed"] += len(failedfiles)
        total["running"] += len(runningfiles)
        print stat, root, len(tasks), len(xfiles), len(slurmfiles), len(donefiles)
        for rf in runningfiles:
            print "\tR %s" %(root + "/" + rf)
        for ff in failedfiles:
            print "\tF %s" % (root + "/" + ff)
        if len(tasks)!=len(xfiles):
            print "Problem with %s" % root
            print tasks
            print xfiles
    print total
