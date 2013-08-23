import root_numpy
import sys

if __name__=="__main__":
    for fi in sys.argv[1:]:
        arr = root_numpy.root2rec(fi, "trees/Events", branches=["event_id"])
        A=len(arr)
        B=len(set(arr))
        print fi, A
        if A!=B:
            print "dupes: %s"% fi
