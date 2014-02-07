#!/bin/bash
cmsRun /home/morten/stpol/CMSSW_5_3_4/src/SingleTopPolarization/CollectionSizeProducer/collectionsizeproducer_cfg.py inputFiles=file:/hdfs/local/stpol/sync2012/FCE664EC-E79B-E111-8B06-00266CF2507C.root outputFile=$CMSSW_BASE/../collectionsizeprodtest.root maxEvents=10
