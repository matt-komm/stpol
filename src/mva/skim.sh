#!/bin/bash

JULIA=~/local-sl6/julia/julia
OFDIR=skims3
FLDIR=../../filelists/Oct18_csvt_af8ee7
MCDIR=step2/mc/iso/nominal/Jul15

#CSVT
DATANAME=csvt
for fi in W1Jets_exclusive W2Jets_exclusive W3Jets_exclusive W4Jets_exclusive WJets_inclusive
do
    $JULIA ../skim/sub.jl $OFDIR/$DATANAME/wjets/$fi  $FLDIR/$MCDIR/$fi.txt
done

for fi in TTJets_FullLept TTJets_SemiLept TTJets_MassiveBinDECAY
do
    $JULIA ../skim/sub.jl $OFDIR/$DATANAME/ttjets/$fi  $FLDIR/$MCDIR/$fi.txt
done

for fi in T_t_ToLeptons Tbar_t_ToLeptons T_t Tbar_t
do
    $JULIA ../skim/sub.jl $OFDIR/$DATANAME/tchan/$fi  $FLDIR/$MCDIR/$fi.txt
done
