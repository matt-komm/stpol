#!/bin/bash
timestamp=`eval date +%m_%d_%H_%M`
OFDIR=out_step3_$timestamp
FLDIR=filelists/step2/latest/
mkdir -p $OFDIR/mu
mkdir -p $OFDIR/mu/iso/nominal
mkdir -p $OFDIR/mu/antiiso/nominal
mkdir -p $OFDIR/ele
mkdir -p $OFDIR/ele/iso/nominal
mkdir -p $OFDIR/ele/antiiso/nominal
CUT="--doHLT --doNJets --nJ=2,9999"

$STPOL_DIR/analysis_step3/suball.sh "$CUT --lepton=mu" $OFDIR/mu/iso/nominal $FLDIR/iso/nominal/data/SingleMu*
$STPOL_DIR/analysis_step3/suball.sh "$CUT --lepton=mu" $OFDIR/mu/antiiso/nominal $FLDIR/antiiso/nominal/data/SingleMu*
$STPOL_DIR/analysis_step3/suball.sh "$CUT --lepton=mu --doControlVars --isMC" $OFDIR/mu/iso/nominal $FLDIR/iso/nominal/mc/*
$STPOL_DIR/analysis_step3/suball.sh "$CUT --lepton=mu --doControlVars --isMC" $OFDIR/mu/antiiso/nominal $FLDIR/antiiso/nominal/mc/*

$STPOL_DIR/analysis_step3/suball.sh "$CUT --lepton=ele" $OFDIR/ele/iso/nominal $FLDIR/iso/nominal/data/SingleEle*
$STPOL_DIR/analysis_step3/suball.sh "$CUT --lepton=ele" $OFDIR/ele/antiiso/nominal $FLDIR/antiiso/nominal/data/SingleEle*
$STPOL_DIR/analysis_step3/suball.sh "$CUT --lepton=ele --doControlVars --isMC" $OFDIR/ele/iso/nominal $FLDIR/iso/nominal/mc/*
$STPOL_DIR/analysis_step3/suball.sh "$CUT --lepton=ele --doControlVars --isMC" $OFDIR/ele/antiiso/nominal $FLDIR/antiiso/nominal/mc/*
