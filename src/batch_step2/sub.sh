#!/bin/bash

jobfile=$1
PWD=`pwd`
cd `dirname $jobfile`
FN=`basename $jobfile`
eval `cat $FN`
cd $PWD
