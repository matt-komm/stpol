#!/bin/bash
#mv CMSSW_5_3_4_cand1/SingleTopPolarization ./

#Tags for https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuidePATReleaseNotes52X#V08_09_43
CMSVERSION=CMSSW_5_3_11
#echo "Stashing current working directory, use 'git stash pop' later to retrieve"
git stash
rm -Rf $CMSVERSION
export SCRAM_ARCH=slc5_amd64_gcc462
cmsrel $CMSVERSION #Base code
cmsrel CMSSW_5_3_8 #Create separate directory for FWLite
git reset --hard
cd $CMSVERSION 

cmsenv
cd $CMSSW_BASE/src

#From official PAT recipe
addpkg DataFormats/PatCandidates V06-05-06-12
addpkg PhysicsTools/PatAlgos     V08-09-62
addpkg PhysicsTools/PatUtils
addpkg RecoBTag/ImpactParameter V01-04-09-01
addpkg RecoBTag/SecondaryVertex V01-10-06
addpkg RecoBTag/SoftLepton      V05-09-11
addpkg RecoBTau/JetTagComputer  V02-03-02
addpkg RecoBTag/Configuration   V00-07-05
addpkg RecoParticleFlow/PFProducer V15-02-06

#For electron MVA https://twiki.cern.ch/twiki/bin/view/CMS/MultivariateElectronIdentification#Recipe_for_5_3_X
cvs co -r V00-00-09 EgammaAnalysis/ElectronTools
cvs co -r V09-00-01 RecoEgamma/EgammaTools
scram b -j 9
cd EgammaAnalysis/ElectronTools/data
cat download.url | xargs wget

cd $CMSSW_BASE/src

#https://twiki.cern.ch/twiki/bin/viewauth/CMS/PileupJetID
cvs co -r V00-03-04 -d CMGTools/External UserCode/CMG/CMGTools/External

#LHAPDF setup must be done prior to full compile
cmsenv
scram setup lhapdffull
cmsenv

scram b -j 8 &> scram_log
cd $CMSSW_BASE/../
source setenv.sh

$STPOL_DIR/setup/install_tunfold.sh
$STPOL_DIR/setup/install_theta.sh
