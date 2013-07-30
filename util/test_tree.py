import root_numpy
import sys
import numpy

if __name__=="__main__":
    fn = sys.argv[1]
    arr = root_numpy.root2rec(fn, "trees/Events")
    for field in sorted(arr.dtype.fields.keys()):
        notnan = arr[field]==arr[field]
        if numpy.sum(notnan)>0:
            min_ = numpy.min(arr[notnan][field])
            max_ = numpy.max(arr[notnan][field])
            print field, min_, max_
            if abs(min_-max_)<0.000001:
                print "W: %s has always the same value: %f" % (field, min_)
        else:
            print "W: %s is always uninitialized!" % field
