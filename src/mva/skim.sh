#!/bin/bash

JULIA=~/local-sl6/julia/julia

##CSVM
#for fi in W1Jets_exclusive W2Jets_exclusive W3Jets_exclusive W4Jets_exclusive
#do
#    $JULIA ../skim/sub.jl skims/csvm/wjets/$fi  ../../filelists/Oct3_nomvacsv_nopuclean_e224b5/step2/mc/iso/nominal/Jul15/$fi.txt
#done
#
#for fi in TTJets_FullLept TTJets_SemiLept
#do
#    $JULIA ../skim/sub.jl skims/csvm/ttjets/$fi  ../../filelists/Oct3_nomvacsv_nopuclean_e224b5/step2/mc/iso/nominal/Jul15/$fi.txt
#done
#
#for fi in T_t_ToLeptons Tbar_t_ToLeptons
#do
#    $JULIA ../skim/sub.jl skims/csvm/tchan/$fi  ../../filelists/Oct3_nomvacsv_nopuclean_e224b5/step2/mc/iso/nominal/Jul15/$fi.txt
#done


#CSVT
for fi in W1Jets_exclusive W2Jets_exclusive W3Jets_exclusive W4Jets_exclusive
do
    $JULIA ../skim/sub.jl skims/csvt/wjets/$fi  ../../filelists/Oct18_csvt_af8ee7/step2/mc/iso/nominal/Jul15/$fi.txt
done

for fi in TTJets_FullLept TTJets_SemiLept
do
    $JULIA ../skim/sub.jl skims/csvt/ttjets/$fi  ../../filelists/Oct18_csvt_af8ee7/step2/mc/iso/nominal/Jul15/$fi.txt
done

for fi in T_t_ToLeptons Tbar_t_ToLeptons
do
    $JULIA ../skim/sub.jl skims/csvt/tchan/$fi  ../../filelists/Oct18_csvt_af8ee7/step2/mc/iso/nominal/Jul15/$fi.txt
done

#TCHPT
DIR=../../filelists/343e0a9_Aug22/step2/mc/iso/nominal/Jul15
for fi in W1Jets_exclusive W2Jets_exclusive W3Jets_exclusive W4Jets_exclusive
do
    $JULIA ../skim/sub.jl skims/tchpt/wjets/$fi  $DIR/$fi.txt
done

for fi in TTJets_FullLept TTJets_SemiLept
do
    $JULIA ../skim/sub.jl skims/tchpt/ttjets/$fi  $DIR/$fi.txt
done

for fi in T_t_ToLeptons Tbar_t_ToLeptons
do
    $JULIA ../skim/sub.jl skims/tchpt/tchan/$fi  $DIR/$fi.txt
done
