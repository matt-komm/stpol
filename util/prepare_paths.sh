#!/bin/bash
rm -Rf $STPOL_DIR/$CMSSW_VERSION/python
mkdir -p $STPOL_DIR/$CMSSW_VERSION/python/SingleTopPolarization/Analysis
ls $STPOL_DIR/$CMSSW_VERSION/python/SingleTopPolarization/Analysis

echo '' > $STPOL_DIR/$CMSSW_VERSION/python/__init__.py
echo '' > $STPOL_DIR/$CMSSW_VERSION/python/SingleTopPolarization/__init__.py
echo 'import os; __path__.append(os.path.join(os.environ["STPOL_DIR"], os.environ["CMSSW_VERSION"], "src/SingleTopPolarization/Analysis/python"))' > $STPOL_DIR/$CMSSW_VERSION/python/SingleTopPolarization/Analysis/__init__.py
