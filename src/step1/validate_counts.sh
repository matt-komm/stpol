#!/bin/bash

infile_list=$1

step1_total_processed=0
step2_total_processed=0
step2_total_out=0

for fi in `cat $infile_list`
do
    step1_out_fileutil=`edmFileUtil $fi | grep "event" | cut -f6 -d' '`
    tempfile=out.$$
    cmsRun $CMSSW_BASE/src/SingleTopPolarization/EfficiencyAnalyzer/efficiencyanalyzer_cfg.py inputFiles=$fi >& $tempfile
    if [ $? -eq 0 ]; then
        
        step1_processed=`cat $tempfile | grep "PATTotalEventsProcessedCount" | cut -f3 -d' '`
        step2_processed=`cat $tempfile | grep "STPOLSEL2TotalEventsProcessedCount" | cut -f3 -d' '`
        
        step1_in_mu=`cat $tempfile | grep "singleTopPathStep1MuPreCount" | cut -f3 -d' '`
        step1_in_ele=`cat $tempfile | grep "singleTopPathStep1ElePreCount" | cut -f3 -d' '`
        
        step1_out_mu=`cat $tempfile | grep "singleTopPathStep1MuPostCount" | cut -f3 -d' '`
        step1_out_ele=`cat $tempfile | grep "singleTopPathStep1ElePostCount" | cut -f3 -d' '`
        
        step2_in_mu=`cat $tempfile | grep "muPathPreCount" | cut -f3 -d' '`
        step2_in_ele=`cat $tempfile | grep "elePathPreCount" | cut -f3 -d' '`

        step2_out_mu=`cat $tempfile | grep "muPathPostCount" | cut -f3 -d' '`
        step2_out_ele=`cat $tempfile | grep "elePathPostCount" | cut -f3 -d' '`
        
        echo "input "$fi" | file "$step1_out_fileutil" | s1_in "$step1_processed" s2_in "$step2_processed
        echo "step1 | mu "$step1_in_mu" "$step1_out_mu" | ele "$step1_in_ele" "$step1_out_ele
        echo "step2 | mu "$step2_in_mu" "$step2_out_mu" | ele "$step2_in_ele" "$step2_out_ele

        step1_total_processed=$(( $step1_total_processed + $step1_processed ))
        #step2_total_processed=$(( $step2_total_processed + $step2_processed ))
        #step2_total_out=$(( $step2_total_out + $step2_out_mu ))
    else
        cat $tempfile
        exit 1
    fi
done

echo "step1 total processed "$step1_total_processed
#echo "step2 total processed "$step2_total_processed
#echo "step2 total out mu "$step2_total_out
rm $tempfile
