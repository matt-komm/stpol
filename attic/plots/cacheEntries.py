#!/usr/bin/env python
import ROOT
from plots.common.sample import Sample
import argparse

if __name__=="__main__":


    parser = argparse.ArgumentParser(
        description='Caches entries.'
    )

    parser.add_argument('outfile', action='store',
        help="The output file name."
    )

    parser.add_argument('cut', action='store',
        help="The cut string."
    )

    parser.add_argument('infiles', nargs='+',
        help="The input file names"
    )
    args = parser.parse_args()

    of = ROOT.TFile(args.outfile, "RECREATE")

    for inf in args.infiles:
        samp = Sample.fromFile(inf)
        samp_path = samp.getPath(escape=True)
        print samp_path
        cache = samp.cacheEntries(samp_path, args.cut)
        print "Cached %d entries for sample %s" % (cache.GetN(), samp.tfile.GetPath())
        of.cd()
        cache = cache.Clone()
        cache.SetDirectory(of)
        cache.Write()
        samp.tfile.Close()
    #of.Write()
    of.Close()