#NOTE: you must source this script, not execute it!
#mv CMSSW_5_3_4_cand1/SingleTopPolarization ./

# Sanity check
echo "Do you wish to really run setup?"
select yn in "Yes" "No"; do
	case $yn in
		Yes ) break;;
		No ) exit;;
	esac
done

#Tags for https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuidePATReleaseNotes52X#V08_09_43
[[ ! -z "$CMSVERSION" ]] || CMSVERSION=CMSSW_5_3_11
#echo "Stashing current working directory, use 'git stash pop' later to retrieve"
git stash #temporaryily store changes
rm -Rf $CMSVERSION #remove the source tree for cmsrel to work
export SCRAM_ARCH=slc5_amd64_gcc462
cmsrel $CMSVERSION #Base code
git checkout CMSSW_5_3_11
#git reset --hard #bring back the source tree
cd $CMSVERSION 

cmsenv
cd $CMSSW_BASE/src

#From official PAT recipe
addpkg DataFormats/PatCandidates V06-05-06-12
addpkg PhysicsTools/PatAlgos     V08-09-62
addpkg PhysicsTools/PatUtils #V03-09-28 FIXME
addpkg RecoBTag/ImpactParameter V01-04-09-01
addpkg RecoBTag/SecondaryVertex V01-10-06
addpkg RecoBTag/SoftLepton      V05-09-11
addpkg RecoBTau/JetTagComputer  V02-03-02
addpkg RecoBTag/Configuration   V00-07-05
addpkg RecoParticleFlow/PFProducer V15-02-06
addpkg RecoLuminosity/LumiDB V04-02-08 #For lumicalc
#For electron MVA https://twiki.cern.ch/twiki/bin/view/CMS/MultivariateElectronIdentification#Recipe_for_5_3_X
cvs co -r V00-00-09 EgammaAnalysis/ElectronTools
cvs co -r V09-00-01 RecoEgamma/EgammaTools
scram b -j 9
cd EgammaAnalysis/ElectronTools/data
cat download.url | xargs wget

cd $CMSSW_BASE/src

#https://twiki.cern.ch/twiki/bin/viewauth/CMS/PileupJetID
cvs co -r V00-03-04 -d CMGTools/External UserCode/CMG/CMGTools/External

#https://twiki.cern.ch/twiki/bin/viewauth/CMS/MissingETOptionalFilters#EB_or_EE_Xtals_with_large_laser
addpkg RecoMET/METFilters V00-00-13-01
addpkg RecoMET/METAnalyzers V00-00-08

#LHAPDF setup must be done prior to full compile
cmsenv
mkdir -p $STPOL_DIR/local/lib
mkdir -p $STPOL_DIR/local/include
scram setup lhapdffull
cmsenv

scram b -j 8 &> scram_log
cd $CMSSW_BASE/../
source setenv.sh

$STPOL_DIR/setup/install_tunfold.sh
$STPOL_DIR/setup/install_theta.sh
$STPOL_DIR/setup/install_exempi.sh
$STPOL_DIR/setup/install_pylibs.sh
