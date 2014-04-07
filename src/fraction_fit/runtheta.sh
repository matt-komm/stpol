#!/bin/sh
echo "running theta wrapper";
DYLD_LIBRARY_PATH=../../theta/lib ../../theta/utils2/theta-auto.py $@;
echo "theta wrapper is done";
exit 0;

