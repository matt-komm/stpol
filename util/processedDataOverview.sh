#!/bin/bash
#This script gets the processed lumi from crab jobs in a machine-readable format

set -e

#find all the crab working directories
for i in `find . -name "WD_*"`
do

    #not a directory
    if [ ! -d $i ]; then continue; fi;

    #get the input dataset name
    INPUTDS=`cat $i/log/crab.log | grep "CMSSW.datasetpath" | cut -d' ' -f6`

    #get the output dataset name
    OUTPUTDS=`grep "<User Dataset Name>" $i/log/crab.log | tail -n1 | cut -f8 -d' '`

    #get the number of events
    NEVENTS=`grep "Total Events read" $i/log/crab.log | tail -n1 | cut -d' ' -f4`     
    MERGEDOUT="${i:3}.root"
    crab -c $i -report &> /dev/null
    #if [ ! -f $i/res/lumiSummary.json ]; then crab -c $i -report &> /dev/null; fi
    lumiCalc2.py -i $i/res/lumiSummary.json -o lumi.out overview &> $i/lumiCalc.out
    if [ -f lumi.out ]
    then
        LUMI=`$STPOL_DIR/util/addLumis.py lumi.out`
        rm lumi.out
    fi

    #if [ -f $MERGEDOUT ]
    #then
    #    mv $MERGEDOUT ${MERGEDOUT%.*}"_"$LUMI"_pb.root"
    #fi
    echo "| "$i" | "$INPUTDS" | "$OUTPUTDS" | "$LUMI" | "$NEVENTS" |"
done
