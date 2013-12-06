#!/bin/bash
DIR="~/singletop/stpol2"
CMD="rsync --progress --ignore-times -r cms.hep.kbfi.ee"

$CMD:$DIR/src/skim/oct* results/

#rsync --progress --ignore-times -r cms.hep.kbfi.ee:$DIR/results ./
#rsync --progress --ignore-times -r cms.hep.kbfi.ee:/hdfs/local/stpol/fit_histograms/no_powheg_fix results/
#rsync --progress --ignore-times -r cms.hep.kbfi.ee:/hdfs/local/stpol/qcd_histograms results/
#
#rsync --progress --ignore-times -r cms.hep.kbfi.ee:/hdfs/local/stpol/fit_histograms/final results/fit_histograms/
#rsync --progress --ignore-times -r cms.hep.kbfi.ee:/hdfs/local/stpol/unfolding_histograms/final results/unfolding_histograms/
