#!/bin/bash
for i in `find $1 -name "*.root"`
do
    ./addMVAasFriend.py -f $i -c $2
done
