#!/usr/bin/env python
"""
Performs operations programmatically using the das_cli.
"""

import das_cli
import sys
from copy import deepcopy
import pdb
from datasets import datasets2
from tempfile import TemporaryFile
import argparse
import os

def call_das_cli(*args):
    """
    Calls das_cli.py using the specified positional arguments.

    Args:
        *args: a positional list of command line arguments for das_cli.py

    Returns:
        The return code from the das_cli.py main method.
    """
    oldarg = deepcopy(sys.argv)
    sys.argv += args
    print sys.argv
    ret = das_cli.main()
    sys.argv = oldarg
    return ret


def local_ds_files(ds):
    """
    Gets the list of files corresponding to a published dataset
    stored on cms_dbs_ph_analysis_02.

    Args:
        ds: the path to the published dataset, ending in /USER

    Returns:
        A list of the LFN-s of the dataset.
    """
    tf = TemporaryFile()
    stdout = sys.stdout
    stdout.flush()
    sys.stdout = tf
    print "Query"
    ret = call_das_cli('--query=file dataset=%s instance=cms_dbs_ph_analysis_02' % ds, '--limit=0')
    print ret
    tf.flush()
    tf.seek(0)
    sys.stdout = stdout
    fl = []
    for li in tf.readlines():
        if "/store/" in li:
            fl.append(li.strip())
    tf.close()
    return fl


if __name__=="__main__":
    parser = argparse.ArgumentParser(
        description='Gets the information on DAS datasets systematically'
    )

    parser.add_argument('infile', action='store',
        help="The input file with the list datasets to be parsed by datasets/datasets2.py"
    )
    args = parser.parse_args()

    dsl = datasets2.parse_file(args.infile)
    for ds in dsl:
        files = local_ds_files(ds.ds)
        ofpath = args.infile.replace("datasets", "filelists")
        try:
            os.makedirs(ofpath)
        except:
            pass
        ofn = os.path.join(ofpath, ds.ds.split("/")[1])
        print ds.ds, ds.name, len(files)
        ofi = open(ofn, "w")
        for fi in files:
            ofi.write(fi + "\n")
        ofi.close()
