#!/bin/bash

DIR=$STPOL_DIR
DATADIR=$STPOL_DIR/$CMSSW_VERSION/src/data/pu_weights
mkdir -p $DATADIR
LUMI=crabs/lumis/Cert_190456-208686_8TeV_22Jan2013ReReco_Collisions12_JSON.txt

curl -k https://cms-service-dqm.web.cern.ch/cms-service-dqm/CAF/certification/Collisions12/8TeV/PileUp/pileup_latest.txt > $DATADIR/pileup_latest.txt

pileupCalc.py -i $STPOL_DIR/$LUMI --inputLumiJSON $DATADIR/pileup_latest.txt --calcMode true --minBiasXsec 69400 --maxPileupBin 60 --numPileupBins 60 $DATADIR/data_PU_nominal.root 

#Systematic variations by 5%
#https://twiki.cern.ch/twiki/bin/view/CMS/PileupSystematicErrors
pileupCalc.py -i $STPOL_DIR/$LUMI --inputLumiJSON $DATADIR/pileup_latest.txt --calcMode true --minBiasXsec 72870.0 --maxPileupBin 60 --numPileupBins 60 $DATADIR/data_PU_up.root 
pileupCalc.py -i $STPOL_DIR/$LUMI --inputLumiJSON $DATADIR/pileup_latest.txt --calcMode true --minBiasXsec 65930.0 --maxPileupBin 60 --numPileupBins 60 $DATADIR/data_PU_down.root 



