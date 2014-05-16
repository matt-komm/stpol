#!/bin/sh
echo "running theta wrapper";
echo $PYTHONPATH
DYLD_LIBRARY_PATH=../../theta/lib:$DYLD_LIBRARY_PATH ../../theta/utils2/theta-auto.py $@;
echo "theta wrapper is done";
exit 0;

