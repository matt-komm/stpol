#!/bin/bash
#IN=file:/hdfs/cms/store/user/joosep/SingleMu/Jul8_51f69b/7cb0fdcb434651e6fe30ffadc793c329/output_Skim_6_1_pia.root,file:/hdfs/cms/store/user/joosep/SingleMu/Jul8_51f69b/7cb0fdcb434651e6fe30ffadc793c329/output_Skim_11_1_w30.root,
#,'file:/hdfs/cms/store/user/joosep/SingleMu/Jul8_51f69b/7cb0fdcb434651e6fe30ffadc793c329/output_Skim_15_1_tbF.root','file:/hdfs/cms/store/user/joosep/SingleMu/Jul8_51f69b/7cb0fdcb434651e6fe30ffadc793c329/output_Skim_16_1_eWr.root','file:/hdfs/cms/store/user/joosep/SingleMu/Jul8_51f69b/7cb0fdcb434651e6fe30ffadc793c329/output_Skim_18_1_Qip.root','file:/hdfs/cms/store/user/joosep/SingleMu/Jul8_51f69b/7cb0fdcb434651e6fe30ffadc793c329/output_Skim_19_1_BSX.root'
#OFDIR="$STPOL_DIR"/testing/step2/data

#IN='file:/hdfs/cms/store/user/joosep/TToLeptons_t-channel_8TeV-powheg-tauola/Jul8_51f69b/e6cee8f160cb239f414a74aa40d88ea9/output_noSkim_1_2_Nef.root','file:/hdfs/cms/store/user/joosep/TToLeptons_t-channel_8TeV-powheg-tauola/Jul8_51f69b/e6cee8f160cb239f414a74aa40d88ea9/output_noSkim_2_1_pdl.root','file:/hdfs/cms/store/user/joosep/TToLeptons_t-channel_8TeV-powheg-tauola/Jul8_51f69b/e6cee8f160cb239f414a74aa40d88ea9/output_noSkim_3_1_CrB.root','file:/hdfs/cms/store/user/joosep/TToLeptons_t-channel_8TeV-powheg-tauola/Jul8_51f69b/e6cee8f160cb239f414a74aa40d88ea9/output_noSkim_4_1_wiL.root','file:/hdfs/cms/store/user/joosep/TToLeptons_t-channel_8TeV-powheg-tauola/Jul8_51f69b/e6cee8f160cb239f414a74aa40d88ea9/output_noSkim_5_1_UKN.root'
#OFDIR="$STPOL_DIR"/testing/step2/signal2

#IN='file:/hdfs/cms/store/user/joosep/TToLeptons_t-channel_8TeV-powheg-tauola/Jul8_51f69b/e6cee8f160cb239f414a74aa40d88ea9/output_noSkim_1_2_Nef.root'
#OFDIR="$STPOL_DIR"/testing/step2/signal

#IN='file:/hdfs/cms/store/user/joosep/TTJets_FullLeptMGDecays_8TeV-madgraph/Jul8_51f69b/e6cee8f160cb239f414a74aa40d88ea9/output_noSkim_1_1_FwW.root','file:/hdfs/cms/store/user/joosep/TTJets_FullLeptMGDecays_8TeV-madgraph/Jul8_51f69b/e6cee8f160cb239f414a74aa40d88ea9/output_noSkim_2_1_ott.root','file:/hdfs/cms/store/user/joosep/TTJets_FullLeptMGDecays_8TeV-madgraph/Jul8_51f69b/e6cee8f160cb239f414a74aa40d88ea9/output_noSkim_3_1_7Jk.root','file:/hdfs/cms/store/user/joosep/TTJets_FullLeptMGDecays_8TeV-madgraph/Jul8_51f69b/e6cee8f160cb239f414a74aa40d88ea9/output_noSkim_4_1_nNS.root','file:/hdfs/cms/store/user/joosep/TTJets_FullLeptMGDecays_8TeV-madgraph/Jul8_51f69b/e6cee8f160cb239f414a74aa40d88ea9/output_noSkim_5_1_ARH.root','file:/hdfs/cms/store/user/joosep/TTJets_FullLeptMGDecays_8TeV-madgraph/Jul8_51f69b/e6cee8f160cb239f414a74aa40d88ea9/output_noSkim_6_1_SKF.root','file:/hdfs/cms/store/user/joosep/TTJets_FullLeptMGDecays_8TeV-madgraph/Jul8_51f69b/e6cee8f160cb239f414a74aa40d88ea9/output_noSkim_7_1_cFz.root'
#OFDIR="$STPOL_DIR"/testing/step2/ttbar_lep

IN=file:/hdfs/cms/store/user/joosep/SingleMu/Jul8_51f69b/7cb0fdcb434651e6fe30ffadc793c329/output_Skim_206_1_6Ia.root
OFDIR="$STPOL_DIR"/testing/step2/test

echo "Runnin step2 test on IN="$IN" with output to OFDIR="$OFDIR
if [ -d "$OFDIR" ]; then
    echo "Removing "$OFDIR 
    rm -Rf "$OFDIR"
fi

mkdir -p $OFDIR

cmsRun $CMSSW_BASE/src/SingleTopPolarization/Analysis/python/runconfs/step2/step2.py doDebug=False inputFiles=$IN isMC=False subChannel=TTbar outputFile=$OFDIR/out.root #&> $OFDIR/log_step2.txt
EX=$?
echo "Exit code:"$EX 
#if [ "$EX" -ne 0 ]
#then
#    grep -A50 "Exception" $OFDIR/log_step2.txt
#fi
