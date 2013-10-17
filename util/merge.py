from subprocess import check_call
from os import walk
from os.path import join
import sys
from glob import glob

if __name__=="__main__":
    ind = sys.argv[1]
    for root, dirs, items in walk(ind):
        items_in_dirs = map(lambda x: glob(join(root, x, "*.root")), dirs)
        tot = sum(map(lambda x: len(x), items_in_dirs))
        if tot>0:
            for d, i in zip(dirs, items_in_dirs):
                print d, i
