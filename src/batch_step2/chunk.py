#!/usr/bin/env python
import sys

csize = 5

def clean(line):
    line = line.strip()
    return line.replace("file:/hdfs/cms", "")
if __name__=="__main__":

    stack = []
    for line in sys.stdin.readlines():
        line = clean(line)
        if len(stack)<csize:
            stack.append(line)
        else:
            print ",".join(stack)
            stack = []
