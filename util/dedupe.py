#!/usr/bin/python
import re
import sys
import pdb

pat = re.compile(".*_([0-9]+)_([0-9]+)_.*\.root")
if __name__=="__main__":
    lines = sys.stdin.readlines()
    #lines = open(sys.argv[1]).readlines()
    lines = map(lambda x: x.strip(), lines)
    lines.sort()

    fileD = dict()
    for line in lines:
        line = line.strip()
        mat = pat.match(line)
        if not mat:
            print "no match:", line
            continue
        jobN = mat.group(1)
        fileN = mat.group(2)
        fileD[jobN] = line

    for v in sorted(fileD.values()):
        print v
