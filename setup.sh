#!/bin/bash
#mv CMSSW_5_3_4_cand1/SingleTopPolarization ./

#Tags for https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuidePATReleaseNotes52X#V08_09_43
CMSVERSION=CMSSW_5_3_11
#echo "Stashing current working directory, use 'git stash pop' later to retrieve"
#git stash
rm -Rf $CMSVERSION
export SCRAM_ARCH=slc5_amd64_gcc462
cmsrel $CMSVERSION #Base code
cmsrel CMSSW_5_3_8 #Create separate directory for FWLite
#git reset --hard
cd $CMSVERSION 

cmsenv
cd $CMSSW_BASE/src

addpkg DataFormats/PatCandidates V06-05-06-12
addpkg PhysicsTools/PatAlgos     V08-09-62
addpkg PhysicsTools/PatUtils
addpkg RecoBTag/ImpactParameter V01-04-09-01
addpkg RecoBTag/SecondaryVertex V01-10-06
addpkg RecoBTag/SoftLepton      V05-09-11
addpkg RecoBTau/JetTagComputer  V02-03-02
addpkg RecoBTag/Configuration   V00-07-05
addpkg RecoParticleFlow/PFProducer V15-02-06

#addpkg DataFormats/StdDictionaries   V00-02-14
#addpkg FWCore/GuiBrowsers            V00-00-70
#addpkg RecoParticleFlow/PFProducer   V15-02-06
#
#addpkg CommonTools/CandAlgos V00-01-03 
#addpkg CommonTools/UtilAlgos V00-02-07
#addpkg CommonTools/Utils V00-04-04
#addpkg CommonTools/RecoUtils                V00-00-14
#addpkg CommonTools/RecoAlgos                V00-03-24
#addpkg CommonTools/ParticleFlow             V00-03-16
#addpkg DataFormats/ParticleFlowCandidate     V15-03-04      
#addpkg DataFormats/TrackReco                V10-02-02      
#addpkg DataFormats/VertexReco               V02-00-04 
#addpkg RecoLuminosity/LumiDB                V04-01-09 ##Newer than in TagCollector for 5_3_X

cvs co -r V00-00-31 -d EGamma/EGammaAnalysisTools UserCode/EGamma/EGammaAnalysisTools
cd EGamma/EGammaAnalysisTools/data
cat download.url | xargs wget

cd $CMSSW_BASE/src

#https://twiki.cern.ch/twiki/bin/viewauth/CMS/MissingETOptionalFilters#EB_or_EE_Xtals_with_large_laser
#addpkg RecoMET/METFilters  V00-00-09 

#https://twiki.cern.ch/twiki/bin/viewauth/CMS/PileupJetID
#cvs co -r V00-02-10 -d CMGTools/External UserCode/CMG/CMGTools/External

#LHAPDF setup must be done prior to full compile
cmsenv
scram setup lhapdffull
cmsenv

#scram b -j 8 &> scram_log
#cd $CMSSW_BASE/../
#source setenv.sh
#
#$STPOL_DIR/setup/install_tunfold.sh
#$STPOL_DIR/setup/install_theta.sh
