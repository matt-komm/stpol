#!/usr/bin/env python
#Author: joosep.pata@cern.ch
import os
import argparse
import sys
from crabXml import Task, JobStats
if __name__=="__main__":

    parser = argparse.ArgumentParser(
        description=''
    )
    parser.add_argument("infile", default=".", type=str,
       help="""
        """
    )
    args = parser.parse_args()
    t = Task(args.infile)

    print t.output_dir
    for j in t.jobs:
        if j.isCompleted() and not os.path.exists(os.path.join(t.output_dir, j.outputFiles[1])):
            print "C but no FJR", j, j.wrapper_ret_code, j.app_ret_code
    js = JobStats(t)
    print js.summary()
    print str(js)
